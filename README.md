# SPress

A production-grade Azerbaijani news portal — Django, PostgreSQL, Redis,
Celery on the backend; server-rendered Django Templates, vanilla CSS/JS
on the frontend. No SPA framework, no jQuery. Full standards are in
[`CLAUDE.md`](CLAUDE.md); the phase-by-phase build history is in
[`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

## Quickstart (local development)

Requirements: Python 3.14, PostgreSQL, Redis.

```bash
git clone https://github.com/emineliyev/spress.git
cd spress

python -m venv .venv
.venv/Scripts/activate          # .venv/bin/activate on macOS/Linux
pip install -r requirements/development.txt

cp .env.example .env            # then edit DJANGO_SECRET_KEY, DATABASE_URL, ...

createdb news_db                # or via psql: CREATE DATABASE news_db;
python manage.py migrate
python manage.py createsuperuser

python manage.py runserver
```

Public site at `http://127.0.0.1:8000/`, CMS at `http://127.0.0.1:8000/cms/`.

## Testing

Three layers — backend (pytest), end-to-end (Playwright), load (Locust).
Full instructions: [`docs/TESTING.md`](docs/TESTING.md).

```bash
pytest                              # backend
cd e2e && npx playwright test       # end-to-end
locust -f stress_tests/locustfile.py --host=http://127.0.0.1:8000   # load
```

## Deployment

Manual deploy to a Hostinger VPS (or any Ubuntu/Debian VPS) — venv +
systemd + Nginx, no Docker. Full runbook: [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md).

## Project structure

```
apps/               Django apps, one per domain (news, categories, cms, ...)
config/              settings/ (base/development/production/test/e2e), urls, wsgi, celery
templates/           Django templates, grouped by app + shared components/
static/              CSS/JS/vendor assets
deploy/              systemd units, Nginx config, deploy.sh
e2e/                 Playwright end-to-end suite
stress_tests/        Locust load test
docs/                Architecture history, testing guide, deployment runbook
```
