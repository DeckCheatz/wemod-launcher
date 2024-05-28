@echo off
@title Wemod Launcher

SET mypath=%~dp0
SET wemodname=WeMod.exe
SET wemodpath=%mypath:~0,-1%\wemod_bin\%wemodname%

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

:wemod
set wemodPID=
for /F "TOKENS=1,2,*" %%a in ('C:/windows/system32/tasklist /FI "IMAGENAME eq %wemodname%" 2>NUL') do set wemodPID=%%b
if not errorlevel 0 (
    goto wemod
)
if not defined wemodPID (
    for /F "TOKENS=1,2,*" %%a in ('C:/windows/system32/tasklist /FI "IMAGENAME eq %wemodname%" 2>NUL') do set wemodPID=%%b
)

REM Start the custom command and get its PID

echo Running game "%~1" with args: %args%
start "" %*

echo.
echo Running loop to check for the game.
echo Minimize this window, don't close it.
echo If you close this window, WeMod won't close with the game.
echo.

REM Couter to check if the game was detected correctly
set /A counter=0

:game
for /F "TOKENS=1,2,*" %%a in ('C:/windows/system32/tasklist.exe /FI "IMAGENAME eq %~n1%~x1" /NH 2>NUL') do set commandPID=%%b
if not errorlevel 0 (
    goto game
)
if not defined commandPID (
    for /F "TOKENS=1,2,*" %%a in ('C:/windows/system32/tasklist.exe /FI "IMAGENAME eq %~n1%~x1" /NH 2>NUL') do set commandPID=%%b
)
:loop
set runningPID=
for /F "TOKENS=1,2,*" %%a in ('C:/windows/system32/tasklist.exe /FI "PID eq %commandPID%" /NH') do set runningPID=%%b
if not errorlevel 0 (
    goto loop
)
if not defined runningPID (
    for /F "TOKENS=1,2,*" %%a in ('C:/windows/system32/tasklist.exe /FI "PID eq %commandPID%" /NH') do set runningPID=%%b
    if not errorlevel 0 (
        goto loop
    )
)
if not defined runningPID (
    for /F "TOKENS=1,2,*" %%a in ('C:/windows/system32/tasklist.exe /FI "PID eq %commandPID%" /NH') do set runningPID=%%b
    if not errorlevel 0 (
        goto loop
    )
)

if defined runningPID (
    @ping localhost -n 1 > NUL 2>&1
    if %counter% LSS 50 (
        set /A counter=%counter%+1
    )
    goto loop
)


if defined wemodPID (
    if %counter% LSS 50 (
        echo.
        echo Game was probably not detected correctly, press a key to exit WeMod
        pause
        echo.
    )
    C:/windows/system32/taskkill.exe /PID %wemodPID% /F 2>NUL
    C:/windows/system32/taskkill.exe /PID %wemodPID% /F 2>NUL
)
echo.
echo Killed %wemodname% over pid %wemodPID%
echo.
echo Done, closing in 1 second
@ping localhost -n 1 > NUL 2>&1
