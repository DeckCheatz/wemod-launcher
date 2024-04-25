@echo off
@title Wemod Launcher

SET mypath=%~dp0
SET wemodpath=%mypath:~0,-1%\wemod_bin\WeMod.exe

echo Hello from WeMod Launcher
echo WEMOD EXE: "%wemodpath%"
echo PWD: "%cd%"
echo command: %*
choice /C Y /N /T 30 /D Y /M "Press Y to continue or wait 30 seconds: "
start "" %wemodpath%
start "" %*
