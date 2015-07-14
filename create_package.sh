#!/bin/bash -e
share_dir="/mnt/p-sys_maker"
dir="${share_dir}/release"
rdir="${share_dir}/public"
oses="linux64 linux32 windows osx"
os=''
outfile='files.py'
toolchains=
tools=

# Identify target OS from package filename
function get_arch {
  os=''
  for o in $oses; do
    if [[ $1 == *${o}* ]]; then
       os=$o
       break
    fi
  done
}

# Get file list from latest build folders
function get_file_list {
  echo "toolchains = {" > $outfile
  # toolchains
  for toolchain in $(ls -1 ${dir}/arc-toolchains/); do
    get_arch "$toolchain"
    echo "   \"$os\":  \"$toolchain\"," >> $outfile
    toolchains="${toolchains} $toolchain"
  done
  echo "}" >> $outfile
  # tools
  echo "toolfiles = {" >> $outfile
  for tool in $(ls -1 ${dir}/arduino-tools/); do
    get_arch "$tool"
    echo "   \"$os\":  \"$tool\"," >> $outfile
    tools="${tools} $tool"
  done
  echo "}" >> $outfile
  # corelibs
  corelib=$(ls -1 ${dir}/corelibs/)
  echo "corelib = \"$corelib\"" >> $outfile
}

# Copy artifacts from latest build to web share
function copy_files {
  # corelibs
  if [ ! -f $rdir/corelibs/$corelib ]; then
    echo "Copying ${dir}/corelibs/$corelib --> $rdir/corelibs/$corelib"
    cp ${dir}/corelibs/$corelib $rdir/corelibs/$corelib
  else
    cmp ${dir}/corelibs/$corelib $rdir/corelibs/$corelib >/dev/null 2>&1
    if [ $? -ne 0 ]; then echo "**** $rdir/corelibs/$corelib is Different!! ****" && exit 1; fi
    echo "$corelib is up-to-date"
  fi
  # toolchains
  for toolchain in $toolchains; do
    if [ ! -f $rdir/arc-toolchains/$toolchain ]; then
      echo "Copying ${dir}/arc-toolchains/$toolchain --> $rdir/arc-toolchains/$toolchain"
      cp ${dir}/arc-toolchains/$toolchain $rdir/arc-toolchains/$toolchain
    else
      cmp ${dir}/arc-toolchains/$toolchain $rdir/arc-toolchains/$toolchain >/dev/null 2>&1
      if [ $? -ne 0 ]; then echo "****  $rdir/arc-toolchains/$toolchain is Different!! ****" && exit 1; fi
      echo "$toolchain is up-to-date"
    fi
  done
  # tools
  for tool in $tools; do
    if [ ! -f $rdir/arduino-tools/$tool ]; then
      echo "Copying ${dir}/arduino-tools/$tool --> $rdir/arduino-tools/$tool"
      cp ${dir}/arduino-tools/$tool $rdir/arduino-tools/$tool
    else
      cmp ${dir}/arduino-tools/$tool $rdir/arduino-tools/$tool >/dev/null 2>&1
      if [ $? -ne 0 ]; then echo "**** $rdir/arduino-tools/$tool is Different!! ****" && exit 1; fi
      echo "$tool is up-to-date"
    fi
  done
}

get_file_list
copy_files
