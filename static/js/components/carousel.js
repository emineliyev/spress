/**
 * Generic auto-advancing carousel — currently only the homepage hero
 * (templates/news/home.html), but driven entirely by data attributes so
 * any [data-component="carousel"] block gets the same behavior without
 * page-specific JS. No-ops when a block has fewer than 2 slides (the
 * template itself omits prev/next/dots in that case).
 */
(function () {
    'use strict';

    var AUTOPLAY_MS = 7000;

    function initCarousel(root) {
        var slides = root.querySelectorAll('[data-carousel-slide]');
        if (slides.length < 2) {
            return;
        }

        var dots = root.querySelectorAll('[data-carousel-dot]');
        var prevButton = root.querySelector('[data-carousel-prev]');
        var nextButton = root.querySelector('[data-carousel-next]');
        var current = 0;
        var timer = null;

        function goTo(index) {
            current = (index + slides.length) % slides.length;

            slides.forEach(function (slide, i) {
                var isActive = i === current;
                slide.classList.toggle('is-active', isActive);
                slide.setAttribute('aria-hidden', String(!isActive));
                slide.querySelectorAll('a').forEach(function (link) {
                    link.tabIndex = isActive ? 0 : -1;
                });
            });

            dots.forEach(function (dot, i) {
                dot.classList.toggle('is-active', i === current);
            });
        }

        function restartAutoplay() {
            if (timer) {
                clearInterval(timer);
            }
            timer = setInterval(function () {
                goTo(current + 1);
            }, AUTOPLAY_MS);
        }

        if (prevButton) {
            prevButton.addEventListener('click', function () {
                goTo(current - 1);
                restartAutoplay();
            });
        }

        if (nextButton) {
            nextButton.addEventListener('click', function () {
                goTo(current + 1);
                restartAutoplay();
            });
        }

        dots.forEach(function (dot, i) {
            dot.addEventListener('click', function () {
                goTo(i);
                restartAutoplay();
            });
        });

        root.addEventListener('mouseenter', function () {
            clearInterval(timer);
        });
        root.addEventListener('mouseleave', restartAutoplay);

        goTo(0);
        restartAutoplay();
    }

    document.addEventListener('DOMContentLoaded', function () {
        document.querySelectorAll('[data-component="carousel"]').forEach(initCarousel);
    });
})();
