/**
 * Breaking-news ticker on the homepage — sets the marquee's scroll speed
 * from the server-computed duration (static/css/layout/header.css scrolls
 * at a fixed default otherwise). Pausing on hover is handled purely in CSS
 * (`.breaking-ticker:hover .breaking-ticker__track`), so this only ever
 * touches `animation-duration`, never play/pause state.
 */
(function () {
    'use strict';

    document.addEventListener('DOMContentLoaded', function () {
        var track = document.querySelector('.breaking-ticker__track');
        if (!track || !track.dataset.duration) {
            return;
        }

        track.style.animationDuration = track.dataset.duration + 's';
    });
})();
