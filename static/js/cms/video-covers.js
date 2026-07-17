/**
 * "Video örtükləri" sidebar (templates/cms/news_form.html) — lets an
 * editor optionally attach a custom cover image to any YouTube video
 * embedded in the article body (apps.news.models.NewsVideoCover).
 *
 * Reads live from the CKEditor5 instance itself (`editor.getData()`,
 * obtained via django_ckeditor_5's own `window.ckeditorRegisterCallback`
 * hook) rather than scraping the editing-view DOM — the editor element
 * is created asynchronously, well after DOMContentLoaded, so this is the
 * only timing-safe way to know when it exists and to read its content.
 * Picker rows reuse the exact same `[data-role="image-picker"]` markup
 * and shared media-picker modal as the featured/OG image pickers
 * (static/js/cms/image-pickers.js's `window.registerImagePicker`), so no
 * picker logic is duplicated here.
 */
(function () {
    'use strict';

    var SYNC_DEBOUNCE_MS = 500;
    var EDITOR_ELEMENT_ID = 'id_content';

    function extractVideoIds(html) {
        var ids = [];
        var regex = /<iframe[^>]+src="[^"]*\/embed\/([\w-]+)/g;
        var match;
        while ((match = regex.exec(html))) {
            if (ids.indexOf(match[1]) === -1) {
                ids.push(match[1]);
            }
        }
        return ids;
    }

    function buildRow(videoId, mediaId, thumbnailUrl) {
        var row = document.createElement('div');
        row.className = 'editor__video-cover-row';
        row.dataset.videoId = videoId;
        row.innerHTML =
            '<p class="editor__video-cover-label">YouTube video: ' + videoId + '</p>' +
            '<div class="media-picker" data-role="image-picker" data-aspect-ratio="1.7777777778">' +
                '<input type="hidden" data-role="picker-input" value="' + (mediaId || '') + '">' +
                '<div class="media-picker__preview" data-role="picker-preview"' + (mediaId ? '' : ' hidden') + '>' +
                    '<img src="' + (thumbnailUrl || '') + '" alt="" class="editor__cover-preview" data-role="picker-preview-image">' +
                    '<button type="button" class="media-picker__remove" data-action="remove-image" aria-label="Örtüyü sil">' +
                        '<i class="bi bi-x-lg" aria-hidden="true"></i>' +
                    '</button>' +
                '</div>' +
                '<button type="button" class="media-picker__choose" data-action="choose-image"' + (mediaId ? ' hidden' : '') + '>' +
                    '<i class="bi bi-image" aria-hidden="true"></i> Örtük seçin' +
                '</button>' +
            '</div>';
        return row;
    }

    function readExistingCovers() {
        var covers = {};
        document.querySelectorAll('[data-role="existing-video-cover"]').forEach(function (el) {
            covers[el.dataset.videoId] = {
                mediaId: el.dataset.mediaId,
                thumbnailUrl: el.dataset.thumbnailUrl,
            };
        });
        return covers;
    }

    function initVideoCovers(editor) {
        var section = document.querySelector('[data-role="video-covers-section"]');
        var list = document.querySelector('[data-role="video-covers-list"]');
        var hiddenInput = document.querySelector('[data-role="video-covers-input"]');
        var form = hiddenInput ? hiddenInput.closest('form') : null;
        if (!section || !list || !hiddenInput || !form) {
            return;
        }

        var existingCovers = readExistingCovers();
        var knownVideoIds = [];

        function syncVideos() {
            var foundIds = extractVideoIds(editor.getData());

            knownVideoIds.slice().forEach(function (videoId) {
                if (foundIds.indexOf(videoId) === -1) {
                    var row = list.querySelector('[data-video-id="' + videoId + '"]');
                    if (row) {
                        row.remove();
                    }
                    knownVideoIds.splice(knownVideoIds.indexOf(videoId), 1);
                }
            });

            foundIds.forEach(function (videoId) {
                if (knownVideoIds.indexOf(videoId) !== -1) {
                    return;
                }
                var existing = existingCovers[videoId];
                var row = buildRow(videoId, existing ? existing.mediaId : '', existing ? existing.thumbnailUrl : '');
                list.appendChild(row);
                if (window.registerImagePicker) {
                    window.registerImagePicker(row.querySelector('[data-role="image-picker"]'));
                }
                knownVideoIds.push(videoId);
            });

            section.hidden = knownVideoIds.length === 0;
        }

        var debounceTimer;
        editor.model.document.on('change:data', function () {
            window.clearTimeout(debounceTimer);
            debounceTimer = window.setTimeout(syncVideos, SYNC_DEBOUNCE_MS);
        });
        syncVideos();

        form.addEventListener('submit', function () {
            var entries = knownVideoIds.map(function (videoId) {
                var row = list.querySelector('[data-video-id="' + videoId + '"]');
                var input = row ? row.querySelector('[data-role="picker-input"]') : null;
                return { video_id: videoId, cover_media_id: input ? input.value : '' };
            }).filter(function (entry) {
                return entry.cover_media_id;
            });
            hiddenInput.value = JSON.stringify(entries);
        }, true);
    }

    if (window.ckeditorRegisterCallback) {
        window.ckeditorRegisterCallback(EDITOR_ELEMENT_ID, initVideoCovers);
    }
})();
