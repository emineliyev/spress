from django.db import migrations

# Maps the old fixed SiteSettings.social_* fields to the new SocialLink
# model's Platform choices — runs once, before those fields are dropped
# in the next migration, so any pre-existing URLs survive the switch to
# a flexible list instead of being silently discarded.
_FIELD_TO_PLATFORM = {
    'social_facebook': 'facebook',
    'social_instagram': 'instagram',
    'social_twitter': 'x',
    'social_youtube': 'youtube',
}


def migrate_social_links_forward(apps, schema_editor):
    SiteSettings = apps.get_model('settings_app', 'SiteSettings')
    SocialLink = apps.get_model('settings_app', 'SocialLink')

    settings_obj = SiteSettings.objects.filter(pk=1).first()
    if not settings_obj:
        return

    order = 0
    for field_name, platform in _FIELD_TO_PLATFORM.items():
        url = getattr(settings_obj, field_name, '')
        if url:
            SocialLink.objects.create(platform=platform, url=url, order=order)
            order += 1


def migrate_social_links_backward(apps, schema_editor):
    SiteSettings = apps.get_model('settings_app', 'SiteSettings')
    SocialLink = apps.get_model('settings_app', 'SocialLink')

    settings_obj = SiteSettings.objects.filter(pk=1).first()
    if not settings_obj:
        return

    platform_to_field = {v: k for k, v in _FIELD_TO_PLATFORM.items()}
    for link in SocialLink.objects.filter(platform__in=platform_to_field):
        setattr(settings_obj, platform_to_field[link.platform], link.url)
    settings_obj.save()


class Migration(migrations.Migration):

    dependencies = [
        ('settings_app', '0003_add_social_link'),
    ]

    operations = [
        migrations.RunPython(migrate_social_links_forward, migrate_social_links_backward),
    ]
