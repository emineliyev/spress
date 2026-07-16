"""
Locust load test for the public site (docs/TESTING.md has the full
usage guide). Reader traffic only — no fixed slugs are hardcoded,
since whatever host this runs against (a local dev server, the
dedicated e2e database, a future staging box) will have different
content; each task discovers a real link from the page it just
loaded instead.

Never point this at a production host without the site owner's
explicit sign-off — even read-only traffic at load-test volume can
degrade a real, publicly-serving box.
"""

import os
import random
import re

from locust import HttpUser, between, task

# Optional — only set these when you want the smaller CMS-login slice of
# traffic included, and only ever against a host/account you control (this
# performs a real login on every task, once per CmsStaffUser wait cycle).
CMS_USERNAME = os.environ.get('LOCUST_CMS_USERNAME')
CMS_PASSWORD = os.environ.get('LOCUST_CMS_PASSWORD')

_LINK_RE = re.compile(r'href="(/[^"#?]+/)"')


def _pick_link(html, *, prefix):
    """Grabs a random same-site link starting with `prefix` out of a
    rendered page — e.g. `/category/` or `/news/` — so tasks always
    exercise a link the page actually rendered, not a guessed slug."""
    candidates = [href for href in _LINK_RE.findall(html) if href.startswith(prefix)]
    return random.choice(candidates) if candidates else None


class ReaderUser(HttpUser):
    """An anonymous visitor browsing the public site — the overwhelming
    majority of real traffic a news portal receives."""

    weight = 8
    wait_time = between(1, 4)

    @task(5)
    def home(self):
        self.client.get('/', name='/')

    @task(3)
    def category_page(self):
        home_response = self.client.get('/', name='/ (for category link)')
        link = _pick_link(home_response.text, prefix='/category/')
        if link:
            self.client.get(link, name='/category/<slug>/')

    @task(3)
    def article_page(self):
        home_response = self.client.get('/', name='/ (for article link)')
        link = _pick_link(home_response.text, prefix='/news/')
        if link:
            self.client.get(link, name='/news/<slug>/')

    @task(1)
    def search(self):
        self.client.get('/search/?q=xeber', name='/search/?q=...')


class CmsStaffUser(HttpUser):
    """A much smaller slice of traffic — editors working in the CMS
    while readers are browsing. Only runs its real-login task when
    LOCUST_CMS_USERNAME/LOCUST_CMS_PASSWORD are set (see module
    docstring); otherwise it just repeats the anonymous redirect, since
    logging in needs credentials for whatever host this points at."""

    weight = 1
    wait_time = between(5, 15)

    @task
    def dashboard(self):
        if not (CMS_USERNAME and CMS_PASSWORD):
            self.client.get('/cms/', name='/cms/ (anonymous, redirected to login)')
            return

        login_page = self.client.get('/accounts/login/', name='/accounts/login/ [GET]')
        csrf_token = self.client.cookies.get('csrftoken')
        self.client.post(
            '/accounts/login/',
            data={'username': CMS_USERNAME, 'password': CMS_PASSWORD, 'csrfmiddlewaretoken': csrf_token},
            name='/accounts/login/ [POST]',
        )
        self.client.get('/cms/', name='/cms/ (authenticated)')
