let hoverAudioClip = new Audio('/static/sound/clicksound.mp3');

document.getElementById('hoverSound').addEventListener('mouseenter', function() {
    hoverAudioClip.play();
});

let clickAudioClip = new Audio('/static/sound/hoversound.mp3');
document.getElementById('clickSound').addEventListener('mousedown', function() {
    let image = document.getElementById('imageToScale');
    let button = document.getElementById('scaleButton');
    clickAudioClip.play();
    button.addEventListener('click', function() {
        // Increase the scale of the image by 15%
        image.style.transform = 'scale(1.05)';
    });
});



document.getElementById("year").innerHTML = new Date().getFullYear();
