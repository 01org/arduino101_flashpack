#!/bin/sh
#
# Script to flash AtlasEdge firmware via USB and dfu-util
#
PID="8087:0ABA"
IMG="images/firmware"
os="$(uname)"

DFU="bin/dfu-util"
if [ x"$os" = x"Darwin" ]; then
  DFU="bin_osx/dfu-util"
fi

flash() {
  $DFU -d$PID -a 3 -D $IMG/bootloader_lakemont.bin
  $DFU -d$PID -a 5 -R -D $IMG/bootupdater.bin
  echo "*** Sleeping for 12 seconds..."
  sleep 12
  $DFU -d$PID -a 2 -D $IMG/lakemont.bin
  $DFU -d$PID -a 7 -D $IMG/arc.bin
  $DFU -d$PID -a 8 -R -D $IMG/ble_core/image.bin
}

wait() {
  x=''
  while [ -z $x ]; do
    x=$($DFU -l |grep sensor)
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

