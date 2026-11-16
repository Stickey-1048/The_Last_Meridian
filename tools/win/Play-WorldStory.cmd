@echo off
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0Play-WorldStory.ps1" -UseF4SE %*
set TLM_STORY_EXIT=%ERRORLEVEL%
pause
exit /b %TLM_STORY_EXIT%
