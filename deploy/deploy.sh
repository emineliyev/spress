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
STATUS=$(curl -s -o /dev/null -w "%{http_code}" -H "Host: spress.az" http://127.0.0.1/)
if [ "$STATUS" != "200" ]; then
    echo "Health check FAILED — homepage returned HTTP $STATUS" >&2
    echo "Check: sudo journalctl -u spress-gunicorn -n 50" >&2
    exit 1
fi

echo "==> Deploy complete, homepage responded 200"
