
//let hoverAudioClip = new Audio('/static/sound/clicksound.mp3');

//document.getElementById('hoverSound').addEventListener('mouseenter', function() {
//    hoverAudioClip.play();
//});

let clickAudioClip = new Audio('/static/sound/hoversound.mp3');
document.getElementById('clickSound').addEventListener('mousedown', function(button) {
    clickAudioClip.play();
    button.addEventListener('click', function() {
    });
});



document.getElementById("year").innerHTML = new Date().getFullYear();
