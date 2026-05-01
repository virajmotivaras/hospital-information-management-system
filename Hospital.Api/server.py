import os
import sys
from pathlib import Path


def application_root():
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def bundled_root():
    return Path(getattr(sys, "_MEIPASS", application_root()))


def configure_environment():
    root = application_root()
    data_dir = root / "data"
    data_dir.mkdir(exist_ok=True)

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hospital_api.settings")
    os.environ.setdefault("HOSPITAL_DB_NAME", str(data_dir / "hospital.sqlite3"))
    os.environ.setdefault("HOSPITAL_FRONTEND_DIR", str(bundled_root() / "Hospital.Web"))
    os.environ.setdefault("HOSPITAL_DEBUG", "1")
    os.environ.setdefault("HOSPITAL_ALLOWED_HOSTS", "*")


def main():
    configure_environment()

    from django.core.management import call_command, execute_from_command_line

    if len(sys.argv) > 1:
        execute_from_command_line(sys.argv)
        return

    call_command("migrate", interactive=False, verbosity=1)
    call_command("bootstrap_roles")
    bind_address = os.environ.get("HOSPITAL_BIND_ADDRESS", "0.0.0.0")
    port = os.environ.get("HOSPITAL_PORT", "8000")
    execute_from_command_line(
        [
            sys.argv[0],
            "runserver",
            f"{bind_address}:{port}",
            "--noreload",
        ]
    )


if __name__ == "__main__":
    main()
