/**
 * Category list (templates/cms/category_list.html): native HTML5
 * drag-and-drop reorder within a sibling group (top-level rows among
 * themselves; a parent's children among themselves — never across groups,
 * since that would silently re-parent a category, which this view doesn't
 * support). Row-menu toggling is handled by static/js/cms/news.js, already
 * generic enough (`data-action="toggle-row-menu"`) to reuse as-is here.
 */
(function () {
    'use strict';

    function getCsrfToken() {
        var match = document.cookie.match(/(?:^|; )csrftoken=([^;]*)/);
        return match ? decodeURIComponent(match[1]) : '';
    }

    function initDragReorder() {
        var table = document.querySelector('[data-role="category-table"]');
        if (!table) {
            return;
        }

        var reorderUrl = table.dataset.reorderUrl;
        var tbody = table.querySelector('tbody');
        var draggedRow = null;

        function rowsInGroup(parentId) {
            return Array.prototype.filter.call(
                tbody.querySelectorAll('tr[draggable="true"]'),
                function (row) { return row.dataset.parent === parentId; },
            );
        }

        function sendOrder(parentId) {
            var order = rowsInGroup(parentId).map(function (row) {
                return parseInt(row.dataset.categoryId, 10);
            });

            fetch(reorderUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken(),
                },
                body: JSON.stringify({ parent: parentId ? parseInt(parentId, 10) : null, order: order }),
            }).then(function (response) {
                if (!response.ok && window.showToast) {
                    window.showToast('Sıralama yadda saxlanılmadı.', 'error');
                }
            }).catch(function () {
                if (window.showToast) {
                    window.showToast('Sıralama yadda saxlanılmadı.', 'error');
                }
            });
        }

        tbody.addEventListener('dragstart', function (event) {
            var row = event.target.closest('tr[draggable="true"]');
            if (!row) {
                return;
            }
            draggedRow = row;
            event.dataTransfer.effectAllowed = 'move';
            row.classList.add('is-dragging');
        });

        tbody.addEventListener('dragend', function () {
            if (draggedRow) {
                draggedRow.classList.remove('is-dragging');
            }
            tbody.querySelectorAll('.is-drop-target').forEach(function (row) {
                row.classList.remove('is-drop-target');
            });
            draggedRow = null;
        });

        tbody.addEventListener('dragover', function (event) {
            var targetRow = event.target.closest('tr[draggable="true"]');
            tbody.querySelectorAll('.is-drop-target').forEach(function (row) {
                row.classList.remove('is-drop-target');
            });
            if (!draggedRow || !targetRow || targetRow === draggedRow) {
                return;
            }
            if (targetRow.dataset.parent !== draggedRow.dataset.parent) {
                return;
            }
            event.preventDefault();
            targetRow.classList.add('is-drop-target');
        });

        function draggedBlock() {
            // A top-level row drags its child rows along with it (they
            // immediately follow it in the DOM) so the parent/children
            // grouping survives the move. A child row has no descendants
            // of its own, so its "block" is just itself.
            var block = [draggedRow];
            if (draggedRow.dataset.parent === '') {
                var sibling = draggedRow.nextElementSibling;
                while (sibling && sibling.dataset.parent === draggedRow.dataset.categoryId) {
                    block.push(sibling);
                    sibling = sibling.nextElementSibling;
                }
            }
            return block;
        }

        tbody.addEventListener('drop', function (event) {
            var targetRow = event.target.closest('tr[draggable="true"]');
            if (!draggedRow || !targetRow || targetRow === draggedRow) {
                return;
            }
            if (targetRow.dataset.parent !== draggedRow.dataset.parent) {
                return;
            }
            event.preventDefault();

            var rows = Array.prototype.slice.call(tbody.querySelectorAll('tr'));
            var draggedIndex = rows.indexOf(draggedRow);
            var targetIndex = rows.indexOf(targetRow);
            var block = draggedBlock();

            if (draggedIndex < targetIndex) {
                var afterAnchor = targetRow;
                if (targetRow.dataset.parent === '') {
                    var lastChild = targetRow;
                    var next = targetRow.nextElementSibling;
                    while (next && next.dataset.parent === targetRow.dataset.categoryId) {
                        lastChild = next;
                        next = next.nextElementSibling;
                    }
                    afterAnchor = lastChild;
                }
                block.forEach(function (row) { afterAnchor.after(row); afterAnchor = row; });
            } else {
                block.forEach(function (row) { targetRow.before(row); });
            }

            sendOrder(draggedRow.dataset.parent);
        });
    }

    document.addEventListener('DOMContentLoaded', function () {
        initDragReorder();
    });
})();
