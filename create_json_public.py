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

# lookup architecture code for given OS
def get_host(fname):
  for os in archs:
    if os in fname:
      return os
  return None

# calculate SHA256 hash of a file
def hashfile(afile, hasher, blocksize=65536):
  buf = afile.read(blocksize)
  while len(buf) > 0:
      hasher.update(buf)
      buf = afile.read(blocksize)
  return hasher.hexdigest()

def get_systems(files_dict):
    systems = []
    for o, fname in files_dict['files'].iteritems():
        system = \
            {
                "url": files_dict['urls'][o],
                "checksum": "SHA-256:%s" % hashfile(open(fname, 'rb'), hashlib.sha256()),
                "host": archs[get_host(fname)],
                "archiveFileName": fname,
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
    toolchain_files['urls'] = {}
    print "-- CORELIBS --"
    corelib_file['url'] = raw_input("Enter corelibs URL: ")
    print "-- ARDUINO-TOOLS --"
    for o in archs:
        tools_files['urls'][o] = raw_input("Enter %s arduino-tools URL: " % o)
    print "-- ARC-TOOLCHAINS --"
    for o in archs:
        toolchain_files['urls'][o] = raw_input("Enter %s arc-toolchains URL: " % o)
    print "** VERSIONS **"

proxy = urllib2.ProxyHandler({'http':  'http://proxy-chain.intel.com:911',
                              'https': 'http://proxy-chain.intel.com:912'})
opener = urllib2.build_opener(proxy)
urllib2.install_opener(opener)

def dl_file(url):
    url_file = os.path.basename(url)
    print "D/Ling %s..." % (url)
    data = urllib2.urlopen(url)
    output = open(url_file,'wb')
    output.write(data.read())
    output.close()

def dl_files():
    global corelib_file, tools_files, toolchain_files
    tools_files['files'] = {}
    toolchain_files['files'] = {}

    #corelib_files
    corelib_file['file'] = os.path.basename(corelib_file['url'])
    dl_file(corelib_file['url'])
    for o in archs:
        dl_file(tools_files['urls'][o])
        tools_files['files'][o] = os.path.basename(tools_files['urls'][o])
    for o in archs:
        dl_file(toolchain_files['urls'][o])
        toolchain_files['files'][o] = os.path.basename(toolchain_files['urls'][o])

    corelib_file['version'] = raw_input("Enter corelibs version: ")
    tools_files['version'] = raw_input("Enter arduino-tools version: ")
    toolchain_files['version'] = raw_input("Enter arc-toolchains version: ")

    corelib_file['name'] = "Intel Curie Boards (Test)"
    tools_files['name'] = "sketchUploader"
    toolchain_files['name']  = "arc-elf32"

# list files
read_urls()
dl_files()

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
        "checksum": "SHA-256:%s" % hashfile(open(corelib_file['file'], 'rb'), hashlib.sha256()),
        "version": corelib_file['version'],
        "toolsDependencies": dependencies,
        "architecture": "arc32",
        "archiveFileName": corelib_file['file'],
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

