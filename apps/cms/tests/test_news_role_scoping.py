"""Jurnalist-specific News restrictions (apps.cms.views.news._scope_to_author,
apps.news.forms.NewsForm's status-choice narrowing): only their own
articles, and never straight to Published/Scheduled — everyone else who
can reach the News screens at all (Administrator, Baş redaktor, Redaktor)
can touch any article and publish freely.
"""

import pytest
from django.urls import reverse

from apps.news.models import News


@pytest.mark.django_db
def test_journalist_news_list_only_shows_their_own_articles(journalist_client, journalist, category, administrator):
    own = News.objects.create(
        title='Jurnalistin öz xəbəri', short_description='d', content='<p>c</p>',
        category=category, author=journalist,
    )
    News.objects.create(
        title='Başqasının xəbəri', short_description='d', content='<p>c</p>',
        category=category, author=administrator,
    )

    response = journalist_client.get(reverse('cms:news_list'))
    html = response.content.decode()

    assert own.title in html
    assert 'Başqasının xəbəri' not in html


@pytest.mark.django_db
def test_journalist_cannot_edit_someone_elses_article(journalist_client, category, administrator):
    other = News.objects.create(
        title='Başqasının xəbəri', short_description='d', content='<p>c</p>',
        category=category, author=administrator,
    )

    response = journalist_client.get(reverse('cms:news_edit', args=[other.pk]))

    assert response.status_code == 404


@pytest.mark.django_db
def test_journalist_can_edit_their_own_article(journalist_client, journalist, category):
    own = News.objects.create(
        title='Jurnalistin xəbəri', short_description='d', content='<p>c</p>',
        category=category, author=journalist,
    )

    response = journalist_client.post(reverse('cms:news_edit', args=[own.pk]), {
        'title': 'Yenilənmiş başlıq', 'short_description': 'd', 'content': '<p>c</p>',
        'category': category.pk, 'status': News.Status.DRAFT,
    })

    assert response.status_code == 302
    own.refresh_from_db()
    assert own.title == 'Yenilənmiş başlıq'


@pytest.mark.django_db
def test_journalist_cannot_publish_directly(journalist_client, category):
    response = journalist_client.post(reverse('cms:news_create'), {
        'title': 'Dərc cəhdi', 'short_description': 'd', 'content': '<p>c</p>',
        'category': category.pk, 'status': News.Status.PUBLISHED,
    })

    # Rejected by NewsForm's narrowed status choices — "That choice is not
    # one of the available choices", so the article is never created.
    assert response.status_code == 200
    assert not News.objects.filter(title='Dərc cəhdi').exists()


@pytest.mark.django_db
def test_journalist_can_save_as_draft_or_pending_review(journalist_client, category):
    response = journalist_client.post(reverse('cms:news_create'), {
        'title': 'Nəzərdən keçirilir üçün', 'short_description': 'd', 'content': '<p>c</p>',
        'category': category.pk, 'status': News.Status.PENDING_REVIEW,
    })

    assert response.status_code == 302
    article = News.objects.get(title='Nəzərdən keçirilir üçün')
    assert article.status == News.Status.PENDING_REVIEW


@pytest.mark.django_db
def test_editor_can_edit_and_publish_someone_elses_article(editor_client, editor, category, administrator):
    other = News.objects.create(
        title='Başqasının xəbəri', short_description='d', content='<p>c</p>',
        category=category, author=administrator,
    )

    response = editor_client.post(reverse('cms:news_edit', args=[other.pk]), {
        'title': 'Redaktor tərəfindən dərc edildi', 'short_description': 'd', 'content': '<p>c</p>',
        'category': category.pk, 'status': News.Status.PUBLISHED,
    })

    assert response.status_code == 302
    other.refresh_from_db()
    assert other.status == News.Status.PUBLISHED


@pytest.mark.django_db
def test_content_manager_cannot_reach_news_screens(content_manager_client, category):
    response = content_manager_client.get(reverse('cms:news_create'))
    assert response.status_code == 403


@pytest.mark.django_db
def test_journalist_bulk_publish_is_rejected(journalist_client, journalist, category):
    article = News.objects.create(
        title='Toplu dərc cəhdi', short_description='d', content='<p>c</p>',
        category=category, author=journalist, status=News.Status.DRAFT,
    )

    response = journalist_client.post(reverse('cms:news_bulk_action'), {
        'selected': [article.pk], 'bulk_action': 'publish',
    })

    assert response.status_code == 302
    article.refresh_from_db()
    assert article.status == News.Status.DRAFT


@pytest.mark.django_db
def test_journalist_bulk_delete_own_article_still_works(journalist_client, journalist, category):
    article = News.objects.create(
        title='Öz xəbərini toplu sil', short_description='d', content='<p>c</p>',
        category=category, author=journalist,
    )

    response = journalist_client.post(reverse('cms:news_bulk_action'), {
        'selected': [article.pk], 'bulk_action': 'delete',
    })

    assert response.status_code == 302
    article.refresh_from_db()
    assert article.is_deleted is True
