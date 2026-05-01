@echo off
setlocal
cd /d "%~dp0..\.."
python -m pip install --upgrade --target "lib\build\pyinstaller-deps" -r "Hospital.Api\requirements.txt" pyinstaller
set PYTHONPATH=%CD%\lib\build\pyinstaller-deps
python -m PyInstaller --clean --noconfirm "lib\packaging\hospital_api.spec" --distpath "lib\dist" --workpath "lib\build\pyinstaller-work"
