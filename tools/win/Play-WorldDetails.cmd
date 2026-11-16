@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Play-WorldStory.ps1" -Details -UseF4SE %*
pause
