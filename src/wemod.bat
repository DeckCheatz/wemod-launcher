@echo off
@title Wand Launcher

SET mypath=%~dp0
SET wandname=Wand.exe

IF "%mypath:~-5%" == "\src\" (
    SET wandpath=%mypath:~0,-5%\wand_data\wand_bin\%wandname%
) ELSE (
    SET wandpath=%mypath:~0,-1%\wand_data\wand_bin\%wandname%
)

SET temptime=%mypath:~0,-1%\.cache\early.tmp
SET returnfile=%mypath:~0,-1%\.cache\return.tmp

echo Hello from the Wand Launcher, the Wand bat was started successfully.
echo.
echo Wand EXE path:
echo %wandpath%
echo.
echo CWD:
echo %cd%
echo.
echo Command:
echo %*

echo.
echo.

REM Start Wand.exe and get its PID
echo Starting Wand by using %wandname%.
start "" %wandpath%

set wandPID=

REM Get the Wand launcher PID, loop until found, and exit subroutine when found.
set wandPIDCounter=0

:search
echo Searching for Wand PID...
REM Check we haven't run this more than 3 times.
if %wandPIDCounter% GTR 3 (
	echo Wand not found in process list, defaulting to prevent infinite loop... > %returnfile%
    type %returnfile%
	pause
    goto :discovered
)
for /F "TOKENS=1,2 delims=," %%a in ('C:/windows/system32/tasklist /FO CSV /NH /FI "IMAGENAME eq %wandname%"') do (
  set wandPID=%%b
)
if defined wandPID goto :discovered
echo Continue search for Wand PID...
set /A wandPIDCounter+=1
@ping localhost -n 6 >NUL
goto :search

:discovered

echo Wand found with pid %wandPID%
echo.

REM start the game and wait for exit
echo Running game "%~1" and waiting for closure..
echo The full command is: %*
start /wait "" %*
echo.
echo The game was closed.

if defined wandPID (
    if exist %temptime% (
        del %temptime%
        echo Game closed too fast, Game detection may have failed. > %returnfile%
        echo Keep in mind that wand-launcher usually can`t detect game launchers. >> %returnfile%
        echo Only open an issue IF the game did not start, >> %returnfile%
        echo or IF the game crashed, or IF Wand exits unexpectedly. >> %returnfile%
        type %returnfile%
        :WaitUser
        @ping localhost -n 2 >NUL
        if exist %returnfile% GOTO WaitUser
    )
    echo Closing Wand..
    C:/windows/system32/taskkill.exe /PID %wandPID% /F >NUL
    C:/windows/system32/taskkill.exe /PID %wandPID% /F >NUL
    echo Killed %wandname% with pid %wandPID%
)

echo.
echo Done running bat, closing in 1 second
@ping localhost -n 2 >NUL
echo.
