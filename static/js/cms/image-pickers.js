/**
 * Generic multi-picker image chooser, shared by any CMS page with one or
 * more `[data-role="image-picker"]` blocks (Site Settings' logo+favicon,
 * News/Page's featured/OG image, Reklam's banner).
 *
 * "Şəkil seçin" opens the shared `#media-picker-modal`
 * (templates/cms/partials/media_picker_modal.html) instead of going
 * straight to the OS file dialog — its "Kitabxanadan seç" tab lets an
 * editor reuse an already-uploaded MediaFile without a fresh upload;
 * "Yeni yüklə" runs the exact same stage→crop→confirm pipeline as
 * before. One shared `MediaUploader` instance (not one per picker —
 * see media-uploader.js) has its `onComplete`/`defaultRatio`
 * reassigned to the *currently open* picker's state right before each
 * upload, the same "singleton, rebind before use" approach the crop
 * modal itself already relies on.
 */
(function () {
    'use strict';

    function initImagePickers() {
        var pickers = document.querySelectorAll('[data-role="image-picker"]');
        var modal = document.getElementById('media-picker-modal');
        if (!pickers.length || !modal || !window.MediaUploader) {
            return;
        }

        var uploader = new window.MediaUploader({
            onError: function (message) {
                if (window.showToast) {
                    window.showToast(message, 'error');
                }
            },
        });

        var pickerUrl = modal.dataset.pickerUrl;
        var grid = modal.querySelector('[data-role="picker-grid"]');
        var searchInput = modal.querySelector('[data-role="picker-search"]');
        var formatSelect = modal.querySelector('[data-role="picker-format-filter"]');
        var tabs = modal.querySelectorAll('[data-role="picker-tab"]');
        var panels = modal.querySelectorAll('[data-role="picker-panel"]');
        var sharedFileInput = modal.querySelector('[data-role="picker-shared-file-input"]');
        var uploadTriggerButton = modal.querySelector('[data-action="picker-trigger-upload"]');

        var currentPicker = null;

        function fetchGrid(queryString) {
            grid.setAttribute('aria-busy', 'true');
            fetch(pickerUrl + (queryString || ''))
                .then(function (response) {
                    return response.text();
                })
                .then(function (html) {
                    grid.innerHTML = html;
                })
                .finally(function () {
                    grid.removeAttribute('aria-busy');
                });
        }

        function currentFilterQueryString() {
            var params = new URLSearchParams();
            if (searchInput.value.trim()) {
                params.set('q', searchInput.value.trim());
            }
            if (formatSelect.value) {
                params.set('format', formatSelect.value);
            }
            var query = params.toString();
            return query ? '?' + query : '';
        }

        function switchTab(panelName) {
            tabs.forEach(function (tab) {
                tab.classList.toggle('is-active', tab.dataset.panel === panelName);
            });
            panels.forEach(function (panel) {
                panel.hidden = panel.dataset.panel !== panelName;
            });
        }

        function openModal(picker) {
            currentPicker = picker;
            switchTab('library');
            searchInput.value = '';
            formatSelect.value = '';
            fetchGrid('');
            modal.hidden = false;
            document.body.classList.add('media-picker-modal-open');
        }

        function closeModal() {
            modal.hidden = true;
            document.body.classList.remove('media-picker-modal-open');
        }

        function selectMedia(mediaId, thumbnailUrl) {
            if (!currentPicker) {
                return;
            }
            currentPicker.hiddenInput.value = mediaId;
            currentPicker.previewImage.src = thumbnailUrl;
            currentPicker.preview.hidden = false;
            currentPicker.chooseButton.hidden = true;
            closeModal();
        }

        function registerPicker(pickerEl) {
            var picker = {
                hiddenInput: pickerEl.querySelector('[data-role="picker-input"]'),
                chooseButton: pickerEl.querySelector('[data-action="choose-image"]'),
                removeButton: pickerEl.querySelector('[data-action="remove-image"]'),
                preview: pickerEl.querySelector('[data-role="picker-preview"]'),
                previewImage: pickerEl.querySelector('[data-role="picker-preview-image"]'),
                ratio: parseFloat(pickerEl.dataset.aspectRatio),
            };

            picker.chooseButton.addEventListener('click', function () {
                openModal(picker);
            });

            picker.removeButton.addEventListener('click', function () {
                picker.hiddenInput.value = '';
                picker.preview.hidden = true;
                picker.chooseButton.hidden = false;
            });
        }

        pickers.forEach(registerPicker);

        // Lets other modules (e.g. video-covers.js, which adds picker
        // blocks dynamically as videos are found in the editor content)
        // wire freshly-created `[data-role="image-picker"]` blocks into
        // this same shared modal/uploader without duplicating any of the
        // logic above.
        window.registerImagePicker = registerPicker;

        // "Kitabxanadan seç" — card clicks, search, format filter, pagination.
        grid.addEventListener('click', function (event) {
            var card = event.target.closest('[data-action="pick-media"]');
            if (card) {
                selectMedia(card.dataset.mediaId, card.dataset.thumbnailUrl);
                return;
            }
            var pageLink = event.target.closest('.pagination a');
            if (pageLink) {
                event.preventDefault();
                fetchGrid(pageLink.getAttribute('href'));
            }
        });

        var searchDebounce;
        searchInput.addEventListener('input', function () {
            window.clearTimeout(searchDebounce);
            searchDebounce = window.setTimeout(function () {
                fetchGrid(currentFilterQueryString());
            }, 300);
        });
        formatSelect.addEventListener('change', function () {
            fetchGrid(currentFilterQueryString());
        });

        // "Yeni yüklə" — unchanged upload→crop→confirm pipeline, just
        // triggered from inside the modal instead of directly.
        tabs.forEach(function (tab) {
            tab.addEventListener('click', function () {
                switchTab(tab.dataset.panel);
            });
        });
        uploadTriggerButton.addEventListener('click', function () {
            sharedFileInput.click();
        });
        sharedFileInput.addEventListener('change', function () {
            var file = sharedFileInput.files[0];
            sharedFileInput.value = '';
            if (!file || !currentPicker) {
                return;
            }
            var picker = currentPicker;
            closeModal();
            uploader.defaultRatio = picker.ratio;
            uploader.onComplete = function (mediaFile) {
                picker.hiddenInput.value = mediaFile.id;
                picker.previewImage.src = mediaFile.thumbnail_url;
                picker.preview.hidden = false;
                picker.chooseButton.hidden = true;
            };
            uploader.uploadFile(file);
        });

        modal.querySelectorAll('[data-action="close-picker-modal"]').forEach(function (el) {
            el.addEventListener('click', closeModal);
        });
        document.addEventListener('keydown', function (event) {
            if (event.key === 'Escape' && !modal.hidden) {
                closeModal();
            }
        });
    }

    document.addEventListener('DOMContentLoaded', function () {
        initImagePickers();
    });
})();
