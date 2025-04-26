@echo off
setlocal EnableDelayedExpansion

REM Project Tools Deployment Script for Windows
REM Setup logging
set LOGFILE=deploy_%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%.log
call :log "Starting deployment process"

REM Validate environment
call :log "Validating environment"
where python >nul 2>nul
if errorlevel 1 (
    call :log "Error: Python is not installed or not in PATH"
    exit /b 1
)

where pip >nul 2>nul
if errorlevel 1 (
    call :log "Error: pip is not installed or not in PATH"
    exit /b 1
)

where git >nul 2>nul
if errorlevel 1 (
    call :log "Error: git is not installed or not in PATH"
    exit /b 1
)

where twine >nul 2>nul
if errorlevel 1 (
    call :log "Error: twine is not installed or not in PATH"
    exit /b 1
)

REM Project name
set project=projects_tools

REM Get current directory
set ROOT_DIR=%cd%
call :log "Working directory: %ROOT_DIR%"

REM Extract version
set "error=0"
call :log "Extracting version"
python -c "with open('src/projects_tools/version.py') as f: print([line.split('=')[1].strip().strip('\"') for line in f if '__version__' in line][0])" > temp.txt
if errorlevel 1 (
    call :log "Error: Failed to extract version"
    exit /b 1
)
set /p version=<temp.txt
del temp.txt
call :log "Building %project% version %version%"

REM Clean dist directory
call :log "Cleaning dist directory"
if exist dist (
    rmdir /s /q dist || (
        call :log "Error: Failed to clean dist directory"
        exit /b 1
    )
)
mkdir dist

REM Build and install
call :execute_with_error "pip uninstall -y %project%" "Uninstall failed"
call :execute_with_error "python setup.py sdist bdist_wheel" "Build failed"
cd dist || exit /b 1
call :execute_with_error "pip install %project%-%version%-py3-none-any.whl" "Installation failed"
cd %ROOT_DIR%

if "%MODE%"=="" set MODE=release
call :log "Mode: %MODE%"

if "%MODE%"=="release" (
    call :execute_with_error "git tag v%version%" "Tagging failed"
    call :execute_with_error "git push origin v%version%" "Tag push failed"
    call :log "Uploading %project% %version%"
    call :execute_with_error "twine upload dist/*" "Upload failed"
)

call :log "Deployment completed successfully"
exit /b %error%

:execute_with_error
call :log "Executing: %~1"
%~1
if errorlevel 1 (
    call :log "Error: %~2"
    set error=1
    exit /b 1
)
exit /b 0

:log
echo %date% %time% - %~1 >> %LOGFILE%
echo %~1
exit /b 0
