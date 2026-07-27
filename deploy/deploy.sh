#!/usr/bin/env bash
# Manual deploy — run this ON THE VPS, in /opt/spress, as the `spress` user
# (or via sudo -u spress), after pushing the commit you want live to GitHub.
# Deliberately not automatic on every push (docs/DEPLOYMENT.md) — you decide
# when production actually moves.
#
# Usage: ./deploy/deploy.sh

set -euo pipefail

PROJECT_ROOT="/opt/spress"
VENV="$PROJECT_ROOT/.venv"

cd "$PROJECT_ROOT"

# manage.py's own fallback (os.environ.setdefault, manage.py) is
# 'config.settings.development' — only gunicorn.service's
# EnvironmentFile=/opt/spress/.env sets this correctly on its own.
# Every manage.py call below was silently running under *development*
# settings until this line existed (confirmed the hard way: migrate/
# collectstatic still "worked" since dev and prod share the same
# DATABASE_URL via .env, so nothing looked wrong — until
# ManifestStaticFilesStorage, a production-only setting, needed
# collectstatic to actually run under production for its manifest to
# be built at all).
export DJANGO_SETTINGS_MODULE=config.settings.production

echo "==> Pulling latest code"
git pull --ff-only origin main

echo "==> Installing dependencies"
"$VENV/bin/pip" install -r requirements/production.txt

echo "==> Running database migrations"
"$VENV/bin/python" manage.py migrate --noinput

echo "==> Collecting static files"
"$VENV/bin/python" manage.py collectstatic --noinput

echo "==> Restarting services"
sudo systemctl restart spress-gunicorn
sudo systemctl restart spress-celery-worker

echo "==> Health check"
sleep 2
# HTTPS, not plain HTTP — since certbot ran (docs/DEPLOYMENT.md step 10),
# Nginx itself redirects every port-80 request to https://, so a plain
# "http://127.0.0.1/" check here always gets a 301 regardless of whether
# the app is actually healthy. --resolve points the real spress.az
# hostname (correct SNI + Host header + a certificate that actually
# validates) at the loopback address instead of hitting port 80 directly.
STATUS=$(curl -s -o /dev/null -w "%{http_code}" --resolve spress.az:443:127.0.0.1 https://spress.az/)
if [ "$STATUS" != "200" ]; then
    echo "Health check FAILED — homepage returned HTTP $STATUS" >&2
    echo "Check: sudo journalctl -u spress-gunicorn -n 50" >&2
    exit 1
fi

echo "==> Deploy complete, homepage responded 200"
