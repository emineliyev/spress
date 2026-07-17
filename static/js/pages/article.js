/**
 * Article page — print button (share/print icons in templates/news/detail.html)
 * and the optional YouTube cover facade (Phase 24).
 *
 * A video with a custom cover (apps.news.models.NewsVideoCover, surfaced
 * here via `templates/news/detail.html`'s `{{ video_covers|json_script }}`)
 * gets its iframe swapped for a clickable image facade on load; clicking
 * it lazily creates the real iframe — the video never starts loading
 * until the reader actually asks for it. A video with no matching cover
 * is left completely untouched (direct iframe, as before Phase 24).
 */
(function () {
    'use strict';

    document.addEventListener('click', function (event) {
        if (event.target.closest('[data-action="print"]')) {
            window.print();
        }
    });

    function extractVideoId(src) {
        var match = /\/embed\/([\w-]+)/.exec(src || '');
        return match ? match[1] : null;
    }

    function createFacade(wrapper, iframe, coverUrl) {
        var iframeAttrs = {
            src: iframe.getAttribute('src'),
            allow: iframe.getAttribute('allow'),
            referrerpolicy: iframe.getAttribute('referrerpolicy'),
            loading: iframe.getAttribute('loading'),
            allowfullscreen: iframe.hasAttribute('allowfullscreen'),
        };

        var facade = document.createElement('button');
        facade.type = 'button';
        facade.className = 'media-embed__facade';
        facade.style.backgroundImage = 'url(' + coverUrl + ')';
        facade.setAttribute('aria-label', 'Videonu yüklə və oynat');
        facade.innerHTML = '<i class="bi bi-play-circle-fill" aria-hidden="true"></i>';

        facade.addEventListener('click', function () {
            var realIframe = document.createElement('iframe');
            realIframe.setAttribute('src', iframeAttrs.src);
            if (iframeAttrs.allow) {
                realIframe.setAttribute('allow', iframeAttrs.allow);
            }
            if (iframeAttrs.referrerpolicy) {
                realIframe.setAttribute('referrerpolicy', iframeAttrs.referrerpolicy);
            }
            if (iframeAttrs.loading) {
                realIframe.setAttribute('loading', iframeAttrs.loading);
            }
            if (iframeAttrs.allowfullscreen) {
                realIframe.setAttribute('allowfullscreen', '');
            }
            wrapper.replaceChild(realIframe, facade);
        });

        wrapper.replaceChild(facade, iframe);
    }

    function initVideoFacades() {
        var dataEl = document.getElementById('video-covers-data');
        if (!dataEl) {
            return;
        }

        var covers;
        try {
            covers = JSON.parse(dataEl.textContent);
        } catch (error) {
            return;
        }
        if (!covers || !Object.keys(covers).length) {
            return;
        }

        document.querySelectorAll('.rich-text-content .media-embed--youtube').forEach(function (wrapper) {
            var iframe = wrapper.querySelector('iframe[src]');
            var videoId = iframe ? extractVideoId(iframe.getAttribute('src')) : null;
            var coverUrl = videoId ? covers[videoId] : null;
            if (iframe && coverUrl) {
                createFacade(wrapper, iframe, coverUrl);
            }
        });
    }

    document.addEventListener('DOMContentLoaded', initVideoFacades);
})();
