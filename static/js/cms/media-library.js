/**
 * Media Library page (templates/cms/media_list.html): dropzone upload,
 * per-card "Əvəz et" (replace), and the inline "Yeni qovluq" form toggle.
 * Filtering/search/pagination stay plain GET links (server-rendered), so
 * this file only wires the pieces that need JS.
 */
(function () {
    'use strict';

    function initDropzone(uploader) {
        var dropzone = document.querySelector('[data-role="dropzone"]');
        var chooseButton = document.querySelector('[data-action="choose-file"]');
        var fileInput = document.getElementById('media-upload-input');
        if (!dropzone || !fileInput) {
            return;
        }

        var currentFolder = new URLSearchParams(window.location.search).get('folder') || null;

        function upload(file) {
            uploader.uploadFile(file, { folderId: currentFolder });
        }

        chooseButton.addEventListener('click', function () {
            fileInput.click();
        });
        fileInput.addEventListener('change', function () {
            if (fileInput.files[0]) {
                upload(fileInput.files[0]);
            }
            fileInput.value = '';
        });

        ['dragenter', 'dragover'].forEach(function (eventName) {
            dropzone.addEventListener(eventName, function (event) {
                event.preventDefault();
                dropzone.classList.add('is-dragover');
            });
        });
        ['dragleave', 'drop'].forEach(function (eventName) {
            dropzone.addEventListener(eventName, function (event) {
                event.preventDefault();
                dropzone.classList.remove('is-dragover');
            });
        });
        dropzone.addEventListener('drop', function (event) {
            var file = event.dataTransfer.files[0];
            if (file) {
                upload(file);
            }
        });
    }

    function initReplace(uploader) {
        var replaceInput = document.getElementById('media-replace-input');
        if (!replaceInput) {
            return;
        }

        var pendingReplaceId = null;

        document.addEventListener('click', function (event) {
            var trigger = event.target.closest('[data-action="replace-media"]');
            if (!trigger) {
                return;
            }
            pendingReplaceId = trigger.dataset.mediaId;
            replaceInput.click();
        });

        replaceInput.addEventListener('change', function () {
            if (replaceInput.files[0] && pendingReplaceId) {
                uploader.uploadFile(replaceInput.files[0], { replaceId: pendingReplaceId });
            }
            replaceInput.value = '';
        });
    }

    function initFolderForm() {
        var toggle = document.querySelector('[data-action="open-folder-form"]');
        var form = document.querySelector('[data-role="folder-form"]');
        if (!toggle || !form) {
            return;
        }
        toggle.addEventListener('click', function () {
            form.hidden = !form.hidden;
            if (!form.hidden) {
                form.querySelector('input[name="name"]').focus();
            }
        });
    }

    function initFolderRename() {
        document.querySelectorAll('[data-action="rename-folder"]').forEach(function (button) {
            button.addEventListener('click', function () {
                var row = button.closest('.media-folders__row');
                var form = row.nextElementSibling;
                row.hidden = true;
                form.hidden = false;
                var input = form.querySelector('input[name="name"]');
                input.focus();
                input.select();
            });
        });
        document.querySelectorAll('[data-action="cancel-rename"]').forEach(function (button) {
            button.addEventListener('click', function () {
                var form = button.closest('.media-folders__rename-form');
                form.hidden = true;
                form.previousElementSibling.hidden = false;
            });
        });
    }

    document.addEventListener('DOMContentLoaded', function () {
        if (!window.MediaUploader) {
            return;
        }

        var uploader = new window.MediaUploader({
            defaultRatio: NaN,
            onComplete: function () {
                window.location.reload();
            },
            onError: function (message) {
                if (window.showToast) {
                    window.showToast(message, 'error');
                }
            },
        });

        initDropzone(uploader);
        initReplace(uploader);
        initFolderForm();
        initFolderRename();
    });
})();
