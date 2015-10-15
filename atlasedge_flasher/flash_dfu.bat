@echo off

:: Flash Arduino 101 firmware via USB and dfu-util

setlocal ENABLEDELAYEDEXPANSION

if "%1" NEQ "" (
  set SER_NUM=-S %1
)
set DFU=bin\dfu-util %SER_NUM% -d8087:0ABA
set IMG=images/firmware

cls
if "%SER_NUM%" NEQ "" echo Flashing board S/N: %1
echo Reset the board before proceeding...
REM wait for DFU device
set X=
:loop
  for /f "delims== tokens=8" %%i in ('%DFU% -l 2^>NUL ^|find "sensor"') do (
    set X=%%i
  )
  REM extract the serial number from unknown discovered device
  if "!X!" EQU "" goto:loop
  if "%SER_NUM%" EQU "" (
    set SER_NUM=!X:*serial=!
	set SER_NUM=!SER_NUM:"=!
	echo Using board S/N: !SER_NUM!...
	set DFU=%DFU% -S !SER_NUM!
  ) 

call:flash

if %ERRORLEVEL% NEQ 0 (
  echo.
  echo ***ERROR***
  exit /b 1
)
echo.
echo ---SUCCESS---
pause
exit /b 0

:flash
  %DFU% -a 7 -D %IMG%/bootloader_lakemont.bin
    if !ERRORLEVEL! NEQ 0 exit /b 1
  %DFU% -a 2 -R -D %IMG%/bootupdater.bin
    if !ERRORLEVEL! NEQ 0 exit /b 1
  echo *** Sleeping for 12 seconds...
  call:delay 12
  %DFU% -a 2 -D %IMG%/lakemont.bin
    if !ERRORLEVEL! NEQ 0 exit /b 1
  %DFU% -a 7 -D %IMG%/arc.bin
    if !ERRORLEVEL! NEQ 0 exit /b 1
  %DFU% -a 8 -R -D %IMG%/ble_core/image.bin
    if !ERRORLEVEL! NEQ 0 exit /b 1
goto:eof

REM Ugly Windows equivalent of 'sleep'
:delay
  choice /c:Z /d:Z /t %1 > nul
goto:eof
