#!/bin/bash
topdir=$(dirname `readlink -e $0`)
cd $topdir
if [ $# -lt 2 ]; then
  echo "Usage: $0 build_directory tag"
  exit 1
fi
# verify build directory exists
dir=$(readlink -e ../$1)
fwdir=$dir/out/current/firmware
if [ ! -d $fwdir ]; then
  echo "$fwdir does not exist."
  exit 1
fi
# create readable tag for flasher package
tag=$(echo $2 |sed -e "s/\//-/g" -)
echo $tag
flasher=../flash-${tag}.zip

# copy artifacts into flasher package
cp -r $fwdir atlasedge_flasher/images/
# create flasher package
zip -r $flasher atlasedge_flasher/

