/**
 * Toggles the header search panel (components/search_form.html).
 * Actual search logic runs entirely in Django (CLAUDE.md ch.8 "Search").
 */
(function () {
    'use strict';

    document.addEventListener('DOMContentLoaded', function () {
        var toggle = document.querySelector('[data-action="toggle-search"]');
        var panel = document.getElementById('header-search-form');
        if (!toggle || !panel) {
            return;
        }

        toggle.addEventListener('click', function () {
            var willOpen = panel.hidden;
            panel.hidden = !willOpen;
            toggle.setAttribute('aria-expanded', String(willOpen));
            if (willOpen) {
                var input = panel.querySelector('input[name="q"]');
                if (input) {
                    input.focus();
                }
            }
        });
    });
})();
