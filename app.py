# app.py
import os
import tempfile, subprocess

from werkzeug.utils import secure_filename, send_from_directory
from flask import Flask, request, render_template
from flask import session, redirect, url_for

app = Flask(__name__)
app.secret_key = 'summit_mc_xyz'


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/resize', methods=['GET', 'POST'])
def resize():
    if request.method == 'POST':
        # Get uploaded files and resize percentage
        uploaded_files = request.files.getlist("files")
        percentage = request.form['percentage']

        # Validate percentage
        try:
            percentage = float(percentage)
            if not 0 < percentage <= 100:
                raise ValueError("Percentage must be between 0 and 100.")
        except ValueError as e:
            return render_template('custom/resize.html', output=str(e))

        # Process each uploaded file
        output_messages = []
        for file in uploaded_files:
            if file:
                # Save the file temporarily
                filename = secure_filename(file.filename)
                file_path = os.path.join(tempfile.gettempdir(), filename)
                file.save(file_path)

                # Call the resize script as a subprocess
                process = subprocess.run(
                    ['python', 'static/py/resize-script.py', file_path, str(percentage)],
                    capture_output=True, text=True)
                output_messages.append(process.stdout)

        # Combine all messages for output
        output = "\n".join(output_messages)
        session['resize_output'] = output
        return redirect(url_for('resize_result'))

        # Redirect to the resize-result route

    # For a GET request, just render the template
    return render_template('custom/resize.html')


@app.route('/resize-result', methods=['GET'])
def resize_result():
    if request.method == 'POST':
        # In case of POST, retrieve data from the session or form
        output = session.get('resize_output', 'No data available')
    else:

        output = 'No data available'

    return render_template('custom/resize-result.html', output=output)


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


if __name__ == "__main__":
    app.run(host='0.0.0.0')
