# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path
import sys

from PyInstaller.utils.hooks import collect_data_files, collect_submodules


ROOT = Path(SPECPATH).parents[1]
API_DIR = ROOT / "Hospital.Api"
WEB_DIR = ROOT / "Hospital.Web"

sys.path.insert(0, str(API_DIR))


a = Analysis(
    [str(API_DIR / "server.py")],
    pathex=[str(API_DIR)],
    binaries=[],
    datas=[
        (str(WEB_DIR), "Hospital.Web"),
        *collect_data_files("repository", includes=["templates/**", "migrations/**"]),
    ],
    hiddenimports=[
        *collect_submodules("api"),
        *collect_submodules("domain"),
        *collect_submodules("hospital_api"),
        *collect_submodules("repository"),
        "hospital_api.settings",
        "repository.apps",
        "repository.migrations",
        "django.contrib.admin",
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.messages",
        "django.contrib.staticfiles",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="HospitalApi",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
