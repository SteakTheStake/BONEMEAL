var fileTag = document.getElementById("fileUpload"),
    preview = document.getElementById("preview");

fileTag.addEventListener("change", function() {
    changeImage(this);
});

function changeImage(input) {
    var reader;

    if (input.files && input.files[0]) {
        reader = new FileReader();

        reader.onload = function(e) {
            preview.setAttribute('src', e.target.result);
        }

        reader.readAsDataURL(input.files[0]);
    }
}

document.getElementById('fileUpload').addEventListener('change', function() {
    if (this.files.length > 0) {
        document.querySelectorAll('.no-files').forEach(el => el.style.display = 'none');
    }
});



document.getElementById('fileUpload').addEventListener('change', function() {
    if (this.files.length > 0) {
        document.querySelectorAll('.no-files').forEach(el => el.style.display = 'initial');
    }
});

