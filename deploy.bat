@echo off
REM Project name
set project=projects_tools

set ROOT_DIR=%cd%

REM Extract version number using Python
for /f "tokens=*" %%a in ('python -c "with open('src/projects_tools/version.py') as f: print([line.split('=')[1].strip().strip('\"') for line in f if '__version__' in line][0])"') do set version=%%a
echo Build %project% %version%

REM Clean dist directory
echo Clean dist
if exist .\dist\ (
    del /Q .\dist\*
) else (
    mkdir .\dist
)

REM Uninstall current version of the project
echo Uninstall %project%
pip uninstall -y %project%

REM Build project
echo Build %project% %version%
python setup.py sdist bdist_wheel
cd .\dist\

REM Install new version of the project
echo Install %project% %version%
pip install %project%-%version%-py3-none-any.whl && cd %ROOT_DIR%

REM Default mode setting
if not defined MODE (
    set MODE=release
)

REM Release mode operations
if "%MODE%"=="release" (
    git tag v%version%
    git push origin v%version%
    echo Upload %project% %version%
    twine upload dist/*
)
