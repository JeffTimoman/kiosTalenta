var toggleButton = document.querySelector('.dropdown-toggle');
var dropdownMenu = document.querySelector('.dropdown-menu');

toggleButton.addEventListener('click', function() {
    dropdownMenu.classList.toggle('show');
});

document.addEventListener('click', function(event) {
    if (!toggleButton.contains(event.target) && !dropdownMenu.contains(event.target)) {
        dropdownMenu.classList.remove('show');
    }
});