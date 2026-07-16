/**
 * CMS off-canvas sidebar toggle (templates/cms/base.html) — collapsible
 * on tablet/mobile, permanently visible on desktop (CLAUDE.md ch.9).
 * Same interaction pattern as the public site's mobile nav
 * (static/js/components/menu.js): toggle button + `is-open` class +
 * close on outside click.
 */
(function () {
    'use strict';

    document.addEventListener('DOMContentLoaded', function () {
        var toggle = document.querySelector('[data-action="toggle-sidebar"]');
        var sidebar = document.getElementById('cms-sidebar');
        var backdrop = document.querySelector('[data-action="close-sidebar"]');
        if (!toggle || !sidebar || !backdrop) {
            return;
        }

        function close() {
            sidebar.classList.remove('is-open');
            backdrop.classList.remove('is-open');
            toggle.setAttribute('aria-expanded', 'false');
        }

        toggle.addEventListener('click', function () {
            var isOpen = sidebar.classList.toggle('is-open');
            backdrop.classList.toggle('is-open', isOpen);
            toggle.setAttribute('aria-expanded', String(isOpen));
        });

        backdrop.addEventListener('click', close);

        document.addEventListener('keydown', function (event) {
            if (event.key === 'Escape' && sidebar.classList.contains('is-open')) {
                close();
            }
        });
    });
})();
