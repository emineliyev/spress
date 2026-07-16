/**
 * Article page — print button (share/print icons in templates/news/detail.html).
 */
(function () {
    'use strict';

    document.addEventListener('click', function (event) {
        if (event.target.closest('[data-action="print"]')) {
            window.print();
        }
    });
})();
