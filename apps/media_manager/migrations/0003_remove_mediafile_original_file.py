from django.db import migrations


def delete_original_files_from_storage(apps, schema_editor):
    """Reclaims disk space before the column itself is dropped below —
    the as-uploaded source was never actually read back anywhere (no
    re-crop-in-place feature ever used it), so every row's original_file
    has been dead weight on disk since the day it was written."""
    MediaFile = apps.get_model('media_manager', 'MediaFile')
    for media_file in MediaFile.objects.exclude(original_file=''):
        media_file.original_file.delete(save=False)


class Migration(migrations.Migration):

    dependencies = [
        ('media_manager', '0002_mediafile_original_file_mediafile_thumbnail_folder_and_more'),
    ]

    operations = [
        migrations.RunPython(delete_original_files_from_storage, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name='mediafile',
            name='original_file',
        ),
    ]
