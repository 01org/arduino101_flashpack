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
symlink=../flashpack.zip

# copy .bin and partition.conf files into flasher package
mkdir arduino101_flasher/images/
rsync -avm --include='*.bin' --include='*partition.conf' -f 'hide,! */' $fwdir/ arduino101_flasher/images/firmware/

# create flasher package
rsync -rav arduino101_flasher/ arduino101_flasher_${tag}
zip -r $flasher arduino101_flasher_${tag}/
ln -s $(basename $flasher) $symlink
