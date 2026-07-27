function initializeCategorySectionsToggle() {
    const checkbox = document.querySelector('[data-role="toggle-all-categories"]');
    const countField = document.querySelector('[data-role="category-sections-count-field"]');
    const countInput = document.querySelector('[data-role="category-sections-count"]');
    if (!checkbox || !countField || !countInput) {
        return;
    }

    const syncDisabledState = () => {
        // readOnly, not disabled — a disabled input is excluded from
        // form submission entirely, which would leave this required
        // field empty and fail validation. readOnly keeps its current
        // value submitting normally; the view ignores it anyway once
        // home_show_all_categories is true (apps/news/views.py).
        countInput.readOnly = checkbox.checked;
        countField.classList.toggle('form-field--disabled', checkbox.checked);
    };

    checkbox.addEventListener('change', syncDisabledState);
    syncDisabledState();
}

document.addEventListener('DOMContentLoaded', initializeCategorySectionsToggle);
