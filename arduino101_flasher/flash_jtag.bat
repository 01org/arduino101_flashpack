@echo off
bin\openocd.exe -f scripts\interface\ftdi\flyswatter2.cfg -f scripts\board\firestarter.cfg -f scripts\flash-jtag.cfg
if %ERRORLEVEL% NEQ 0 (
  echo.
  echo ***ERROR***
  exit /b 1
) else (
  echo.
  echo !!!SUCCESS!!!
)
PAUSE
