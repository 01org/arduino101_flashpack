#!/bin/bash

if [ "$1" == "-help" ]; then
  echo "./$0 arg1 arg2"
  echo 'arg1:'
  echo ' -help                display this help'
  echo ' -flash               flashing ARC and lakemont'
  echo ' -rom                 flashing rom only'
  echo ' -all                 flashing ARC, lakemont and rom'
  echo ' -debug               connect openocd server to board for debug'
  echo ' -restart             restart lakemont'
  echo ' -factory             flashing provisioning'
  echo ' -test_openocd_sanity openocd integration tests'
  echo 'arg2:'
  echo ' empty               by default ftdi interface APP1.0'
  echo '-fs                  select flyswatter interface'
  exit 0
fi

if [ -z "$2" ];
then
    msg="interface: ftdi"
    cmd0='atpdev'
elif [ $2 == "fs" ];
then
    msg="$msg interface:flyswatter "
    cmd0='flyswatter2'
else
    msg="bad interface"
fi


cmd1='atp_soc_connect.cfg'
cmd3='atp_soc_run.cfg'


if [ $1 == "-flash" ];
then
    cmd2='atp_soc_flash.cfg'
elif [ $1 == "-rom" ];
then
    cmd2='atp_soc_rom.cfg'
elif [ $1 == "-factory" ];
then
    cmd2='atp_soc_factory.cfg'
    dd if=/dev/urandom of=../../../out/current/firmware/intel_otp.bin bs=512 count=1
    dd if=/dev/urandom of=../../../out/current/firmware/customer_otp.bin bs=512 count=1
    dd if=/dev/urandom of=../../../out/current/firmware/customer_nvim.bin bs=512 count=1
elif [ $1 == "-all" ];
then
    cmd2='atp_soc_flash.cfg'
    cmd2_bis='atp_soc_rom.cfg'
elif [ $1 == "-debug" ];
then
    echo debug mode
elif [ $1 == "-restart" ];
then
    echo restart target

elif [ $1 == "-test_openocd_sanity" ];
then
     dd if=/dev/urandom of=../../../out/current/firmware/block_bin.bin bs=196608 count=1
     dd if=/dev/urandom of=../../../out/current/firmware/align_bin.bin bs=8192 count=1
     dd if=/dev/urandom of=../../../out/current/firmware/align_bin.bin bs=8192 count=1
     dd if=/dev/zero bs=196608 count=1 | tr "\000" "\377" > ../../../out/current/firmware/erase_bin.bin
     cmd2='atp_soc_openocd_sanity.cfg'
else
    echo $1: bad argument
    exit 1
fi

    echo "$msg"
    if [ $1 == "-debug" ];
    then
        ../bin/./openocd -c "source [find interface/ftdi/"$cmd0".cfg]" -f "$cmd1"
    elif [ $1 == "-restart" ];
    then
        ../bin/./openocd -c "source [find interface/ftdi/"$cmd0".cfg]" -f "$cmd1" -f "$cmd3"
    elif [ -z "$cmd2_bis" ];
    then
       ../bin/./openocd -c "source [find interface/ftdi/"$cmd0".cfg]" -f "$cmd1" -f "$cmd2" -f "$cmd3"

    elif [ $cmd2_bis == "atp_soc_rom.cfg" ];
    then
        ../bin/./openocd -c "source [find interface/ftdi/"$cmd0".cfg]" -f "$cmd1" -f "$cmd2" -f "$cmd2_bis" -f "$cmd3"
    fi

function compare {
    for RESULT in "${DIFF[@]:$1:$2}"; do
	if echo $RESULT | egrep -q identical;then
          TEST_DUMP=true
        else
          TEST_DUMP=false
	  break
        fi
    done

   if $TEST_DUMP ;then
      echo "-----------------------------------"
      echo "Info Sanity: Test "$3" passed"
   else
      echo "-----------------------------------"
      echo "Info Sanity: Test "$3" failed"
   fi
}

if [ $cmd2 == "atp_soc_openocd_sanity.cfg" ];
then

DIFF[0]=$(diff -s ../../../out/current/firmware/Dump_Flash1.bin ../../../out/current/firmware/block_bin.bin)
DIFF[1]=$(diff -s ../../../out/current/firmware/Dump_Flash0.bin ../../../out/current/firmware/block_bin.bin)
DIFF[2]=$(diff -s ../../../out/current/firmware/Dump_Rom.bin ../../../out/current/firmware/FSRom.bin)

DIFF[3]=$(diff -s ../../../out/current/firmware/Erase_Flash0.bin ../../../out/current/firmware/erase_bin.bin)
DIFF[4]=$(diff -s ../../../out/current/firmware/Erase_Flash1.bin ../../../out/current/firmware/erase_bin.bin)

DIFF[5]=$(diff -s ../../../out/current/firmware/Mass_erase_Flash0.bin ../../../out/current/firmware/erase_bin.bin)
DIFF[6]=$(diff -s ../../../out/current/firmware/Mass_erase_Flash1.bin ../../../out/current/firmware/erase_bin.bin)

compare 0 3 "integrity"
compare 3 2 "single erase"
compare 5 2 "Mass erase"

fi

exit 0
