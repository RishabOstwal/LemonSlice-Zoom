@echo off
rem Usage: dispatch ["<zoom link>"] ["Bot name"]
rem Installs uv with the official installer if it is missing.

where uv >nul 2>&1
if not errorlevel 1 goto run

echo uv is not installed. Installing uv...
powershell -NoProfile -ExecutionPolicy ByPass -Command "irm https://astral.sh/uv/install.ps1 | iex"
if errorlevel 1 goto install_failed

set "PATH=%USERPROFILE%\.local\bin;%PATH%"
where uv >nul 2>&1
if errorlevel 1 goto path_missing

:run
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0dispatch.ps1" %*
exit /b %ERRORLEVEL%

:install_failed
echo Could not install uv. Install it manually: https://docs.astral.sh/uv/getting-started/installation/
exit /b 1

:path_missing
echo uv was installed but is not on PATH yet. Open a new terminal and run dispatch again.
exit /b 1
