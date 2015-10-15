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
  echo "Flashing DFU device with $ser_num"
  $DFU $ser_num -d$PID -a 7 -D $IMG/bootloader_lakemont.bin
  $DFU $ser_num -d$PID -a 2 -R -D $IMG/bootupdater.bin
  echo "*** Sleeping for 12 seconds..."
  sleep 12
  $DFU $ser_num -d$PID -a 2 -D $IMG/lakemont.bin
  $DFU $ser_num -d$PID -a 7 -D $IMG/arc.bin
  $DFU $ser_num -d$PID -a 8 -R -D $IMG/ble_core/image.bin
}

wait() {
  x=''
  while [ -z "$x" ]; do
    x=$($DFU -l $ser_num 2>/dev/null |grep sensor)
    #sleep 1
  done
  if [ -z $ser_num ]; then
    ser_num=$(echo $x|awk -F= {'print $8'}|sed -e "s/\"//g")
  fi
}

if [ $# -gt 0 ]; then
  ser_num="-S $1"
fi
echo "*** Reset the board to begin..."
wait
echo Flashing board S/N: $ser_num
flash
exit $?

if [ $? -ne 0 ]; then
  echo
  echo "***ERROR***"
else
  echo
  echo "!!!SUCCESS!!!"
fi

