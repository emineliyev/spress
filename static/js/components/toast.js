/**
 * Renders Django messages (components/toast.html) as dismissible toasts.
 * Never uses browser alert() (CLAUDE.md ch.8 "Notifications").
 */
(function () {
    'use strict';

    var AUTO_DISMISS_MS = 5000;

    function iconClassFor(type) {
        switch (type) {
            case 'success':
                return 'bi-check-circle';
            case 'error':
                return 'bi-x-circle';
            case 'warning':
                return 'bi-exclamation-triangle';
            default:
                return 'bi-info-circle';
        }
    }

    function dismiss(toast) {
        toast.classList.remove('is-visible');
        window.setTimeout(function () {
            toast.remove();
        }, 300);
    }

    function createToast(message, type) {
        var container = document.getElementById('toast-container');
        if (!container) {
            return;
        }

        var toast = document.createElement('div');
        toast.className = 'toast toast--' + type;
        toast.setAttribute('role', 'status');

        var icon = document.createElement('i');
        icon.className = 'bi toast__icon ' + iconClassFor(type);
        icon.setAttribute('aria-hidden', 'true');

        var text = document.createElement('span');
        text.textContent = message;

        var close = document.createElement('button');
        close.type = 'button';
        close.className = 'toast__close';
        close.setAttribute('aria-label', 'Bağla');
        close.innerHTML = '<i class="bi bi-x" aria-hidden="true"></i>';
        close.addEventListener('click', function () {
            dismiss(toast);
        });

        toast.appendChild(icon);
        toast.appendChild(text);
        toast.appendChild(close);
        container.appendChild(toast);

        requestAnimationFrame(function () {
            toast.classList.add('is-visible');
        });
        window.setTimeout(function () {
            dismiss(toast);
        }, AUTO_DISMISS_MS);
    }

    document.addEventListener('DOMContentLoaded', function () {
        var source = document.querySelector('.toast-source');
        if (!source) {
            return;
        }

        source.querySelectorAll('li').forEach(function (item) {
            createToast(item.textContent.trim(), item.dataset.toastType || 'info');
        });
    });

    // Exposed so other modules can raise a toast for client-side events
    // (AJAX failures etc.) without ever falling back to alert() — CLAUDE.md
    // ch.8 "Notifications": "Never use browser alert()."
    window.showToast = createToast;
})();
