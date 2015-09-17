#!/usr/bin/python
import glob
import os
import filecmp
import sys
import json
import shutil
import hashlib

share = '/mnt/p-sys_maker/release'
pub_dir = '/mnt/p-sys_maker/public'
base_url = "http://mkfs.ndg.intel.com"
package_name = "Intel-Test"

archs = \
  { "linux64": "x86_64-linux-gnu",
    "linux32": "i686-linux-gnu",
    "osx":     "i386-apple-darwin11",
    "windows": "i686-mingw32"
  }

# lookup architecture code for given OS
def get_host(fname):
  for os in archs:
    if os in fname:
      return os
  return None

# Evaluate latest package files
def load_files(subdir, name):
  p = {}
  p['subdir'] = subdir
  p['name']   = name
  tmpdir = os.path.join(share,subdir)
  print "listing %s..." % tmpdir
  p['files'] = glob.glob("%s/*.bz2" % tmpdir)
  p['files'].extend(glob.glob("%s/*.zip" % tmpdir))
  for fpath in p['files']:
    fname = os.path.basename(fpath)
    dest_file = os.path.join(pub_dir, subdir, fname)
    print fpath, dest_file
    if os.path.isfile(dest_file):
      if (filecmp.cmp(fpath, dest_file)):
        print '%s is up-to-date.' % dest_file
      else:
        print '%s is out of sync!' % dest_file
        sys.exit(1)
  with open (os.path.join(share, subdir, 'VERSION'), "r") as myfile:
    p['version'] = myfile.readline().rstrip('\n')
  return p

# calculate SHA256 hash of a file
def hashfile(afile, hasher, blocksize=65536):
  buf = afile.read(blocksize)
  while len(buf) > 0:
      hasher.update(buf)
      buf = afile.read(blocksize)
  return hasher.hexdigest()

# publish files
def promote_files(subdir, files):
  for fpath in files:
    fname = os.path.basename(fpath)
    dest_file = os.path.join(pub_dir, subdir, fname)
    if not os.path.isfile(dest_file):
      print 'Promoting %s to %s' % (fname, dest_file)
      shutil.copy(fpath, dest_file)


def get_systems(files_dict):
    systems = []
    for f in files_dict['files']:
        fname = os.path.basename(f)
        system = \
            {
                "url": "%s/%s/%s" % (base_url, files_dict['subdir'], fname),
                "checksum": "SHA-256:%s" % hashfile(open(f, 'rb'), hashlib.sha256()),
                "host": archs[get_host(f)],
                "archiveFileName": fname,
                "size": os.stat(f).st_size
            }
        systems.append(system)
    return systems

# list files
corelib_files    = load_files("corelibs", "Intel Curie Boards")
tools_files      = load_files("arduino-tools", "sketchUploader")
toolchain_files  = load_files("arc-toolchains", "arc-elf32")
# verify package file counts - nothing is missing
if (len(corelib_files['files'])   != 1 or
    len(tools_files['files'])     != 4 or
    len(toolchain_files['files']) != 4):
    print "ERROR: Incorrect number of packages."
    sys.exit(1)

# form systems section of JSON
tools_systems = get_systems(tools_files)
toolchain_systems = get_systems(toolchain_files)

tools = []
tools.append(
    {
        "version": toolchain_files['version'],
        "name": toolchain_files['name'],
        "systems": toolchain_systems
    })
tools.append(
    {
        "version": tools_files['version'],
        "name": tools_files['name'],
        "systems": tools_systems
    })

dependencies = [
    {
        "packager": package_name,
        "version": toolchain_files['version'],
        "name": toolchain_files['name']
    },
    {
        "packager": package_name,
        "version": tools_files['version'],
        "name": tools_files['name']
    }]

corefile = os.path.basename(corelib_files['files'][0])
platforms = []
platforms.append(
    {
        "category": "Arduino Certified",
        "name": corelib_files['name'],
        "url": "%s/%s/%s" % (base_url, corelib_files['subdir'], corefile),
        "checksum": "SHA-256:%s" % hashfile(open(corelib_files['files'][0], 'rb'), hashlib.sha256()),
        "version": corelib_files['version'],
        "toolsDependencies": dependencies,
        "architecture": "arc32",
        "archiveFileName": corefile,
        "size": os.stat(corelib_files['files'][0]).st_size,
        "boards": [
            {
                "name": "EDU"
            }
        ]
    })
packages = \
    {
        "maintainer": "Intel",
        "name": package_name,
        "websiteURL": "http://www.intel.com/",
        "email": "support@intel.com",
        "platforms": platforms,
        "tools": tools
    }
data = {"packages": packages}
with open('package.json', 'w') as outfile:
    json.dump(data, outfile, indent=4, separators=(',', ': '))

