/**
 * News editor (templates/cms/news_form.html):
 *  - suggests a slug from the title while the slug field hasn't been
 *    touched by hand (server-side apps.core.utils.az_slugify remains the
 *    authoritative source — this is only a live preview);
 *  - turns the plain <select multiple> tags field into clickable pills,
 *    with the native select as the always-present fallback control.
 *
 * Image pickers (featured_image, og_image) are handled by the shared
 * static/js/cms/image-pickers.js, not here.
 */
(function () {
    'use strict';

    var AZ_MAP = { 'ə': 'e', 'ğ': 'g', 'ı': 'i', 'ö': 'o', 'ü': 'u', 'ş': 's', 'ç': 'c' };

    function slugify(value) {
        return value
            .toLowerCase()
            .replace(/[əğışöüç]/g, function (ch) { return AZ_MAP[ch]; })
            .replace(/[^a-z0-9]+/g, '-')
            .replace(/^-+|-+$/g, '');
    }

    function initSlugSuggestion() {
        var titleInput = document.querySelector('[data-role="title-input"]');
        var slugInput = document.querySelector('[data-role="slug-input"]');
        if (!titleInput || !slugInput) {
            return;
        }

        var slugTouched = slugInput.value.trim().length > 0;
        slugInput.addEventListener('input', function () {
            slugTouched = true;
        });
        titleInput.addEventListener('input', function () {
            if (!slugTouched) {
                slugInput.value = slugify(titleInput.value);
            }
        });
    }

    function initTagPicker() {
        var select = document.querySelector('[data-role="tag-input"]');
        if (!select) {
            return;
        }

        var picker = document.createElement('div');
        picker.className = 'tag-picker';
        select.insertAdjacentElement('afterend', picker);
        select.classList.add('visually-hidden');

        function render() {
            picker.innerHTML = '';
            Array.prototype.forEach.call(select.options, function (option) {
                var pill = document.createElement('button');
                pill.type = 'button';
                pill.className = 'tag-picker__pill' + (option.selected ? ' is-selected' : '');
                pill.textContent = option.textContent.trim();
                pill.addEventListener('click', function () {
                    option.selected = !option.selected;
                    render();
                });
                picker.appendChild(pill);
            });
        }

        render();
    }

    document.addEventListener('DOMContentLoaded', function () {
        initSlugSuggestion();
        initTagPicker();
    });
})();
