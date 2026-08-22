@echo off
setlocal

set "TOKEN=%~1"

if "%TOKEN%"=="" (
    set /p TOKEN="Please enter your GitHub Personal Access Token: "
)

if "%TOKEN%"=="" (
    echo Error: No token provided.
    pause
    exit /b 1
)

echo Pushing all committed code to https://github.com/imtiaz571/NLP ...
node scripts/push_to_github.js "%TOKEN%"

if %ERRORLEVEL% equ 0 (
    echo.
    echo =======================================================
    echo  SUCCESS! All code has been pushed to GitHub.
    echo  View repo: https://github.com/imtiaz571/NLP
    echo =======================================================
) else (
    echo.
    echo Push failed. Please verify that your token has 'repo' permissions.
)

pause
