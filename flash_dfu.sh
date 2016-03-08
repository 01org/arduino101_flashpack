#!/bin/sh
#
# Script to flash Arduino 101 firmware via USB and dfu-util
#
PID="8087:0ABA"
IMG="images/firmware"
os="$(uname)"

if [ $# -gt 0 ]; then
  ser_num="-S $1"
fi

DIR="$( dirname `readlink -f $0`)"
cd "$DIR"

BIN="bin/dfu-util"
if [ x"$os" = x"Darwin" ]; then
  BIN="bin_osx/dfu-util"
  export DYLD_LIBRARY_PATH=bin_osx:$DYLD_LIBRARY_PATH
fi
DFU="$BIN $ser_num -d,$PID"

flash() {
  $DFU -a 7 -D $IMG/bootloader_quark.bin
  $DFU -a 2 -R -D $IMG/bootupdater.bin
  echo "*** Sleeping for 12 seconds..."
  sleep 12
  $DFU -a 2 -D $IMG/quark.bin
  $DFU -a 7 -D $IMG/arc.bin -R
}

trap_to_dfu() {
  # If trapped.bin already exists, clean up before starting the loop
  [ -f "trapped.bin" ] && rm -f "trapped.bin"

  # Loop to read from 101 so that it stays on DFU mode afterwards
  until $DFU -a 4 -U trapped.bin > /dev/null 2>&1
  do
    sleep 0.1
  done

  # Clean up
  [ -f "trapped.bin" ] && rm -f "trapped.bin"

  # If a serial number is not specified by the user, read it from the board
  if [ -z "$ser_num" ]; then
    x=$($DFU -l 2>/dev/null |grep sensor|head -1)
    ser_num="-S $(echo $x|awk -F= {'print $8'}|sed -e 's/\"//g')"
    DFU="$BIN $ser_num -d,$PID"
  fi
}

echo "*** Reset the board to begin..."
trap_to_dfu
echo Flashing board S/N: $ser_num
flash

if [ $? -ne 0 ]; then
  echo
  echo "***ERROR***"
  exit 1
else
  echo
  echo "!!!SUCCESS!!!"
  exit 0
fi

