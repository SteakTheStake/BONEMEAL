# app.py
import os
import shutil
import threading
import time
from datetime import datetime, timedelta
from shutil import rmtree

from PIL import Image
from flask import Flask, request, render_template, session, send_file
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'summit_mc_xyz'
app.config['MAX_CONTENT_LENGTH'] = 1000 * 1024 * 1024


@app.route('/')
def home():
    return render_template('index.html')


def zip_directory(folder_path, output_filename):
    shutil.make_archive(output_filename, 'zip', folder_path)
    return output_filename + '.zip'


def delete_files_after_delay(directory_path, zip_path, delay=60):
    """ Deletes the specified directory and zip file after a delay. """
    def task():
        time.sleep(delay)
        try:
            # Delete all files in the directory
            rmtree(directory_path)
            # Delete the zip file
            os.remove(zip_path)
            print(f"Deleted directory {directory_path} and zip file {zip_path}")
        except Exception as e:
            print(f"Error deleting files: {e}")

    threading.Thread(target=task).start()


def get_directory_path():
    path = input("Enter the directory path: ")
    if not os.path.isdir(path):
        print("Invalid directory path.")
        return get_directory_path()
    return path


def get_image_dimensions():
    try:
        width = int(input("Enter the desired width: "))
        height = int(input("Enter the desired height: "))
        return width, height
    except ValueError:
        print("Invalid dimensions. Please enter numeric values.")
        return get_image_dimensions()


def apply_diffusion_dither(image_path):
    with Image.open(image_path) as img:
        # Convert the image to 8-bit palette using dithering
        dithered_img = img.convert("P", dither=Image.Dither.FLOYDSTEINBERG)
        # Save the dithered image
        dithered_img.save(image_path)


def resize_image(image_path, size, filter_type):
    with Image.open(image_path) as img:
        img.thumbnail(size, filter_type)
        return img


def process_images(directory, size):
    for filename in os.listdir(directory):
        if filename.endswith(".png"):
            image_path = os.path.join(directory, filename)
            if "_s.png" in filename or "_n.png" in filename:
                resized_image = resize_image(image_path, size, Image.Resampling.BICUBIC)
            else:
                resized_image = resize_image(image_path, size, Image.Resampling.NEAREST)
            resized_image.save(os.path.join(directory, "resized", filename))


# Add a utility function for allowed file types
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ['png', 'jpg', 'jpeg', 'gif']


def calculate_new_dimensions(width, height, target_size):
    if width < height:
        new_width = target_size
        new_height = int((target_size / width) * height)
    else:
        new_height = target_size
        new_width = int((target_size / height) * width)
    return new_width, new_height


@app.route('/resize', methods=['GET', 'POST'])
def resize():
    if request.method == 'POST':
        uploaded_files = request.files.getlist("files")
        size_selection = request.form.get('value-radio')  # Get the selected radio button value

        # Convert size_selection to actual pixel values
        size_mapping = {
            "value-1": 16,
            "value-2": 32,
            "value-3": 64,
            "value-4": 128,
            "value-5": 256,
            "value-6": 512
        }
        target_size = size_mapping.get(size_selection, 16)  # Default to 16x16 if no valid selection

        if len(uploaded_files) > 5000:
            return "Error: Too many files. The limit is 5000.", 400

        apply_dither = 'dither' in request.form

        now = datetime.today()
        dir_name = f"BONEMEAL_EXPORT_{now.strftime('%Y-%m-%d_%H-%M-%S')}"
        target_dir = os.path.join('root', dir_name)

        if not os.path.exists(target_dir):
            os.makedirs(target_dir)

        saved_files = []
        for file in uploaded_files:
            if file and allowed_file(file.filename):
                filename_only = os.path.basename(file.filename)
                secure_name = secure_filename(filename_only)

                sub_dir = os.path.dirname(file.filename)
                target_sub_dir = os.path.join(target_dir, sub_dir)
                if not os.path.exists(target_sub_dir):
                    os.makedirs(target_sub_dir)

                file_path = os.path.join(target_sub_dir, secure_name)
                file.save(file_path)

                try:
                    with Image.open(file_path) as img:
                        if img.width < 8 or img.height < 8:
                            print(f"Skipping file {filename_only} due to insufficient dimensions.")
                            os.remove(file_path)
                            continue

                        if apply_dither and not filename_only.endswith(("_s.png", "_n.png")):
                            apply_diffusion_dither(file_path)

                        # Calculate new dimensions while maintaining aspect ratio
                        new_width, new_height = calculate_new_dimensions(img.width, img.height, target_size)
                        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                        img.save(file_path)
                        saved_files.append(file_path)

                except (OSError, ValueError) as error:
                    print(f"Error processing file {filename_only}: {error}")

        zip_path = zip_directory(target_dir, os.path.join('root', dir_name))
        session['zip_path'] = zip_path
        deletion_delay = 60
        deletion_time = datetime.now() + timedelta(seconds=deletion_delay)
        remaining_seconds = int((deletion_time - datetime.now()).total_seconds())

        delete_files_after_delay(target_dir, zip_path, delay=deletion_delay)

        return render_template('custom/resize-result.html', files=saved_files, remaining_seconds=remaining_seconds)

    return render_template('custom/resize-img.html', files=[])


@app.route('/download')
def download():
    zip_path = session.get('zip_path')
    if zip_path and os.path.isfile(zip_path):
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
