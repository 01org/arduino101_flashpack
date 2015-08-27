@echo off
setlocal ENABLEDELAYEDEXPANSION
set DFU=bin\dfu-util.exe
set file=%TMP%\dfuver.txt

set ARGS=%*
if "%1" == "" set ARGS=1 2 3

rem cls
echo.
echo Reset the board to proceed...
set X=
:loop
  for /f "tokens=*" %%i in ('%DFU% -l ^|find "sensor"') do (
    set X="%%i"
  )
  if "!X!" EQU "" goto:loop

set readbin=bin\readbin.exe
for %%i in (%ARGS%) do (
  if exist %file% del %file%
  %DFU% -d8087:0ABA -a %%i -t 1 -U %file% >NUL
  %readbin% %file%
)

%DFU% -e >NUL 2>&1
