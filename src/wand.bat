@echo off
@title Wand Launcher

SET mypath=%~dp0
SET wandname=Wand.exe
SET wandpath=%mypath:~0,-1%\wand_bin\%wandname%
SET temptime=%mypath:~0,-1%\.cache\early.tmp
SET returnfile=%mypath:~0,-1%\.cache\return.tmp

echo Hello from the Wand Launcher, the Wand bat was started successfully.
echo.
echo WAND EXE:
echo "%wandpath%"
echo.
echo PWD:
echo "%cd%"
echo.
echo command:
echo %*

echo.
echo.

REM Start Wand.exe and get its PID
echo Starting Wand by using %wandname%.
start "" %wandpath%

echo Checking for running Wand pid
set retry_count=0
:retry_pid
set wandPID=
set /a retry_count+=1

REM Get the wand pid over Proton
if not defined wandPID (
    for /F "TOKENS=1,2,*" %%a in ('C:/windows/system32/tasklist /FI "IMAGENAME eq %wandname%"') do (
        set void=%%a
        set wandPID=%%b
    )
)
REM Retry to get the wand pid over Proton
if not defined wandPID (
    for /F "TOKENS=1,2,*" %%a in ('C:/windows/system32/tasklist /FI "IMAGENAME eq %wandname%"') do (
        set void=%%a
        set wandPID=%%b
    )
)
REM If still not set get wand pid over wine
if not defined wandPID (
    for /F "TOKENS=2 delims=," %%d in ('C:/windows/system32/tasklist /FI "IMAGENAME eq %wandname%"') do (
        set wandPID=%%d
    )
)
REM And If still not set retry getting the wand pid over wine
if not defined wandPID (
    for /F "TOKENS=2 delims=," %%d in ('C:/windows/system32/tasklist /FI "IMAGENAME eq %wandname%"') do (
        set wandPID=%%d
    )
)

if not defined wandPID (
    echo Attempting to find Wand PID (attempt %retry_count% of 3)...
    if %retry_count% leq 3 (
        @ping localhost -n 1 > NUL 2>&1
        goto retry_pid
    )
    echo Failed to find Wand PID after multiple attempts. Continuing anyway.
)

echo Wand found with pid %wandPID%
echo.

echo Wand found with pid %wandPID%
echo.

REM Start the game and wait for exit
echo Running game "%~1" and waiting for close
echo The full command is: %*
start /wait "" %*
echo.
echo The game was closed

if defined wandPID (
    if exist %temptime% (
        del %temptime%
        echo Game closed to fast, Game detection may have failed. > %returnfile%
        echo Keep in mind the wand-launcher usualy can`t detect game launchers. >> %returnfile%
        echo THIS IS NOT A BUG, its not possible with the current project structure. >> %returnfile%
        echo Only open a Issue if the game (launcher) did not start, >> %returnfile%
        echo or if the game crashed, or if wand won't closes unexpectedly. >> %returnfile%
        echo.
        echo Game closed to fast, Game detection may have failed, sending problem to python script and waiting for awnser
        :WaitUser
        @ping localhost -n 1 > NUL 2>&1
        if exist %returnfile% (
            goto WaitUser
        )
    )
    echo Closing Wand
    C:/windows/system32/taskkill.exe /PID %wandPID% /F 2>NUL
    C:/windows/system32/taskkill.exe /PID %wandPID% /F 2>NUL
    echo.
    echo Killed %wandname% with pid %wandPID%
)

echo.
echo Done running bat, closing in 1 second
@ping localhost -n 1 > NUL 2>&1
echo.
