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

echo Waiting for 5 seconds to continue.
@ping localhost -n 5 > NUL

echo.
echo.

REM Start WeMod.exe and get its PID
echo Starting %wemodname%.
start "" %wemodpath%

:wemod
set wemodPID=
for /F "TOKENS=1,2,*" %%a in ('tasklist /FI "IMAGENAME eq %wemodname%"') do set wemodPID=%%b
if not errorlevel 0 (
    goto wemod
)

REM Start the custom command and get its PID
echo Running game %1.
start "" %*

echo.
echo Running loop to check for the game.
echo Minimize this window, don't close it.
echo If you close this window, WeMod won't close with the game.
echo.

REM Couter to check if the game was detected correctly
set /A counter=0

:game
for /F "TOKENS=1,2,*" %%a in ('tasklist /FI "IMAGENAME eq %~n1%~x1" /NH') do set commandPID=%%b
if not errorlevel 0 (
    goto game
)
:loop
set runningPID=
for /F "TOKENS=1,2,*" %%a in ('tasklist /FI "PID eq %commandPID%" /NH') do set runningPID=%%b
if not errorlevel 0 (
    goto loop
)

if defined runningPID (
    @ping localhost -n 1 > NUL
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
    )
    taskkill /PID %wemodPID% /F
    if not errorlevel 0 (
        taskkill /PID %wemodPID% /F
    )
)
echo.
echo Killed %wemodPID%
echo.
echo Done, closing in 5 seconds
@ping localhost -n 5 > NUL
