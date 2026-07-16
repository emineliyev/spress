import time

from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand

from apps.media_manager.services import TEMP_DIR

MAX_AGE_SECONDS = 24 * 60 * 60


class Command(BaseCommand):
    help = (
        'Deletes files under media/temp/ older than 24 hours — uploads staged '
        'via the Media Library crop flow that were never confirmed or discarded '
        '(CLAUDE.md ch.4 "Management Commands... Remove temporary files"). '
        'No Celery Beat schedule is configured yet, so run this via an external '
        'cron in production.'
    )

    def handle(self, *args, **options):
        try:
            _, files = default_storage.listdir(TEMP_DIR)
        except FileNotFoundError:
            self.stdout.write('No temp directory yet — nothing to clean.')
            return

        cutoff = time.time() - MAX_AGE_SECONDS
        removed = 0
        for filename in files:
            path = f'{TEMP_DIR}/{filename}'
            modified = default_storage.get_modified_time(path).timestamp()
            if modified < cutoff:
                default_storage.delete(path)
                removed += 1

        self.stdout.write(self.style.SUCCESS(f'Removed {removed} stale temp upload(s) out of {len(files)}.'))
