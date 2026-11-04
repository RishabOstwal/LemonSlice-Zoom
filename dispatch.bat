@echo off
rem Usage: dispatch ["<zoom link>"] ["Bot name"]
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0dispatch.ps1" %*
exit /b %ERRORLEVEL%
