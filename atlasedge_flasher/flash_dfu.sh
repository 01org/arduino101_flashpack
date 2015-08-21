#!/bin/sh -x
#
# Script to flash AtlasEdge firmware via USB and dfu-util
#
DFU="sudo bin/dfu-util -d8087:0ABA"
IMG="images/firmware"

flash() {
  $DFU -a 3 -D $IMG/bootloader_lakemont.bin
  $DFU -a 5 -R -D $IMG/bootupdater.bin
  echo "*** Sleeping for 12 seconds..."
  sleep 12
  $DFU -a 2 -D $IMG/lakemont.bin
  $DFU -a 7 -D $IMG/arc.bin
  $DFU -a 8 -R -D $IMG/ble_core/image.bin
}

wait() {
  x=''
  while [ -z $x ]; do
    x=$(sudo bin/dfu-util -l |grep sensor)
    #sleep 1
  done
}

echo "*** Reset the board to begin..."
wait
flash

if [ $? -ne 0 ]; then
  echo
  echo "***ERROR***"
else
  echo
  echo "!!!SUCCESS!!!"
fi

