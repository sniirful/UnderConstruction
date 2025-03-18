let filtersButton = document.querySelector('div.full > div:first-child > button');
let filtersContainer = document.querySelector('div.filters');

filtersButton.addEventListener('click', () => {
    if (filtersButton.classList.contains('collapsed')) {
        filtersButton.classList.remove('collapsed');
        filtersButton.classList.add('expanded');
        filtersContainer.classList.remove('hidden');
        filtersContainer.classList.add('shown');
    } else {
        filtersButton.classList.remove('expanded');
        filtersButton.classList.add('collapsed');
        filtersContainer.classList.remove('shown');
        filtersContainer.classList.add('hidden');
    }
});

for (let filter of document.querySelectorAll('div.mini-button.unselected')) {
    filter.addEventListener('click', () => {
        if (filter.classList.contains('unselected')) {
            filter.classList.remove('unselected');
            filter.classList.add('selected');
        } else {
            filter.classList.remove('selected');
            filter.classList.add('unselected');
        }

        refreshPosts()
    });
}