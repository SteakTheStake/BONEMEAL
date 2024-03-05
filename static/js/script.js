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

const gradient = document.querySelector(".gradient");

function onMouseMove(event) {
    gradient.style.backgroundImage = 'radial-gradient(at ' + event.clientX + 'px ' + event.clientY + 'px, rgba(33, 15, 75, 0.75) 0, #120431 70%)';
}
document.addEventListener("mousemove", onMouseMove);
