@echo off
@title Wemod Launcher

SET mypath=%~dp0
SET wemodname=WeMod.exe
SET wemodpath=%mypath:~0,-1%\wemod_bin\%wemodname%
SET temptime=%mypath:~0,-1%\.cache\early.tmp
SET returnfile=%mypath:~0,-1%\.cache\return.tmp

echo Hello from WeMod Launcher.
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
echo Starting %wemodname%.
start "" %wemodpath%

set wemodPID=
REM Get the wemod pid over proton
for /F "TOKENS=1,2,*" %%a in ('C:/windows/system32/tasklist /FI "IMAGENAME eq %wemodname%" 2>NUL') do (
    set void=%%a
    set wemodPID=%%b
)
REM On fail try once more to get the wemod pid over proton
if not defined wemodPID (
    for /F "TOKENS=1,2,*" %%a in ('C:/windows/system32/tasklist /FI "IMAGENAME eq %wemodname%" 2>NUL') do (
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
    for /F "TOKENS=2 delims=," %%d in ('C:/windows/system32/tasklist /FI "IMAGENAME eq %wemodname%" 2>NUL') do (
        set wemodPID=%%d
    )
)

echo WeMod found with pid %wemodPID%
echo.

REM Start the game and wait for exit
echo Running game "%~1" and waiting for close
echo The full command is: %*
start /wait "" %*

if defined wemodPID (
    if exist %temptime% (
        del %temptime%
        echo Game closed to fast, Game detection may have failed > %returnfile%
        echo.
        echo Game closed to fast, Game detection may have failed, sending problem to python script and waiting for awnser
        :WaitUser
        @ping localhost -n 1 > NUL 2>&1
        if exist %returnfile% (
            goto WaitUser
        )
    )
    C:/windows/system32/taskkill.exe /PID %wemodPID% /F 2>NUL
    C:/windows/system32/taskkill.exe /PID %wemodPID% /F 2>NUL
)
echo.
echo Killed %wemodname% over pid %wemodPID%
echo.
echo Done, closing in 1 second
@ping localhost -n 1 > NUL 2>&1
