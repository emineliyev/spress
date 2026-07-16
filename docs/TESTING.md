# Testing

Three layers, each with a different job. Run all three before merging
anything non-trivial; CI (`.github/workflows/ci.yml`) runs the first two
automatically on every push/PR.

## 1. Backend — pytest

```bash
pip install -r requirements/development.txt
pytest                              # whole suite
pytest apps/news/                   # one app
pytest --cov=apps --cov-report=term-missing   # with coverage
```

Settings: `config/settings/test.py` (inherits `development.py`, fast
password hasher, media isolated to `test_media/` so nothing lands in the
real `media/` folder). Uses the same PostgreSQL database as development —
Django creates/drops a throwaway `test_<dbname>` automatically
(`--reuse-db` in `pytest.ini` keeps it between runs for speed; pass
`--create-db` once if you need a clean rebuild, e.g. after editing a
migration).

**One-time local setup**: the database role in `DATABASE_URL` needs
`CREATEDB` for Django to create that throwaway database:

```sql
ALTER ROLE news_user CREATEDB;
```

**Fixtures & factories**: shared fixtures live in the root `conftest.py`
(`administrator`, `journalist`, `admin_client`, `category`,
`published_news`, `media_file`, `sample_image_bytes`, ...). Reuse these
instead of constructing objects by hand in a new test.

**What's covered** (107 tests, ~84% of `apps/`): permission checks on
every CMS screen, the News publish/soft-delete/permanent-delete lifecycle
and its media cleanup, category hierarchy + empty-category nav hiding,
the view counter's per-session dedup, upload validation (size/type/
corrupted files), slug generation/uniqueness, one CRUD smoke test per
CMS-managed model, and the public-facing views (home, article, category,
search, sitemap, robots.txt).

**What's deliberately not covered**: pixel-level template rendering,
CKEditor's internal behavior, the `clean_temp_uploads` management
command. Those are either a Playwright concern (below) or low enough
risk/impact not to justify unit coverage yet.

## 2. Frontend — Playwright (e2e/)

```bash
cd e2e
npm install
npx playwright install chromium     # once
npx playwright test
```

This is a **real, separate environment** — never the developer's own
`news_db`. `playwright.config.js`'s `webServer` starts `manage.py
runserver` under `config.settings.e2e`, which points at its own database
(`news_db_e2e` by default) and its own Redis logical DB (index 3, not
development's index 1). `global-setup.js` runs once per `playwright test`
invocation and creates-if-missing, migrates, flushes and reseeds that
database (`apps/core/management/commands/bootstrap_e2e_db.py`) — every
run starts from the same known state (one administrator, one category,
one social link) regardless of what a previous run left behind.

This separation matters: the e2e suite creates, soft-deletes and
permanently deletes real articles as part of testing the CMS. Running
that against a shared/real database would be exactly the kind of
destructive, unattended action worth avoiding.

Login credentials for the seeded administrator:
`e2e_admin` / `E2E-test-password-123` (`bootstrap_e2e_db.py`).

Specs: `home.spec.js`, `article.spec.js`, `cms-auth.spec.js`,
`cms-news.spec.js` (the full create → soft-delete → restore →
permanent-delete-with-media-cleanup lifecycle), `contact-form.spec.js`,
`mobile-nav.spec.js`.

Tests run with `workers: 1` — every spec shares one database/server, so
parallel workers would race each other's writes.

## 3. Load — Locust (stress_tests/)

```bash
pip install -r requirements/development.txt   # locust is in there
locust -f stress_tests/locustfile.py --host=http://127.0.0.1:8000
```

Then open `http://localhost:8089`, pick a user count/spawn rate, and
watch response times and error rate climb (or not) as load increases.
For a quick unattended run:

```bash
locust -f stress_tests/locustfile.py --host=http://127.0.0.1:8000 \
    --headless --users 50 --spawn-rate 5 --run-time 2m
```

`ReaderUser` (the bulk of the weight) never hardcodes a slug — it reads
the homepage's actual rendered links and picks a real category/article
to visit, so the same locustfile works unchanged against any host with
any content. `CmsStaffUser` only performs a real login if
`LOCUST_CMS_USERNAME`/`LOCUST_CMS_PASSWORD` are set in the environment;
otherwise it just repeats the anonymous `/cms/` redirect.

**Never point this at a production host without the site owner's
explicit go-ahead** — even read-only load-test traffic can degrade a
real, publicly-serving box. Run it against a local dev server or a
disposable staging environment.
