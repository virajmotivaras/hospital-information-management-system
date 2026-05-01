# Local Deployment Notes

The intended deployment is one Windows computer acting as the server.

## Network Access

Run Django on all network interfaces:

```bat
python manage.py runserver 0.0.0.0:8000
```

Other devices connect with:

```text
http://SERVER-IP:8000
```

For trial use, allow port `8000` through Windows Firewall.

## First-Time Setup

After installing dependencies and running migrations:

```bat
python manage.py bootstrap_roles
python manage.py createsuperuser
```

Use the superuser to open `/admin/`.

Create normal staff users:

- Reception users: assign group `Reception`.
- Doctor users: assign group `Doctor`.
- Admin users: assign group `Admin` and enable `staff status`.

## Backups

The admin panel includes `Hospital profile`.

Set `backup_folder_path` to an existing empty folder on the server machine. Then select the hospital profile row and run the `Create database backup now` admin action.

For the current SQLite prototype, the backup action copies `db.sqlite3` into that folder.

For production, use PostgreSQL and scheduled `pg_dump` backups instead of relying only on manual SQLite copies.

## Later Production Packaging

For a non-development installation:

- package the backend with PyInstaller, Nuitka, or an installer that includes Python;
- run the backend as a Windows service;
- use PostgreSQL instead of SQLite for serious multi-user usage;
- add automated backups;
- give the server computer a static LAN IP address.
