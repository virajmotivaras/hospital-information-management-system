import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
API_DIR = ROOT / "Hospital.Api"
DEPS_DIR = API_DIR / ".deps"
TESTS_DIR = ROOT / "Hospital.Tests"

sys.path.insert(0, str(API_DIR))
if DEPS_DIR.exists():
    sys.path.insert(0, str(DEPS_DIR))

import django
from django.conf import settings
from django.test.runner import DiscoverRunner


def main():
    django.setup()
    runner = DiscoverRunner(verbosity=2)
    old_config = runner.setup_databases()
    try:
        suite = unittest.defaultTestLoader.discover(
            start_dir=str(TESTS_DIR),
            pattern="test*.py",
            top_level_dir=str(TESTS_DIR),
        )
        result = runner.run_suite(suite)
    finally:
        runner.teardown_databases(old_config)
    return 1 if result.failures or result.errors else 0


if __name__ == "__main__":
    import os

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hospital_api.settings")
    raise SystemExit(main())
