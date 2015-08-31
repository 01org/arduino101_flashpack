@echo off

:: Flash AtlasEdge firmware via USB and dfu-util

setlocal ENABLEDELAYEDEXPANSION
set DFU=bin\dfu-util -d8087:0ABA
set IMG=images/firmware

cls
echo Reset the board before proceeding...
REM wait for DFU device
set X=
:loop
  for /f "tokens=*" %%i in ('%DFU% -l ^|find "sensor"') do (
    set X="%%i"
  )
  if "!X!" EQU "" goto:loop

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
  %DFU% -a 3 -D %IMG%/bootloader_lakemont.bin
    if !ERRORLEVEL! NEQ 0 exit /b 1
  %DFU% -a 5 -R -D %IMG%/bootupdater.bin
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

