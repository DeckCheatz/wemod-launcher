@echo off
@title Wemod Launcher

SET mypath=%~dp0
SET wemodname=WeMod.exe
SET wemodpath=%mypath:~0,-1%\wemod_bin\%wemodname%
SET temptime=%mypath:~0,-1%\.cache\early.tmp
SET returnfile=%mypath:~0,-1%\.cache\return.tmp

echo Hello from the WeMod Launcher, the WeMod bat was started successfully.
echo.
echo WEMOD EXE:
echo "%wemodpath%"
echo.
echo PWD:
echo "%cd%"
echo.
echo command:
echo %*

echo.
echo.

REM Start WeMod.exe and get its PID
echo Starting WeMod by using %wemodname%.
start "" %wemodpath%

echo Cheking for running WeMod pid
set wemodPID=

set retry_count=0
:retry_pid
set wemodPID=
set /a retry_count+=1

REM Get the wemod pid over Proton
for /F "TOKENS=1,2,*" %%a in ('C:/windows/system32/tasklist /FI "IMAGENAME eq %wemodname%" 2>NUL') do (
    set void=%%a
    set wemodPID=%%b
)
REM On fail try once more to get the wemod pid over Proton
if not defined wemodPID (
    for /F "TOKENS=1,2,*" %%a in ('C:/windows/system32/tasklist /FI "IMAGENAME eq %wemodname%"') do (
        set void=%%a
        set wemodPID=%%b
    )
)
REM If still not set get wemod pid over wine
if not defined wemodPID (
    for /F "TOKENS=2 delims=," %%d in ('C:/windows/system32/tasklist /FI "IMAGENAME eq %wemodname%" 2>NUL') do (
        set wemodPID=%%d
    )
)
REM On fail try once more to get wemod pid over wine
if not defined wemodPID (
    for /F "TOKENS=2 delims=," %%d in ('C:/windows/system32/tasklist /FI "IMAGENAME eq %wemodname%"') do (
        set wemodPID=%%d
    )
)

if not defined wemodPID (
    echo Attempting to find WeMod PID (attempt %retry_count% of 3)...
    if %retry_count% leq 3 (
        @ping localhost -n 1 > NUL
        goto :retry_pid
    )
    echo Failed to find WeMod PID after multiple attempts. Continuing anyway.
)

echo WeMod found with pid %wemodPID%
echo.

REM Start the game and wait for exit
echo Running game "%~1" and waiting for close
echo The full command is: %*
start /wait "" %*
echo.
echo The game was closed

if defined wemodPID (
    if exist %temptime% (
        del %temptime%
        echo Game closed to fast, Game detection may have failed. > %returnfile%
        echo Keep in mind the wemod-launcher usualy can`t detect game launchers. >> %returnfile%
        echo THIS IS NOT A BUG, its not possible with the current project structure. >> %returnfile%
        echo Only open a Issue if the game (launcher) did not start, >> %returnfile%
        echo or if the game crashed, or if wemod won't closes unexpectedly. >> %returnfile%
        echo.
        echo Game closed to fast, Game detection may have failed, sending problem to python script and waiting for awnser
        :WaitUser
        @ping localhost -n 1 > NUL 2>&1
        if exist %returnfile% (
            goto WaitUser
        )
    )
    echo Closing WeMod
    C:/windows/system32/taskkill.exe /PID %wemodPID% /F 2>NUL
    C:/windows/system32/taskkill.exe /PID %wemodPID% /F 2>NUL
    echo.
    echo Killed %wemodname% with pid %wemodPID%
)

echo.
echo Done running bat, closing in 1 second
@ping localhost -n 1 > NUL 2>&1
echo.
