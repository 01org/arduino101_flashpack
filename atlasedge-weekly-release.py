#!/usr/bin/python

""" INTEL CONFIDENTIAL Copyright 2015 Intel Corporation All Rights Reserved.
  *
  * The source code contained or described herein and all documents related to
  * the source code ("Material") are owned by Intel Corporation or its suppliers
  * or licensors.
  * Title to the Material remains with Intel Corporation or its suppliers and
  * licensors.
  * The Material contains trade secrets and proprietary and confidential information
  * of Intel or its suppliers and licensors. The Material is protected by worldwide
  * copyright and trade secret laws and treaty provisions.
  * No part of the Material may be used, copied, reproduced, modified, published,
  * uploaded, posted, transmitted, distributed, or disclosed in any way without
  * Intel's prior express written permission.
  *
  * No license under any patent, copyright, trade secret or other intellectual
  * property right is granted to or conferred upon you by disclosure or delivery
  * of the Materials, either expressly, by implication, inducement, estoppel or
  * otherwise.
  *
  * Any license under such intellectual property rights must be express and
  * approved by Intel in writing
  
  Original Author: Calvin Sangbin Park <calvin.s.park@intel.com>
"""

from tempfile import mkstemp
from shutil import move
from os import remove, close
from argparse import RawTextHelpFormatter
import sys, subprocess, commands, argparse, datetime, os, re, shutil

def main():
    """
    Tag the latest commit of all repo projects and submodules,
    modify the manifest to point to the latest tag,
    then push all the tags.
    """
    defaultTag = "ATLASEDGE/WEEKLY/WW{workweek}".format(workweek=datetime.date.today().isocalendar()[1])

    parser = argparse.ArgumentParser(description='Create a weekly release for AtlasEdge.', formatter_class=RawTextHelpFormatter)
    parser.add_argument('aedir', help="Top directory location of AtlasEdge")
    parser.add_argument('-t', '--tag', metavar="customTag", default=defaultTag, help="Tag all directories and push the tag.\nDefault: {default}".format(default=defaultTag))
    parser.add_argument('-e', '--execute', action="store_true", help="Unless this option is used, everything is a dry run.")
    parser.add_argument('-v', '--verbose', action="store_true", help="Verbose")
    args = parser.parse_args()
    
    # Go into the source directory
    os.chdir(args.aedir)
    # Get all the paths to repo
    repo_paths = subprocess.check_output("repo forall -c 'echo $REPO_PATH'", stderr=subprocess.STDOUT, shell=True).splitlines()

    ####
    tag_all_except_manifest(repo_paths, args.tag, args.execute, args.verbose)

    MANIFEST_REPO_DIR = "manifest"
    modify_manifest_then_tag_and_push(MANIFEST_REPO_DIR, args.tag, args.execute, args.verbose)

    push_tags(repo_paths, args.tag, args.execute, args.verbose)
    
    gather_artifacts(args.aedir, args.tag, args.execute, args.verbose)
    ####


def tag_all_except_manifest(repo_paths, tag, execute, verbose):
    """
    Tag all repos in repo_paths except for the manifest repo

    :param repo_paths:  Array of relative paths to repo projects and submodules
    :param tag:         Tag for this weekly release
    :param execute:     Confirmation flag to actually perform the task
    :param verbose:     Verbose mode. Not yet implemented.
    """
    print "\nTagging the repo heads as: %s" % (tag)

    for repo_path in repo_paths:
        # Skip the manifest since it has a different tagging structure
        if repo_path == "manifest":
            continue

        # For non-manifest repo, put a tag on it
        if execute:
            try:
                subprocess.check_call("git tag %s"%(tag), cwd=repo_path, shell=True)
                print "[Success] %s" % (repo_path)
            except:
                # Failure is ignored for now in order to further diagnose the failure patterns
                print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
                print "[FAILURE] %s" % (repo_path)
                print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
        else:
            print "[Dry-run] %s" % (repo_path)



def modify_manifest_then_tag_and_push(repo_path, tag, execute, verbose):
    """
    Modify the manifest files to point to the current tag. Then, apply the tag onto the new manifest.

    :param repo_path:   Paths to manifest repo
    :param tag:         Tag for this weekly release
    :param execute:     Confirmation flag to actually perform the task
    :param verbose:     Verbose mode. Not yet implemented.
    """
    print "\nModifying the manifest to point to the tag"
    if not execute:
        print "[Dry-run] %s" % repo_path
        return

    # Modify the manifest file to point to the current tag.
    # Replace |revision="master"|revision="refs/tags/TAG"|
    REVISION_PATTERN = 'revision="[a-zA-Z0-9_/-]+"'
    replace(          "%s/default.xml"%repo_path, REVISION_PATTERN, 'revision="refs/tags/%s"'%tag)
    replace("%s/include/atlaspeak.xml"%repo_path, REVISION_PATTERN, 'revision="refs/tags/%s"'%tag)
    
    # Make a new branch where a tag can live
    BRANCH_NAME = "dev/%s" % tag.lower()
    subprocess.check_call('git checkout -b %s' % BRANCH_NAME, cwd=repo_path, shell=True)
    
    # Make a new commit and put a tag on it
    subprocess.check_call('git commit -sam "Release %s"' % tag, cwd=repo_path, shell=True)
    subprocess.check_call('git tag %s' % tag, cwd=repo_path, shell=True)
    
    # Push the branch so that the tag can be properly pushed
    subprocess.check_call('git push ach %s' % BRANCH_NAME, cwd=repo_path, shell=True)



def push_tags(repo_paths, tag, execute, verbose):
    """
    Push the tag from all repos in repo_paths

    :param repo_paths:  Array of relative paths to repo projects and submodules
    :param tag:         Tag for this weekly release
    :param execute:     Confirmation flag to actually perform the task
    :param verbose:     Verbose mode. Not yet implemented.
    """
    print "\nPushing the tags"

    for repo_path in repo_paths:
        remote = "ach"
        reference = "refs/tags/%s" % (tag)

        # Push all the tags
        if execute:
            try:
                subprocess.check_call("git push %s %s"%(remote, reference), cwd=repo_path, shell=True)
                print "[Success] %s" % (repo_path)
            except:
                # Failure is ignored for now in order to further diagnose the failure patterns
                print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
                print "[FAILURE] %s" % (repo_path)
                print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
        else:
            print "[Dry-run] %s" % (repo_path)



def gather_artifacts(aedir, tag, execute, verbose):
    """
    Gather artifacts into a directory named as the tag

    :param aedir:       Directory where the AtlasEdge was built
    :param tag:         Tag for this weekly release
    :param execute:     Confirmation flag to actually perform the task
    :param verbose:     Verbose mode. Not yet implemented.
    """
    print "\nGathering the artifacts"
    if not execute:
        print "[Dry-run] Not actually gathering since -e option wasn't used."
        return
    
    shutil.copytree("../%s/out/current/firmware" % aedir, "../artifacts/%s" % tag)



def replace(filename, pattern, subst):
    """
    In a given file, find & replace all.

    :param filename:    Filename to be searched and replaced. Relative from the current directory.
    :param pattern:     Pattern to search in regular expression.
    :param subst:       Pattern to replace in regular expression.
    """
    #Create temp file
    fh, abs_path = mkstemp()
    new_file = open(abs_path,'w')
    old_file = open(filename)
    for line in old_file:
        new_file.write(re.sub(pattern, subst, line))
    #close temp file
    new_file.close()
    close(fh)
    old_file.close()
    #Remove original file
    remove(filename)
    #Move new file
    move(abs_path, filename)


if __name__ == "__main__":
    # execute only if run as a script
    main()
