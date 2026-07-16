/**
 * Reusable upload -> stage -> crop -> confirm widget on top of Cropper.js.
 * Shared by the Media Library page (static/js/cms/media-library.js) and
 * the News editor's cover-image picker (static/js/cms/editor.js) so the
 * pipeline lives in one place (CLAUDE.md ch.8 "Component Initialization").
 *
 * Requires templates/cms/partials/media_crop_modal.html to be included on
 * the page, and Cropper.js (static/vendors/cropperjs/) loaded first.
 */
(function () {
    'use strict';

    function getCsrfToken() {
        var match = document.cookie.match(/(?:^|; )csrftoken=([^;]*)/);
        return match ? decodeURIComponent(match[1]) : '';
    }

    function postForm(url, formData) {
        return fetch(url, {
            method: 'POST',
            headers: { 'X-CSRFToken': getCsrfToken() },
            body: formData,
        }).then(function (response) {
            return response.json().then(function (data) {
                return { ok: response.ok, data: data };
            });
        });
    }

    function MediaUploader(options) {
        options = options || {};
        this.onComplete = options.onComplete || function () {};
        this.onError = options.onError || function () {};
        this.defaultRatio = options.defaultRatio;

        this.modal = document.getElementById('media-crop-modal');
        this.image = document.getElementById('media-crop-image');
        this.altInput = document.getElementById('media-crop-alt');
        this.captionInput = document.getElementById('media-crop-caption');

        if (!this.modal || !this.image) {
            return;
        }

        // URLs live on the shared modal markup (templates/cms/partials/
        // media_crop_modal.html) rather than being duplicated as JS
        // string literals per page (CLAUDE.md ch.8 "Data Attributes").
        this.stageUrl = options.stageUrl || this.modal.dataset.stageUrl;
        this.confirmUrl = options.confirmUrl || this.modal.dataset.confirmUrl;

        this.errorEl = this.modal.querySelector('[data-role="crop-error"]');
        this.applyButton = this.modal.querySelector('[data-role="apply-crop"]');
        this.aspectButtons = this.modal.querySelectorAll('[data-role="aspect-buttons"] .media-crop-modal__aspect');

        this.cropper = null;
        this.tempId = null;
        this.replaceId = null;
        this.folderId = null;

        this._bindStaticEvents();
    }

    MediaUploader.prototype._bindStaticEvents = function () {
        var self = this;

        this.modal.querySelectorAll('[data-action="close-crop-modal"]').forEach(function (el) {
            el.addEventListener('click', function () {
                self.close();
            });
        });

        document.addEventListener('keydown', function (event) {
            if (event.key === 'Escape' && !self.modal.hidden) {
                self.close();
            }
        });

        this.aspectButtons.forEach(function (button) {
            button.addEventListener('click', function () {
                self.aspectButtons.forEach(function (b) {
                    b.classList.remove('is-active');
                });
                button.classList.add('is-active');
                if (self.cropper) {
                    self.cropper.setAspectRatio(parseFloat(button.dataset.ratio));
                }
            });
        });

        this.applyButton.addEventListener('click', function () {
            self._confirm();
        });
    };

    /**
     * @param {File} file
     * @param {{replaceId?: string|number, folderId?: string|number}} [options]
     */
    MediaUploader.prototype.uploadFile = function (file, options) {
        options = options || {};
        this.replaceId = options.replaceId || null;
        this.folderId = options.folderId || null;
        this._clearError();

        var self = this;
        var formData = new FormData();
        formData.append('file', file);

        return postForm(this.stageUrl, formData).then(function (result) {
            if (!result.ok) {
                throw new Error(result.data.error || 'Yükləmə uğursuz oldu.');
            }
            self.tempId = result.data.temp_id;
            if (result.data.is_svg) {
                return self._confirm();
            }
            self._openCropper(result.data.url);
            return undefined;
        }).catch(function (error) {
            self.onError(error.message);
        });
    };

    MediaUploader.prototype._openCropper = function (imageUrl) {
        var self = this;

        if (this.cropper) {
            this.cropper.destroy();
            this.cropper = null;
        }

        var ratio = this.defaultRatio;
        this.aspectButtons.forEach(function (button) {
            var buttonRatio = parseFloat(button.dataset.ratio);
            var matches = buttonRatio === ratio || (Number.isNaN(buttonRatio) && Number.isNaN(ratio));
            button.classList.toggle('is-active', matches);
        });

        this.image.onload = function () {
            self.cropper = new Cropper(self.image, {
                aspectRatio: ratio,
                viewMode: 1,
                autoCropArea: 0.9,
                responsive: true,
                background: false,
            });
        };
        this.image.src = imageUrl;

        this.modal.hidden = false;
        document.body.classList.add('media-crop-modal-open');
    };

    MediaUploader.prototype.close = function () {
        this.modal.hidden = true;
        document.body.classList.remove('media-crop-modal-open');
        if (this.cropper) {
            this.cropper.destroy();
            this.cropper = null;
        }
        this.tempId = null;
        this.replaceId = null;
        this.folderId = null;
        this.altInput.value = '';
        this.captionInput.value = '';
        this._clearError();
    };

    MediaUploader.prototype._confirm = function () {
        if (!this.tempId) {
            return undefined;
        }

        var formData = new FormData();
        formData.append('temp_id', this.tempId);
        if (this.cropper) {
            var box = this.cropper.getData(true);
            formData.append('x', box.x);
            formData.append('y', box.y);
            formData.append('width', box.width);
            formData.append('height', box.height);
        }
        if (this.folderId) {
            formData.append('folder', this.folderId);
        }
        if (this.replaceId) {
            formData.append('replace', this.replaceId);
        }
        formData.append('alt_text', this.altInput.value.trim());
        formData.append('caption', this.captionInput.value.trim());

        var self = this;
        this.applyButton.disabled = true;

        return postForm(this.confirmUrl, formData).then(function (result) {
            self.applyButton.disabled = false;
            if (!result.ok) {
                throw new Error(result.data.error || 'Əməliyyat uğursuz oldu.');
            }
            self.close();
            self.onComplete(result.data);
        }).catch(function (error) {
            self.applyButton.disabled = false;
            self._notifyError(error.message);
        });
    };

    MediaUploader.prototype._notifyError = function (message) {
        if (this.modal.hidden) {
            // Crop panel never opened (e.g. an SVG that skipped cropping) —
            // there's no visible surface for `errorEl`, so fall back to the
            // page-level error callback instead of writing to a hidden node.
            this.onError(message);
            return;
        }
        if (this.errorEl) {
            this.errorEl.textContent = message;
            this.errorEl.hidden = false;
        }
    };

    MediaUploader.prototype._clearError = function () {
        if (this.errorEl) {
            this.errorEl.hidden = true;
            this.errorEl.textContent = '';
        }
    };

    window.MediaUploader = MediaUploader;
})();
