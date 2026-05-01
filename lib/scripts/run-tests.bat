@echo off
cd /d "%~dp0..\.."
python lib\scripts\run_django_tests.py
