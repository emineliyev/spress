/**
 * News list (templates/cms/news_list.html): per-row "..." action menu
 * and the select-all / bulk-action bar.
 */
(function () {
    'use strict';

    function positionRowMenuPanel(toggle, panel) {
        // The panel is `position: fixed` (viewport-relative) specifically so
        // it can escape `.cms-table-wrapper`'s `overflow: hidden` (needed
        // there for the table's rounded corners + horizontal scroll) —
        // `position: absolute` inside that wrapper got clipped/invisible
        // for any row near the bottom edge.
        var rect = toggle.getBoundingClientRect();
        panel.style.top = (rect.bottom + 4) + 'px';
        panel.style.right = (window.innerWidth - rect.right) + 'px';
    }

    function initRowMenus() {
        var toggles = document.querySelectorAll('[data-action="toggle-row-menu"]');
        if (!toggles.length) {
            return;
        }

        function closeAllPanels() {
            document.querySelectorAll('.cms-row-menu__panel').forEach(function (p) {
                p.hidden = true;
            });
        }

        toggles.forEach(function (toggle) {
            toggle.addEventListener('click', function (event) {
                event.stopPropagation();
                var panel = toggle.nextElementSibling;
                var willOpen = panel.hidden;
                closeAllPanels();
                if (willOpen) {
                    positionRowMenuPanel(toggle, panel);
                }
                panel.hidden = !willOpen;
                toggle.setAttribute('aria-expanded', String(willOpen));
            });
        });

        document.addEventListener('click', function (event) {
            // Clicking a closed <select> to open it (the "Qovluğa köçür"
            // move select, templates/cms/partials/media_grid.html) fires
            // a bubbling click on the select itself, same as any other
            // click inside the panel — without this guard the panel (and
            // the select along with it) closed itself the instant it was
            // clicked, before a folder could ever be chosen.
            if (event.target.closest('.cms-row-menu__move-form')) {
                return;
            }
            closeAllPanels();
        });
        // Fixed-position panels don't scroll with the table body, so a
        // stale-looking detached panel would otherwise linger on scroll.
        window.addEventListener('scroll', closeAllPanels, true);
    }

    function initBulkSelection() {
        var selectAll = document.querySelector('[data-role="select-all"]');
        var bulkBar = document.querySelector('[data-role="bulk-bar"]');
        var bulkCount = document.querySelector('[data-role="bulk-count"]');
        if (!selectAll || !bulkBar) {
            return;
        }

        var rowCheckboxes = document.querySelectorAll('[data-role="select-row"]');

        function update() {
            var checked = Array.prototype.filter.call(rowCheckboxes, function (checkbox) {
                return checkbox.checked;
            });
            var buttons = bulkBar.querySelectorAll('button');

            if (checked.length > 0) {
                bulkBar.hidden = false;
                bulkCount.textContent = checked.length + ' seçildi';
                buttons.forEach(function (button) {
                    button.disabled = false;
                });
            } else {
                bulkBar.hidden = true;
                buttons.forEach(function (button) {
                    button.disabled = true;
                });
            }
        }

        selectAll.addEventListener('change', function () {
            rowCheckboxes.forEach(function (checkbox) {
                checkbox.checked = selectAll.checked;
            });
            update();
        });
        rowCheckboxes.forEach(function (checkbox) {
            checkbox.addEventListener('change', update);
        });
    }

    document.addEventListener('DOMContentLoaded', function () {
        initRowMenus();
        initBulkSelection();
    });
})();
