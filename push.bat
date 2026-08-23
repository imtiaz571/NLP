@echo off
setlocal enabledelayedexpansion

echo =======================================================
echo   NLP Project - Push to GitHub
echo   Repository: https://github.com/imtiaz571/NLP
echo =======================================================
echo.

set "GIT_CMD=git"
where git >nul 2>nul
if %ERRORLEVEL% neq 0 (
    if exist "C:\Program Files\Git\cmd\git.exe" (
        set "GIT_CMD=C:\Program Files\Git\cmd\git.exe"
    ) else if exist "%LOCALAPPDATA%\Programs\Git\cmd\git.exe" (
        set "GIT_CMD=%LOCALAPPDATA%\Programs\Git\cmd\git.exe"
    )
)

set "TOKEN=%~1"

if "%TOKEN%"=="" (
    echo To push your code to GitHub, please enter your GitHub Personal Access Token (PAT).
    echo (You can create one at https://github.com/settings/tokens with 'repo' permission)
    echo.
    set /p TOKEN="Enter GitHub Token (or press ENTER to use default Git login): "
)

if "%TOKEN%"=="" (
    echo.
    echo Pushing using standard Git authentication...
    "%GIT_CMD%" push origin main
) else (
    echo.
    echo Pushing repository to https://github.com/imtiaz571/NLP ...
    "%GIT_CMD%" push https://%TOKEN%@github.com/imtiaz571/NLP.git main
)

if %ERRORLEVEL% equ 0 (
    echo.
    echo =======================================================
    echo  SUCCESS! All code has been successfully pushed.
    echo  View repository: https://github.com/imtiaz571/NLP
    echo =======================================================
) else (
    echo.
    echo Push encountered an error.
    echo Please verify your token permissions (ensure 'repo' is checked).
)

echo.
pause
