/**
 * Subcategory dropdown. Desktop uses CSS :hover/:focus-within
 * (components/dropdown.css) — this only handles the mobile off-canvas
 * case, where the first tap on a parent category reveals its
 * subcategories instead of navigating, and a second tap navigates.
 */
(function () {
    'use strict';

    var MOBILE_QUERY = '(max-width: 992px)';

    function isMobileNav() {
        return window.matchMedia(MOBILE_QUERY).matches;
    }

    document.addEventListener('DOMContentLoaded', function () {
        var items = document.querySelectorAll('.nav__item--has-dropdown');

        items.forEach(function (item) {
            var link = item.querySelector(':scope > .nav__link');
            if (!link) {
                return;
            }

            link.addEventListener('click', function (event) {
                if (!isMobileNav() || item.classList.contains('is-open')) {
                    return;
                }
                event.preventDefault();
                items.forEach(function (other) {
                    if (other !== item) {
                        other.classList.remove('is-open');
                    }
                });
                item.classList.add('is-open');
            });
        });
    });
})();
