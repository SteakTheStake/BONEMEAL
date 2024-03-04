document.addEventListener('DOMContentLoaded', function () {
    var menuButton = document.getElementById('menuButton');
    var menu = document.querySelector('.navbar .menu');

    menuButton.addEventListener('click', function () {
        menu.classList.toggle('show');
    });
});

function delay (URL) {
    setTimeout( function() { window.location = URL }, 250 );
}

document.getElementById("go-back").addEventListener("click", () => {
    history.back();
});