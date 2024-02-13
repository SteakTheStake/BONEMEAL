# app.py
import os
import tempfile
import glob
import zipfile

from PIL import Image
from flask import Flask, request, render_template, session, redirect, url_for, send_file
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'summit_mc_xyz'


@app.route('/')
def home():
    return render_template('index.html')


def resize_image(image_path, percentage):
    try:
        img = Image.open(image_path)
        width, height = img.size
        new_width = int(width * percentage / 100)
        new_height = int(height * percentage / 100)
        img_resized = img.resize((new_width, new_height), Image.Resampling.NEAREST)
        img_resized.save(image_path)
        return f"Resized {image_path}"
    except Exception as e:
        return f"Error resizing {image_path}: {e}"


def resize_images_in_tree(folder_path, percentage):
    messages = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff', '.PNG', '.JPG', '.JPEG', '.BMP',
                                      '.GIF', '.TIFF')):
                image_path = os.path.join(root, file)
                message = resize_image(image_path, percentage)
                messages.append(message)
    return messages


def find_png_files(directory):
    """ Find all .png files in the specified directory and its subdirectories. """
    return glob.glob(
        os.path.join(directory, '.png', '.jpg', '.jpeg', '`.bmp', '.gif', '.tiff'), recursive=True)


def convert_to_indexed_color(image_path):
    """ Convert the image to indexed color and save it. """
    with Image.open(image_path) as img:
        img = img.convert('P', palette=Image.Palette.ADAPTIVE, colors=256)
        img.save(image_path)


def convert_all_images(directory):
    """ Convert all .png images in the directory to indexed color. """
    for image_path in find_png_files(directory):
        convert_to_indexed_color(image_path)
        print(f'Converted: {image_path}')


@app.route('/resize', methods=['GET', 'POST'])
def resize():
    if request.method == 'POST':
        uploaded_files = request.files.getlist("files")
        percentage = request.form['percentage']
        convert_indexed = request.form.get('cbx') == 'on'
        try:
            percentage = float(percentage)
            if not 0 < percentage <= 100:
                raise ValueError("Percentage must be between 0 and 100.")
        except ValueError as e:
            return render_template('custom/resize.html', output=str(e))

        if convert_indexed:
            with tempfile.TemporaryDirectory() as temp_dir:
                for file in uploaded_files:
                    if file and file.filename.lower().endswith('.png'):
                        filename = secure_filename(file.filename)
                        file_path = os.path.join(temp_dir, filename)
                        file.save(file_path)
                        convert_to_indexed_color(file_path)

        output_messages = []
        zip_path = os.path.join(tempfile.gettempdir(), 'bonemeal-output.zip')
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for file in uploaded_files:
                filename = secure_filename(file.filename)
                file_path = os.path.join(temp_dir, filename)
                if os.path.exists(file_path):  # Check if file exists
                    zipf.write(file_path, filename)

        session['zip_path'] = zip_path

        return redirect(url_for('resize_result'))

    return render_template('custom/resize.html')


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
