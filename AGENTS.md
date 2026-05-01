# Hospital Information Management System Instructions

These instructions define the preferred project shape and coding style for this repository. Follow them when creating or modifying the hospital management system.

## Product Direction

- Build a locally hosted hospital information management system.
- The application should run on one Windows server laptop or desktop and be accessed by other laptops, desktops, and tablets through a browser on the same local network.
- Prefer a browser-based LAN application over installing a desktop executable on every client machine.
- The server package should eventually be deployable on a Windows computer without requiring a development environment.

## Preferred Stack

- Backend: Python with Django.
- Frontend: HTML, CSS, and JavaScript.
- Database: PostgreSQL for real multi-user usage. SQLite is acceptable only for early prototypes or demos.
- Deployment target: Windows server machine, ideally with the backend packaged as an executable or installed as a Windows service.

## Solution-Style Directory Structure

Model the repository after the user's familiar C#/.NET layered solution style:

```text
hospital-information-management-system/
  lib/
  Hospital.Api/
  Hospital.Domain/
  Hospital.Repository/
  Hospital.Tests/
  Hospital.Web/
  AGENTS.md
```

Use these folders as Python/Django equivalents of the .NET projects:

- `Hospital.Api/`: Django project entry point, URL routing, API views/controllers, request/response serializers, middleware, app configuration, and server startup.
- `Hospital.Domain/`: core business entities, domain services, validation rules, constants, enums, permissions, and business workflows that should not depend on web framework details where practical.
- `Hospital.Repository/`: database access layer, Django models, query helpers, repositories, migrations, and persistence-related code.
- `Hospital.Tests/`: automated tests for API, domain, repository, and frontend-adjacent behavior where useful.
- `Hospital.Web/`: browser frontend built with HTML, CSS, and JavaScript.
- `lib/`: shared scripts, deployment helpers, packaging files, reusable utilities, documentation fragments, or local tooling.

Keep folder names close to the .NET-style names above unless the user explicitly asks to rename them.

## Backend Structure Guidance

Inside `Hospital.Api/`, prefer a Django layout similar to:

```text
Hospital.Api/
  manage.py
  hospital_api/
    __init__.py
    settings.py
    urls.py
    wsgi.py
    asgi.py
  apps/
    patients/
    appointments/
    staff/
    billing/
    inventory/
```

Backend rules:

- Keep HTTP concerns in `Hospital.Api/`.
- Keep business rules in `Hospital.Domain/`.
- Keep persistence concerns in `Hospital.Repository/`.
- Do not put large business workflows directly inside Django views.
- Use Django REST Framework if building JSON APIs.
- Use class-based services for non-trivial workflows.
- Use repository/query helper modules when database access becomes repeated or complex.
- Prefer relative frontend API calls such as `/api/patients/` instead of hardcoded IP addresses.
- Configure the server to listen on `0.0.0.0` for LAN access when deployed locally.
- Keep secrets, database credentials, host names, and ports in environment variables or config files, not hardcoded in source.

## Domain Layer Guidance

`Hospital.Domain/` should contain business language and hospital concepts, for example:

```text
Hospital.Domain/
  patients/
    entities.py
    services.py
    rules.py
  appointments/
    services.py
    rules.py
  staff/
  billing/
  common/
    errors.py
    permissions.py
    value_objects.py
```

Use this layer for rules such as:

- patient registration validation,
- appointment scheduling rules,
- role and permission decisions,
- billing calculations,
- discharge workflow rules,
- stock/inventory thresholds.

Avoid importing Django views from this layer. If Django models are needed, keep that dependency deliberate and minimal.

## Repository Layer Guidance

`Hospital.Repository/` should own database-facing implementation details:

```text
Hospital.Repository/
  models/
  migrations/
  repositories/
  queries/
```

Repository rules:

- Put Django models and migrations here if the chosen Django configuration supports it cleanly.
- If Django app conventions make that awkward, keep models inside Django apps but preserve the conceptual repository boundary with `repositories.py`, `queries.py`, or package-level repository modules.
- Keep raw SQL rare and documented.
- Prefer Django ORM querysets for normal data access.
- Add indexes and constraints for identifiers, dates, patient records, appointment lookups, and billing references when the schema matures.

## Frontend Structure Guidance

Use plain HTML, CSS, and JavaScript in `Hospital.Web/`:

```text
Hospital.Web/
  index.html
  assets/
    images/
    icons/
  css/
    base.css
    layout.css
    components.css
    pages/
  js/
    app.js
    api/
    pages/
    components/
    utils/
```

Frontend rules:

- Build the real application screens directly, not a marketing landing page.
- Use browser-native HTML/CSS/JS unless the user later chooses a framework.
- Keep JavaScript modular by feature: API clients, page controllers, reusable components, and utilities.
- Use `fetch()` with relative API routes, for example `fetch("/api/patients/")`.
- Keep UI dense, clear, and operational. This is hospital software, so prioritize scanning, speed, forms, tables, search, filtering, and predictable navigation.
- Avoid decorative-heavy layouts. Use restrained styling, accessible contrast, and clear focus states.
- Make screens responsive for laptops, desktops, and tablets.
- Validate forms on the frontend for user experience, but rely on backend validation for correctness.
- Do not store sensitive medical data in local storage unless explicitly designed and justified.

## Local Network Hosting Guidance

- The backend should serve the frontend static files or be deployed with a small local web server.
- Client devices should connect through the server machine's LAN IP, for example `http://192.168.1.25:8000`.
- Production-like local deployment should document:
  - server IP or hostname,
  - port,
  - Windows Firewall rule,
  - database location,
  - backup process,
  - startup process.
- Plan for a static local IP address or local DNS name for the server machine.

## Packaging Guidance

For final Windows deployment:

- Package the Python backend using PyInstaller, Nuitka, cx_Freeze, or an installer-based Python runtime.
- Include the built/static frontend files with the backend package.
- Consider running the backend as a Windows service.
- Include database setup and migration commands in deployment scripts.
- Avoid requiring Angular, Node.js, Python, or development tools on client devices.

## Testing Guidance

- Put tests in `Hospital.Tests/`.
- Use pytest or Django's test runner consistently once selected.
- Cover domain rules first, then API behavior, then repository queries for important workflows.
- Add tests when changing business rules, permissions, billing behavior, appointment scheduling, or patient record handling.

## Coding Style

- Prefer clear, explicit names over abbreviations.
- Keep modules focused by feature and layer.
- Avoid large files that mix UI, API, database, and business rules.
- Write comments only when they clarify non-obvious business or technical decisions.
- Preserve this layered structure unless a Django convention clearly makes a small exception more maintainable.
