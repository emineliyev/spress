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
    return '<div class="media-embed media-embed--youtube">' +
        '<iframe src="https://www.youtube-nocookie.com/embed/' + videoId + '" ' +
        'allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" ' +
        'allowfullscreen loading="lazy"></iframe></div>';
};
