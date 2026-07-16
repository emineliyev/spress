/**
 * Generic multi-picker image uploader, shared by any CMS page with one or
 * more `[data-role="image-picker"]` blocks (Site Settings' logo+favicon,
 * News/Page's featured/OG image, Reklam's banner). A second
 * `new MediaUploader(...)` per picker would double-bind click handlers
 * onto the same singleton `#media-crop-modal` DOM (see
 * templates/cms/partials/media_crop_modal.html) — instead this uses a
 * single shared instance and reassigns `onComplete`/`defaultRatio` right
 * before each `uploadFile()` call, since MediaUploader reads those off
 * `this` at the moment it needs them, not once at construction.
 *
 * Originally written for Site Settings alone (hence prior filename
 * settings.js) — renamed once a third and fourth page started reusing it,
 * since nothing about it is Settings-specific.
 */
(function () {
    'use strict';

    function initImagePickers() {
        var pickers = document.querySelectorAll('[data-role="image-picker"]');
        if (!pickers.length || !window.MediaUploader) {
            return;
        }

        var uploader = new window.MediaUploader({
            onError: function (message) {
                if (window.showToast) {
                    window.showToast(message, 'error');
                }
            },
        });

        pickers.forEach(function (picker) {
            var hiddenInput = picker.querySelector('[data-role="picker-input"]');
            var chooseButton = picker.querySelector('[data-action="choose-image"]');
            var removeButton = picker.querySelector('[data-action="remove-image"]');
            var fileInput = picker.querySelector('[data-role="picker-file-input"]');
            var preview = picker.querySelector('[data-role="picker-preview"]');
            var previewImage = picker.querySelector('[data-role="picker-preview-image"]');
            var ratio = parseFloat(picker.dataset.aspectRatio);

            chooseButton.addEventListener('click', function () {
                fileInput.click();
            });

            fileInput.addEventListener('change', function () {
                if (fileInput.files[0]) {
                    uploader.defaultRatio = ratio;
                    uploader.onComplete = function (mediaFile) {
                        hiddenInput.value = mediaFile.id;
                        previewImage.src = mediaFile.thumbnail_url;
                        preview.hidden = false;
                        chooseButton.hidden = true;
                    };
                    uploader.uploadFile(fileInput.files[0]);
                }
                fileInput.value = '';
            });

            removeButton.addEventListener('click', function () {
                hiddenInput.value = '';
                preview.hidden = true;
                chooseButton.hidden = false;
            });
        });
    }

    document.addEventListener('DOMContentLoaded', function () {
        initImagePickers();
    });
})();
