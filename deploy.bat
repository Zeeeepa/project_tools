@echo off
REM Windows Deployment Script for projects_tools

echo Building projects_tools %1

REM Get version from version.py
for /f "tokens=*" %%a in ('python -c "with open('src/projects_tools/version.py') as f: print([line.split('=')[1].strip().strip('\"') for line in f if '__version__' in line][0])"') do set version=%%a
echo Building projects_tools %version%

REM Clean dist directory
echo Cleaning dist directory
if exist dist rmdir /s /q dist

REM Uninstall current version
echo Uninstalling current version of projects_tools
pip uninstall -y projects_tools

REM Build project
echo Building projects_tools %version%
python setup.py sdist bdist_wheel
cd dist

REM Install new version
echo Installing projects_tools %version%
for %%f in (projects_tools-%version%-py3-none-any.whl) do pip install %%f
cd ..

REM Set deployment mode
if "%1"=="" (
    set MODE=release
) else (
    set MODE=%1
)

REM Release mode operations
if "%MODE%"=="release" (
    git tag v%version%
    git push origin v%version%
    echo Uploading projects_tools %version%
    twine upload dist/*
)

echo Deployment completed successfully!
