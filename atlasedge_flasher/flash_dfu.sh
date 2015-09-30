#!/bin/sh
#
# Script to flash Arduino 101 firmware via USB and dfu-util
#
PID="8087:0ABA"
IMG="images/firmware"
os="$(uname)"

DFU="bin/dfu-util"
if [ x"$os" = x"Darwin" ]; then
  DFU="bin_osx/dfu-util"
  export DYLD_LIBRARY_PATH=bin_osx:$DYLD_LIBRARY_PATH
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
    x=$($DFU -l 2>/dev/null |grep sensor)
    #sleep 1
  done
}

echo "*** Reset the board to begin..."
wait
flash
exit $?

if [ $? -ne 0 ]; then
  echo
  echo "***ERROR***"
else
  echo
  echo "!!!SUCCESS!!!"
fi

