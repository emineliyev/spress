import json

from .models import NewsVideoCover

MAX_VIDEO_COVERS_PER_ARTICLE = 20


def sync_video_covers(article, payload_json):
    """Replaces `article`'s `NewsVideoCover` rows with whatever the CMS
    sidebar ("Video örtükləri", static/js/cms/video-covers.js) submitted
    alongside the article form — a plain JSON array of
    `{"video_id": "...", "cover_media_id": 123}` objects, one per YouTube
    video the JS found embedded in the live CKEditor content at submit
    time.

    Always a full replace, not a diff: simpler to reason about than
    matching up adds/removes, and this only ever runs once per form
    submission (CLAUDE.md ch.10 "transactions... multiple related
    records"). Malformed entries are skipped rather than raising —
    `content` is the source of truth for which videos exist; this is
    only ever an optional enhancement on top of it, never something a
    save should fail over.
    """
    from apps.media_manager.models import MediaFile

    try:
        entries = json.loads(payload_json) if payload_json else []
    except (TypeError, ValueError):
        entries = []

    covers = []
    seen_video_ids = set()
    for entry in entries[:MAX_VIDEO_COVERS_PER_ARTICLE]:
        if not isinstance(entry, dict):
            continue
        video_id = entry.get('video_id')
        cover_media_id = entry.get('cover_media_id')
        if not video_id or not cover_media_id or video_id in seen_video_ids:
            continue
        if not MediaFile.objects.filter(pk=cover_media_id).exists():
            continue
        seen_video_ids.add(video_id)
        covers.append(NewsVideoCover(news=article, video_id=video_id, cover_image_id=cover_media_id))

    article.video_covers.all().delete()
    if covers:
        NewsVideoCover.objects.bulk_create(covers)
