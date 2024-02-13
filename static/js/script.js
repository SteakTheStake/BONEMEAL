document.getElementById('runScript').addEventListener('click', function() {
    // Example: Sending an AJAX request to the Flask server
    fetch('/run-script')
        .then(response => response.text())
        .then(data => {
            document.getElementById('resultArea').innerText = data;
        });
});

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