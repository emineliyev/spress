/**
 * Mobile off-canvas navigation toggle.
 */
(function () {
    'use strict';

    document.addEventListener('DOMContentLoaded', function () {
        var toggle = document.querySelector('[data-action="toggle-menu"]');
        var nav = document.getElementById('primary-navigation');
        if (!toggle || !nav) {
            return;
        }

        toggle.addEventListener('click', function () {
            var isOpen = nav.classList.toggle('is-open');
            toggle.setAttribute('aria-expanded', String(isOpen));
        });

        document.addEventListener('click', function (event) {
            if (!nav.classList.contains('is-open')) {
                return;
            }
            if (nav.contains(event.target) || toggle.contains(event.target)) {
                return;
            }
            nav.classList.remove('is-open');
            toggle.setAttribute('aria-expanded', 'false');
        });
    });
})();
