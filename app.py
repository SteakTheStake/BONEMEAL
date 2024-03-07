# app.py
import os
from datetime import datetime, timedelta
from fileinput import filename

from PIL import Image
from celery.bin import celery
from flask import Blueprint, render_template
from flask import request, session, send_file, jsonify, redirect, url_for
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from __init__ import create_app
from config import secret_key
from task import allowed_ctm_file, apply_diffusion_dither, calculate_new_dimensions, zip_directory, \
    delete_files_after_delay, split_and_save_image

app = Blueprint('app', __name__)


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/profile')
@login_required
def profile():
    return render_template('custom/profile.html', name=current_user.name)


@app.route('/settings')
def settings():
    return render_template('custom/settings.html')


@app.route('/progress')
def progress():
    return render_template('custom/progress.html')


@app.route('/login', methods=['GET'])
def login():
    return render_template('custom/login.html')


""" RESIZE START """


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
        target_dir = os.path.join('user-data/resize', dir_name)

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

        zip_filename = f"{dir_name}.zip"
        zip_path = zip_directory(target_dir, zip_filename)
        deletion_delay = 60
        deletion_time = datetime.now() + timedelta(seconds=deletion_delay)
        remaining_seconds = int((deletion_time - datetime.now()).total_seconds())

        delete_files_after_delay(target_dir, zip_path, delay=deletion_delay)

        return render_template('custom/resize-result.html', files=saved_files, remaining_seconds=remaining_seconds)

    return render_template('custom/resize-img.html', files=[])


""" RESIZE END """

""" SPLIT CTM START """


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
    task = celery.result(task_id)
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
    task = celery.result(task_id)
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


if __name__ == '__main__':
    app = create_app()  # Get the Flask application instance from create_app()
    app.secret_key = secret_key
    app.run(host="0.0.0.0")
