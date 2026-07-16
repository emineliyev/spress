"""
Prepares the database `config.settings.e2e` points at: creates it if it
doesn't exist yet, migrates it, then flushes and reseeds the fixed set
of fixtures the Playwright suite (e2e/) logs in as / creates content
against.

Run only under `--settings=config.settings.e2e` — `e2e/global-setup.js`
is the only caller, once per test run, so every run starts from the
same known state regardless of what a previous run left behind.
"""

import psycopg
from django.core.cache import cache
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import connection

E2E_ADMIN_USERNAME = 'e2e_admin'
E2E_ADMIN_PASSWORD = 'E2E-test-password-123'


class Command(BaseCommand):
    help = 'Creates (if needed), migrates and reseeds the e2e test database.'

    def handle(self, *args, **options):
        db_settings = connection.settings_dict
        db_name = db_settings['NAME']

        if 'e2e' not in db_name:
            # A safeguard against ever running this against a database
            # that isn't clearly the dedicated e2e one — this command
            # flushes everything.
            raise SystemExit(
                f'Refusing to run: database name "{db_name}" does not look like '
                'an e2e database (expected "e2e" in the name).'
            )

        self._ensure_database_exists(db_settings, db_name)

        call_command('migrate', verbosity=0)
        call_command('flush', verbosity=0, interactive=False)
        cache.clear()  # also resets any leftover login-lockout counters from a previous run

        self._seed()
        self.stdout.write(self.style.SUCCESS(f'e2e database "{db_name}" ready.'))

    def _ensure_database_exists(self, db_settings, db_name):
        maintenance_dsn = (
            f"postgresql://{db_settings['USER']}:{db_settings['PASSWORD']}"
            f"@{db_settings['HOST']}:{db_settings['PORT']}/postgres"
        )
        conn = psycopg.connect(maintenance_dsn, autocommit=True)
        try:
            exists = conn.execute(
                'SELECT 1 FROM pg_database WHERE datname = %s', (db_name,),
            ).fetchone()
            if not exists:
                conn.execute(f'CREATE DATABASE "{db_name}"')
                self.stdout.write(f'Created database "{db_name}".')
        finally:
            conn.close()

    def _seed(self):
        from apps.accounts.models import User
        from apps.categories.models import Category
        from apps.settings_app.models import SocialLink

        User.objects.create_user(
            username=E2E_ADMIN_USERNAME,
            password=E2E_ADMIN_PASSWORD,
            role=User.Role.ADMINISTRATOR,
            email='e2e_admin@example.com',
        )
        Category.objects.create(name='İqtisadiyyat')
        SocialLink.objects.create(platform=SocialLink.Platform.FACEBOOK, url='https://facebook.com/spress')
