from pathlib import Path
import os


BASE_DIR = Path(__file__).resolve().parent.parent
REPO_DIR = BASE_DIR.parent
FRONTEND_DIR = Path(os.environ.get("HOSPITAL_FRONTEND_DIR", REPO_DIR / "Hospital.Web"))

SECRET_KEY = os.environ.get("HOSPITAL_SECRET_KEY", "dev-only-change-before-deployment")
DEBUG = os.environ.get("HOSPITAL_DEBUG", "1") == "1"
ALLOWED_HOSTS = os.environ.get("HOSPITAL_ALLOWED_HOSTS", "*").split(",")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "repository.apps.RepositoryConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "api.middleware.ForcePasswordChangeMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]

ROOT_URLCONF = "hospital_api.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [FRONTEND_DIR],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    }
]

WSGI_APPLICATION = "hospital_api.wsgi.application"
ASGI_APPLICATION = "hospital_api.asgi.application"

DATABASES = {
    "default": {
        "ENGINE": os.environ.get("HOSPITAL_DB_ENGINE", "django.db.backends.sqlite3"),
        "NAME": os.environ.get("HOSPITAL_DB_NAME", BASE_DIR / "db.sqlite3"),
    }
}

LANGUAGE_CODE = "en-us"
TIME_ZONE = os.environ.get("HOSPITAL_TIME_ZONE", "Europe/Stockholm")
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATICFILES_DIRS = [FRONTEND_DIR]
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/login/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
