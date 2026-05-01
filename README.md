# Hospital Information Management System

Local-first hospital management prototype for a gynecology and pediatrics focused hospital.

## Current Features

- Quick patient check-in with minimal required data.
- Automatic repeat-patient detection by mobile number or patient plus guardian name.
- Waiting queue for consultation.
- Patient search.
- Appointment scheduling.
- Prescription creation with printable prescription page.
- Staff login with Reception, Doctor, and Admin roles.
- Admin-managed hospital name, logo, address, and backup folder.
- Plain HTML/CSS/JavaScript frontend served by Django.

## Project Structure

```text
Hospital.Api/
  api/          HTTP endpoints
  domain/       business rules and workflows
  repository/   Django models and data access
Hospital.Web/   browser frontend
Hospital.Tests/ automated tests
lib/docs/       manuals and deployment notes
```

## Run Locally

```bat
cd Hospital.Api
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python manage.py migrate
.venv\Scripts\python manage.py bootstrap_roles
.venv\Scripts\python manage.py runserver 0.0.0.0:8000
```

Create the first admin user:

```bat
cd Hospital.Api
.venv\Scripts\python manage.py createsuperuser
```

Then log in at `/admin/`, create staff users, and assign them to `Reception`, `Doctor`, or `Admin`.

Open the app on the server computer:

```text
http://127.0.0.1:8000
```

Other devices on the same network can open:

```text
http://SERVER-LAPTOP-IP:8000
```

## Run Tests

```bat
python lib\scripts\run_django_tests.py
```

If you install dependencies into `Hospital.Api\.deps` instead of a virtual environment, run commands with:

```bat
set PYTHONPATH=Hospital.Api\.deps
python lib\scripts\run_django_tests.py
```
