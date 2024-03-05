# task.py
import os
import shutil
import threading
import time
import zipfile
from datetime import datetime, timedelta
from fileinput import filename
from shutil import rmtree

import celeryconfig
from PIL import Image
from celery import Celery
from celery.bin import celery
from flask import Flask, request, render_template, session, send_file, url_for, send_from_directory, jsonify
from werkzeug.utils import secure_filename, redirect

# Create a Celery instance using the broker URL from Flask app
app = Celery('tasks', broker='CELERY_BROKER_URL')
app.config_from_object(celeryconfig)

""" SPLIT """


@app.task
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


@app.task
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


@app.task
def allowed_ctm_file(filename_ctm):
    return '.' in filename and filename_ctm.rsplit('.', 1)[1].lower() in ['png']


@app.task
def zip_directory(directory_path, zip_filename):
    # Create a ZipFile object
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)

        with zipfile.ZipFile(os.path.join(directory_path, f"{zip_filename}.zip"), 'w') as zip_file:
            # Iterate over all the files in the directory
            for root, dirs, files in os.walk(directory_path):
                for file in files:
                    # Add the file to the ZipFile object
                    zip_file.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), directory_path))

    # Return the path to the zip file
    return os.path.join(directory_path, f"{zip_filename}.zip")


""" SPLIT """

""" RESIZE """


@app.task
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


@app.task
def get_directory_path():
    path = input("Enter the directory path: ")
    if not os.path.isdir(path):
        print("Invalid directory path.")
        return get_directory_path()
    return path


@app.task
def get_image_dimensions():
    try:
        width = int(input("Enter the desired width: "))
        height = int(input("Enter the desired height: "))
        return width, height
    except ValueError:
        print("Invalid dimensions. Please enter numeric values.")
        return get_image_dimensions()


@app.task
def apply_diffusion_dither(image_path):
    with Image.open(image_path) as img:
        # Convert the image to 8-bit palette using dithering
        dithered_img = img.convert("P", dither=Image.Dither.FLOYDSTEINBERG)
        # Save the dithered image
        dithered_img.save(image_path)


@app.task
def resize_image(image_path, size, filter_type):
    with Image.open(image_path) as img:
        img.thumbnail(size, filter_type)
        return img


@app.task
def process_images(directory, size):
    for filename in os.listdir(directory):
        if filename.endswith(".png"):
            image_path = os.path.join(directory, filename)
            if "_s.png" in filename or "_n.png" in filename:
                resized_image = resize_image(image_path, size, Image.Resampling.BICUBIC)
            else:
                resized_image = resize_image(image_path, size, Image.Resampling.NEAREST)
            resized_image.save(os.path.join(directory, "resized", filename))


@app.task
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ['png']


@app.task
def calculate_new_dimensions(width, height, target_size):
    if width < height:
        new_width = target_size
        new_height = int((target_size / width) * height)
    else:
        new_height = target_size
        new_width = int((target_size / height) * width)
    return new_width, new_height


""" RESIZE """
