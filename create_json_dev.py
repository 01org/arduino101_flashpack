#!/usr/bin/python

# Create JSON using package URLs
import glob
import os
import filecmp
import sys
import json
import shutil
import hashlib
import urllib, urllib2

package_name = "Intel-Test"

archs = \
  { "linux64": "x86_64-linux-gnu",
    "linux32": "i686-linux-gnu",
    "osx":     "i386-apple-darwin11",
    "windows": "i686-mingw32"
  }

url = "http://mkfs.ndg.intel.com"
root_dir = "/mnt/share/public"

# lookup architecture code for given OS
def get_host(fname):
  for os in archs:
    if os in fname:
      return os
  return None

# calculate SHA256 hash of a file
def get_hash(fname, hasher, blocksize=65536):
    with open(fname, 'rb') as afile:
        buf = afile.read(blocksize)
        while len(buf) > 0:
            hasher.update(buf)
            buf = afile.read(blocksize)
    return hasher.hexdigest()

def get_systems(files_dict):
    systems = []
    for o, fname in files_dict['files'].iteritems():
        print "Inspecting %s...(%s)" % (fname, os.path.basename(fname))
        system = \
            {
                "url": files_dict['urls'][o],
                "checksum": "SHA-256:%s" % get_hash(fname, hashlib.sha256()),
                "host": archs[get_host(fname)],
                "archiveFileName": os.path.basename(fname),
                "size": os.stat(fname).st_size
            }
        systems.append(system)
    return systems

corelib_file = {}
tools_files = {}
toolchain_files = {}

def read_urls():
    global corelib_file, tools_files, toolchain_files
    tools_files['urls'] = {}
    tools_files['files'] = {}
    toolchain_files['urls'] = {}
    toolchain_files['files'] = {}
    print "-- CORELIBS --"
    corelib_file['file'] = raw_input("Enter corelibs path: ")
    corelib_file['url'] = "%s/%s" % (url, corelib_file['file'])
    corelib_file['file'] = "%s/%s" % (root_dir, corelib_file['file'])
    print "-- ARDUINO-TOOLS --"
    for o in archs:
        tools_files['files'][o] = raw_input("Enter %s arduino-tools path: " % o)
        tools_files['urls'][o] = "%s/%s" % (url, tools_files['files'][o])
        tools_files['files'][o] = "%s/%s" % (root_dir, tools_files['files'][o])
    print "-- ARC-TOOLCHAINS --"
    for o in archs:
        toolchain_files['files'][o] = raw_input("Enter %s arc-toolchains path: " % o)
        toolchain_files['urls'][o] = "%s/%s" % (url, toolchain_files['files'][o])
        toolchain_files['files'][o] = "%s/%s" % (root_dir, toolchain_files['files'][o])
    print "** VERSIONS **"
    corelib_file['version'] = raw_input("Enter corelibs version: ")
    tools_files['version'] = raw_input("Enter arduino-tools version: ")
    toolchain_files['version'] = raw_input("Enter arc-toolchains version: ")


    corelib_file['name'] = "Intel Curie Boards (DEV)"
    tools_files['name'] = "arduino101load"
    toolchain_files['name']  = "arc-elf32"

# list files
read_urls()

# verify package file counts - nothing is missing
if (corelib_file['file']   == '' or
    len(tools_files['files'].keys())     != 4 or
    len(toolchain_files['files'].keys()) != 4):
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

platforms = []
platforms.append(
    {
        "category": "Arduino Certified",
        "name": corelib_file['name'],
        "url": corelib_file['url'],
        "checksum": "SHA-256:%s" % get_hash(corelib_file['file'], hashlib.sha256()),
        "version": corelib_file['version'],
        "toolsDependencies": dependencies,
        "architecture": "arc32",
        "archiveFileName": os.path.basename(corelib_file['file']),
        "size": os.stat(corelib_file['file']).st_size,
        "boards": [
            {
                "name": "Arduino/Genuino 101"
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

