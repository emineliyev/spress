# Deployment — GitHub → Hostinger VPS

Classic stack, no containers: a Python venv, systemd services, Nginx in
front. Matches CLAUDE.md ch.3's stated backend stack directly — nothing
here needs Docker to exist first. Deploys are **manual, by design**: you
run `deploy/deploy.sh` yourself when you decide production should move,
never automatically on every push.

## One-time VPS setup

Assumes a fresh Ubuntu/Debian VPS with root access (Hostinger VPS plans
give you this) and a domain (`spress.az`) already pointed at the VPS's IP.

```bash
# 1. System packages
sudo apt update
sudo apt install -y python3.14 python3.14-venv postgresql redis-server nginx git

# 2. Dedicated system user — the app never runs as root
sudo adduser --system --group --home /opt/spress spress

# 3. Database + role
sudo -u postgres psql -c "CREATE ROLE spress WITH LOGIN PASSWORD 'CHANGE-ME';"
sudo -u postgres psql -c "CREATE DATABASE spress_db OWNER spress;"

# 4. Clone the repo
sudo -u spress git clone https://github.com/emineliyev/spress.git /opt/spress
cd /opt/spress

# 5. Virtualenv + dependencies
sudo -u spress python3.14 -m venv .venv
sudo -u spress .venv/bin/pip install -r requirements/production.txt

# 6. Environment file — copy .env.example, then fill in REAL values:
#    DJANGO_SETTINGS_MODULE=config.settings.production
#    DJANGO_SECRET_KEY=<random 50+ chars — see below>
#    DJANGO_ALLOWED_HOSTS=spress.az,www.spress.az
#    DATABASE_URL=postgres://spress:CHANGE-ME@localhost:5432/spress_db
#    REDIS_URL / CELERY_BROKER_URL / CELERY_RESULT_BACKEND (redis://127.0.0.1:6379/N)
#    EMAIL_* (real SMTP credentials — contact-form emails go through these)
sudo -u spress cp .env.example .env
sudo -u spress nano .env
python -c "import secrets; print(secrets.token_urlsafe(50))"   # generate the secret key

# 7. Log directory (systemd units write here) + first migration + static files
sudo -u spress mkdir -p /opt/spress/logs
sudo -u spress .venv/bin/python manage.py migrate
sudo -u spress .venv/bin/python manage.py collectstatic --noinput
sudo -u spress .venv/bin/python manage.py createsuperuser

# 8. systemd services
sudo cp deploy/gunicorn.service /etc/systemd/system/spress-gunicorn.service
sudo cp deploy/celery-worker.service /etc/systemd/system/spress-celery-worker.service
sudo systemctl daemon-reload
sudo systemctl enable --now spress-gunicorn spress-celery-worker

# 8b. Let `spress` restart its own services without a password — deploy.sh
#     (step 12 below) does this on every deploy, and `spress` (a system
#     account, adduser --system --group) has no password of its own for
#     an interactive sudo prompt to even check against. Scoped to just
#     these two exact commands (principle of least privilege, CLAUDE.md
#     ch.12), not blanket sudo access.
echo 'spress ALL=(root) NOPASSWD: /usr/bin/systemctl restart spress-gunicorn, /usr/bin/systemctl restart spress-celery-worker' | sudo tee /etc/sudoers.d/spress-deploy
sudo chmod 0440 /etc/sudoers.d/spress-deploy
sudo visudo -c

# 9. Nginx
sudo cp deploy/nginx.conf /etc/nginx/sites-available/spress.az
sudo ln -s /etc/nginx/sites-available/spress.az /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx

# 10. HTTPS (certbot edits the Nginx config in place to add the 443/ssl_certificate directives)
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d spress.az -d www.spress.az

# 11. Cron — two management commands expect to run periodically; neither
#     has a Celery Beat schedule (see below), so both run via plain cron.
sudo -u spress crontab -e
# Add these two lines:
#   */5 * * * * cd /opt/spress && .venv/bin/python manage.py publish_scheduled >> logs/cron.log 2>&1
#   0 3 * * *   cd /opt/spress && .venv/bin/python manage.py clean_temp_uploads >> logs/cron.log 2>&1
```

No Celery Beat service — nothing in this project runs on a recurring
schedule via Celery. Two things still need to happen periodically
regardless, so they run as plain cron jobs instead (step 11 above):

- `publish_scheduled` flips a Scheduled article to Published once its
  `published_at` arrives. **This is not automatic otherwise** —
  `News.objects.published()` only ever matches `status=PUBLISHED`, so a
  Scheduled article whose time has passed just sits there forever,
  invisible to readers, until this command (or a manual status edit)
  runs. Every 5 minutes is a reasonable default; tighten it if same-
  minute scheduling accuracy matters.
- `clean_temp_uploads` deletes `media/temp/` uploads older than 24
  hours (crop-flow uploads that were never confirmed or discarded).
  Once a day is plenty.

Add a real Celery Beat schedule later only if a task shows up that
genuinely needs sub-minute precision or Celery's own retry/monitoring —
cron is simpler and sufficient for both of these today.

## Updating production (every deploy after the first)

```bash
sudo -u spress -i
cd /opt/spress
./deploy/deploy.sh
```

`deploy.sh` pulls `main`, reinstalls dependencies, migrates, collects
static files, restarts both services, then checks the homepage actually
returns 200 before declaring success. If the health check fails, it
exits non-zero and points at `journalctl -u spress-gunicorn` — investigate
before assuming the previous deploy is still serving traffic correctly.

## Rolling back

There's no automatic rollback. To revert:

```bash
cd /opt/spress
git log --oneline -5          # find the last-known-good commit
git checkout <commit-sha>
./deploy/deploy.sh
```

## What CI does and doesn't do

`.github/workflows/ci.yml` runs the full pytest + Playwright suite on
every push and PR (`docs/TESTING.md`). It never touches the VPS and
needs no deploy credentials — a green check just means "safe to deploy
whenever you choose to," not "already deployed."
