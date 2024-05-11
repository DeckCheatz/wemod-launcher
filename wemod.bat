@echo off
@title Wemod Launcher

SET mypath=%~dp0
SET wemodpath=%mypath:~0,-1%\wemod_bin\WeMod.exe

echo Hello from WeMod Launcher
echo WEMOD EXE: "%wemodpath%"
echo PWD: "%cd%"
echo command: %*

echo Waiting for 5 seconds to continue
@ping localhost -n 5 > NUL

start "" %wemodpath%
start "" %*
