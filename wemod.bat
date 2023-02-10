@echo off
@title Wemod Launcher

SET mypath=%~dp0
SET wemodpath=%mypath:~0,-1%\WeMod.exe

echo Hello from WeMod Launcher
echo WEMOD EXE: "%wemodpath%"
echo PWD: "%cd%"
echo command: "%*"
pause
start "" "%wemodpath%"
start "" %*
