# app.py
import os
import shutil
import threading
import time
import zipfile
from datetime import datetime, timedelta
from fileinput import filename
from shutil import rmtree

from PIL import Image
from celery import Celery
from celery.bin import celery
from flask import Flask, request, render_template, session, send_file, url_for, send_from_directory, jsonify
from werkzeug.utils import secure_filename, redirect

app = Flask(__name__)
app.secret_key = 'summit_mc_xyz'
app.config['MAX_CONTENT_LENGTH'] = 1000 * 1024 * 1024
app.config['CTM_USER_CONTENT'] = 'user-data'
if not os.path.exists(app.config['CTM_USER_CONTENT']):
    os.makedirs(app.config['CTM_USER_CONTENT'])
app = Flask(__name__)
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)


@app.route('/')
def home():
    return render_template('custom/progress.html')


""" RESIZE START """


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
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ['png']


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
        uploaded_files = request.files.getlist("images")
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
        dir_name = f"BONEMEAL_RESIZE_{now.strftime('%Y-%m-%d_%H-%M-%S')}"
        target_dir = os.path.join('user_content/resize', dir_name)

        if not os.path.exists(target_dir):
            os.makedirs(target_dir)

        saved_files = []
        for file in uploaded_files:
            if file and allowed_ctm_file(file.filename):
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


""" RESIZE END """

""" SPLIT CTM START """


@celery.task
def split_and_save_image(target_dir, uploaded_files, num_rows, num_columns):
    processed_files = []
    for file in uploaded_files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(target_dir, filename)
            file.save(file_path)

            new_filenames = split_image(file_path, num_rows, num_columns)
            processed_files.extend(new_filenames)
    return processed_files


def split_image(file_path, num_rows, num_columns):
    new_filenames = []  # List to store names of new files
    with Image.open(file_path) as img:
        img_width, img_height = img.size
        slice_width, slice_height = img_width // num_columns, img_height // num_rows
        counter = 0
        for row in range(num_rows):
            for col in range(num_columns):
                left, upper = col * slice_width, row * slice_height
                right, lower = left + slice_width, upper + slice_height
                img_cropped = img.crop((left, upper, right, lower))
                new_filename = f"{counter}.png"
                img_cropped.save(os.path.join(os.path.dirname(file_path), new_filename))
                new_filenames.append(new_filename)
                counter += 1
    return new_filenames


def allowed_ctm_file(filename_ctm):
    return '.' in filename and filename_ctm.rsplit('.', 1)[1].lower() in ['png']


def zip_directory(directory_path, zip_filename):
    # Create a ZipFile object
    with zipfile.ZipFile(os.path.join(directory_path, f"{zip_filename}.zip"), 'w') as zip_file:
        # Iterate over all the files in the directory
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                # Add the file to the ZipFile object
                zip_file.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), directory_path))

    # Return the path to the zip file
    return os.path.join(directory_path, f"{zip_filename}.zip")


@app.route('/ctm_generator', methods=['GET', 'POST'])
def ctm_generator():
    if request.method == 'POST' and request.form.get('properties'):
        method = 'repeat'
        width = request.form.get('width')
        height = request.form.get('height')
        tiles = request.form.get('tiles').split(',')
        symmetry = request.form.get('symmetry')

        # Construct the properties file content
        properties = (f"method={method}\n"
                      f"matchTiles={filename}\n"
                      f"width={width}\n"
                      f"height={height}\n"
                      f"tiles={','.join(tiles)}")
        if symmetry:
            properties += f"\nsymmetry={symmetry}"

        # Create the properties file
        with open('ctm.properties', 'w') as f:
            f.write(properties)

        # Send the properties file to the user for download
        return send_file('ctm.properties', as_attachment=True)


@app.route('/split_ctm', methods=['GET', 'POST'])
def split_ctm():
    if request.method == 'POST':
        if 'images' not in request.files:
            return 'No images part in the request', 400
        uploaded_files = request.files.getlist('images')
        num_rows_selection = request.form.get('num_rows')
        num_columns_selection = request.form.get('num_columns')
        # Use the mappings to get the integer values
        num_rows = int(num_rows_selection) if num_rows_selection else 2  # Default to 2 if not provided
        num_columns = int(num_columns_selection) if num_columns_selection else 2  # Default to 2 if not provided
        # Create a unique directory for this upload session
        now = datetime.now()
        upload_session_dir = f"BONEMEAL_CTM_{now.strftime('%Y-%m-%d_%H-%M-%S')}"
        target_dir = os.path.join('user-data/ctm', upload_session_dir)

        if not os.path.exists(target_dir):
            os.makedirs(target_dir)

        # Create a Celery task and store the task ID in the session
        task = split_and_save_image.delay(target_dir, uploaded_files, num_rows, num_columns)
        session['task_id'] = task.id

        return render_template('custom/progress.html', task_id=task.id)
    return render_template('custom/upload-ctm.html')


@app.route('/ctm_result')
def ctm_result():
    task_id = session.get('task_id')
    task = celery.AsyncResult(task_id)
    if task.state == 'SUCCESS':
        processed_files = task.result
        zip_filename = f"BONEMEAL_CTM_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
        zip_path = zip_directory(os.path.join('user-data/ctm', task_id), zip_filename)
        return render_template('custom/ctm-result.html', files=processed_files, zip_file=f"{zip_filename}.zip")
    else:
        return render_template('custom/progress.html', task_id=task_id)


""" SPLIT CTM END """


@app.route('/task_status/<task_id>')
def task_status(task_id):
    task = celery.AsyncResult(task_id)
    if task.state == 'PENDING':
        response = {
            'state': 'PENDING',
            'progress': 0
        }
    elif task.state == 'FAILURE':
        response = {
            'state': 'FAILURE',
            'progress': 100
        }
    else:
        response = {
            'state': 'SUCCESS',
            'progress': 100
        }
    return jsonify(response)


@app.route('/download')
def download():
    zip_path = session.get('zip_path')
    if zip_path and os.path.isfile(zip_path):
        return send_file(zip_path, as_attachment=True)
    return 'No file available for download', 404


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


@app.route('/documentation')
def documentation():
    return render_template('custom/documentation.html')


if __name__ == "__main__":
    app.run(host='0.0.0.0')
