# app.py
import os
import tempfile
import glob
import zipfile

from PIL import Image
from flask import Flask, request, render_template, session, redirect, url_for, send_file, json, send_from_directory
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'summit_mc_xyz'


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/pkg/bonemeal_bg.wasm')
def serve_wasm():
    return send_from_directory('pkg', 'bonemeal_bg.wasm', mimetype='application/wasm')


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff'}


def allowed_file(filename):
    # Check if the file has one of the allowed extensions
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/resize', methods=['GET', 'POST'])
def resize():
    if request.method == 'POST':
        uploaded_files = request.files.getlist("files")
        percentage = request.form.get('percentage', type=float, default=0)
        if not 0 < percentage <= 100:
            return render_template('custom/resize.html', error="Percentage must be between 0 and 100.", files=[])

        temp_files = []
        with tempfile.TemporaryDirectory() as temp_dir:
            for file in uploaded_files:
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file_path = os.path.join(temp_dir, filename)
                    file.save(file_path)
                    temp_files.append(file_path)

        # Pass the temp_files and percentage to the template
        return render_template('custom/resize.html', files=temp_files, percentage=percentage)

    # Handle GET request
    return render_template('custom/resize.html', files=[])


@app.route('/resize-result', methods=['GET'])
def resize_result():
    output = session.get('resize_output')
    print(f"Resize Result Output: {output}")  # Debugging line
    return render_template('custom/resize-result.html', output=output)


@app.route('/download')
def download():
    zip_path = session.get('zip_path')
    if zip_path and os.path.exists(zip_path):
        return send_file(zip_path, as_attachment=True)
    return 'No file available for download', 404


@app.route('/split_ctm')
def split_ctm():
    return render_template('custom/split_ctm.html')


@app.route('/convert_ctm')
def convert_ctm():
    return render_template('custom/convert_ctm.html')


@app.route('/tile_textures')
def tile_textures():
    return render_template('custom/tile_textures.html')


@app.route('/merge_ctm')
def merge_ctm():
    return render_template('custom/merge_ctm.html')


@app.route('/internal_error')
def internal_error():
    return render_template('custom/internal_error.html')


if __name__ == "__main__":
    app.run(host='0.0.0.0')
