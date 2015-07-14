#!/usr/bin/python
import os
import hashlib
import json
from files import *

archs = \
  { "linux64": "x86_64-linux-gnu",
    "linux32": "i686-linux-gnu",
    "osx":     "i386-apple-darwin11",
    "windows": "i686-mingw32"
  }
# web URL and folder
root =         '/mnt/p-sys_maker/public'
urlroot =      'http://mkfs.ndg.intel.com'
# file directories
corelibsdir =  'corelibs'
tooldir =      'arduino-tools'
toolchaindir = 'arc-toolchains'
# JSON template
jsonfile =     'default.json'
def hashfile(afile, hasher, blocksize=65536):
    buf = afile.read(blocksize)
    while len(buf) > 0:
        hasher.update(buf)
        buf = afile.read(blocksize)
    return hasher.hexdigest()

def setsystem(tcfile, host, dirname):
    system = {}
    print '-----',root, dirname, tcfile
    fname = os.path.join(root, dirname, tcfile)
    print fname
    fsize = os.path.getsize(fname)
    sha256 = 'SHA-256:' + hashfile(open(fname, 'rb'), hashlib.sha256())
    url = '/'.join([urlroot, dirname, tcfile])
    system['url'] = url
    system['archiveFileName'] = tcfile
    system['size'] = fsize
    system['checksum'] = sha256
    system['host'] = host
    return system
  
# read default JSON
data = json.load(open(jsonfile))
# list corlib file
fname = os.path.join(root, corelibsdir, corelib)
fsize = os.path.getsize(fname)
sha256 = 'SHA-256:' + hashfile(open(fname, 'rb'), hashlib.sha256())
url = '/'.join([urlroot, corelibsdir, corelib])
data['packages'][0]['platforms'][0]['url'] = url
data['packages'][0]['platforms'][0]['archiveFileName'] = corelib
data['packages'][0]['platforms'][0]['size'] = fsize
data['packages'][0]['platforms'][0]['checksum'] = sha256

# list toolchain files
tools = data['packages'][0]['tools']
systems = []
index = [i for (i, d) in enumerate(tools) if d["name"] == "arc-elf32"][0]
for arch, tcfile in dict.iteritems(toolchains):
    host = archs[arch]
    print tcfile, host, toolchaindir
    systems.append(setsystem(tcfile, host, toolchaindir))
data['packages'][0]['tools'][index]['systems'] = systems

# list sketchuploader files
systems = []
index = [i for (i, d) in enumerate(tools) if d["name"] == "sketchUploader"][0]
for arch, toolfile in dict.iteritems(toolfiles):
    host = archs[arch]
    systems.append(setsystem(toolfile, host, tooldir))
data['packages'][0]['tools'][index]['systems'] = systems

#print json.dumps(data, indent=4, separators=(',', ': '))
with open('package.json', 'w') as outfile:
    json.dump(data, outfile, indent=4, separators=(',', ': '))
