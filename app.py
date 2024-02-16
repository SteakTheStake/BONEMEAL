# app.py
import os
import glob
import zipfile
from datetime import datetime

from PIL import Image
from flask import Flask, request, render_template, session, redirect, url_for, send_file, json, send_from_directory
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'summit_mc_xyz'


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/run-resize')
def serve_wasm():
    return send_from_directory('static/pkg', 'bonemeal_bg.wasm', mimetype='application/wasm')


# Utility function to check allowed file extensions
def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff'}
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/resize', methods=['GET', 'POST'])
def resize():
    if request.method == 'POST':
        uploaded_files = request.files.getlist("files")
        percentage = request.form.get('percentage', type=float, default=0)

        if not 0 < percentage <= 100:
            return render_template('custom/resize.html', error="Percentage must be between 0 and 100.", files=[])

        # Generate unique directory name
        now = datetime.today()
        dir_name = f"img-resize-{now.strftime('%Y%m%d-%H%M%S')}"
        target_dir = os.path.join('root', dir_name)  # Adjust 'root' to your actual root directory path

        # Create directory if it doesn't exist
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)

        saved_files = []
        for file in uploaded_files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(target_dir, filename)
                file.save(file_path)
                saved_files.append(file_path)

        # Pass the saved files and percentage to the template
        return render_template('custom/resize.html', files=saved_files, percentage=percentage)

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
    app.run(debug=True)
