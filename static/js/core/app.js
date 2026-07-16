/**
 * App shell — closes any open overlay (mobile nav, header search) on Escape.
 * Component-specific behavior lives in its own module (CLAUDE.md ch.8
 * "Every component must initialize independently").
 */
(function () {
    'use strict';

    document.addEventListener('keydown', function (event) {
        if (event.key !== 'Escape') {
            return;
        }

        var openNav = document.querySelector('.nav.is-open');
        if (openNav) {
            openNav.classList.remove('is-open');
            var menuToggle = document.querySelector('[data-action="toggle-menu"]');
            if (menuToggle) {
                menuToggle.setAttribute('aria-expanded', 'false');
            }
        }

        var searchPanel = document.getElementById('header-search-form');
        if (searchPanel && !searchPanel.hidden) {
            searchPanel.hidden = true;
            var searchToggle = document.querySelector('[data-action="toggle-search"]');
            if (searchToggle) {
                searchToggle.setAttribute('aria-expanded', 'false');
            }
        }
    });
})();
