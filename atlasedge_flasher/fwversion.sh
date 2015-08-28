#!/bin/bash
#
# Read version strings from DFU memory
#
file='/tmp/dfuver.txt'
readbin='bin/readbin'
DFU='bin/dfu-util'
os=$(uname)
if [ "$os" = "Darwin" ]; then
  DFU='bin_osx/dfu-util'
  readbin='bin_osx/readbin'
fi

ARGS=$*
if [ -z "$*" ] ; then
   ARGS="1 2 3"
fi

# wait for DFU mode
echo ""
echo "Reset the board to proceed..."
X=''
while [ -z "$X" ]; do
  X=$($DFU -l |grep "sensor")
done

# dump DFU partition memory and parse for version
for i in $ARGS;
do
  if [ -f $file ]; then
    rm $file
  fi
  $DFU -d8087:0ABA -a $i -t 1 -U $file >/dev/null
  $readbin $file
done

# detatch from DFU
$DFU -e >/dev/null 2>&1

