/**
 * Custom CKEditor5 mediaEmbed provider (config/settings/base.py's
 * CKEDITOR_5_CONFIGS.default.mediaEmbed.providers[0].html references this
 * as "callback:ckeditorYoutubeEmbedHtml") — django_ckeditor_5's widget
 * bootstrap (django_ckeditor_5/static/django_ckeditor_5/app.js) resolves
 * "callback:<name>" config strings to window[<name>] at editor-init time,
 * so this must load and assign the global before that init runs (see the
 * <script> ordering in templates/cms/news_form.html/page_form.html).
 *
 * Written by hand instead of using MediaEmbed's own default YouTube
 * provider so the saved markup is our own semantic wrapper (styled by
 * static/css/components/rich-text.css) instead of CKEditor's inline
 * `style="position:absolute;..."` output, which CLAUDE.md forbids.
 */
window.ckeditorYoutubeEmbedHtml = function (match) {
    'use strict';
    var videoId = match[1];
    // referrerpolicy is required, not cosmetic: SecurityMiddleware sends
    // `Referrer-Policy: same-origin` site-wide (CLAUDE.md ch.12), which
    // strips the referrer entirely on any cross-origin request — YouTube's
    // player can't validate the embed without one and fails with a
    // generic "Error 153 / player configuration error" instead of
    // actually loading, confirmed by reproducing it with and without this
    // attribute. `strict-origin-when-cross-origin` still only reveals this
    // site's origin (scheme+host, not the full page URL) to YouTube —
    // enough for the player to initialize without leaking the specific
    // article being read.
    return '<div class="media-embed media-embed--youtube">' +
        '<iframe src="https://www.youtube-nocookie.com/embed/' + videoId + '" ' +
        'allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" ' +
        'referrerpolicy="strict-origin-when-cross-origin" ' +
        'allowfullscreen loading="lazy"></iframe></div>';
};
