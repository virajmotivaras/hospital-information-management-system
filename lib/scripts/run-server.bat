@echo off
cd /d "%~dp0..\..\Hospital.Api"
if not exist ".venv\Scripts\python.exe" (
  python -m venv .venv
)
".venv\Scripts\python.exe" -m pip install -r requirements.txt
".venv\Scripts\python.exe" manage.py migrate
".venv\Scripts\python.exe" manage.py bootstrap_roles
".venv\Scripts\python.exe" manage.py runserver 0.0.0.0:8000
