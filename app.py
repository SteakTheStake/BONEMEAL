# app.py
import os
import tempfile, subprocess

from werkzeug.utils import secure_filename
from flask import Flask, request, render_template, session, redirect, url_for

app = Flask(__name__)
app.secret_key = 'summit_mc_xyz'


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/resize', methods=['GET', 'POST'])
def resize():
    if request.method == 'POST':
        uploaded_files = request.files.getlist("files")
        percentage = request.form['percentage']
        try:
            percentage = float(percentage)
            if not 0 < percentage <= 100:
                raise ValueError("Percentage must be between 0 and 100.")
        except ValueError as e:
            return render_template('custom/resize.html', output=str(e))

        output_messages = []
        for file in uploaded_files:
            if file:
                filename = secure_filename(file.filename)
                file_path = os.path.join(tempfile.gettempdir(), filename)
                file.save(file_path)
                process = subprocess.run(
                    ['python', 'static/py/resize-script.py', file_path, str(percentage)],
                    capture_output=True, text=True)
                print(f"Process Error: {process.stderr}")
                print(f"Process Output: {process.stdout}")
                output_messages.append(process.stdout)

        output = "\n".join(output_messages)
        print(f"Final Output: {output}")  # Debugging line
        session['resize_output'] = output
        print(f"Session Output: {session['resize_output']}")  # Debugging line
        return redirect(url_for('resize_result'))

    return render_template('custom/resize.html')


@app.route('/resize-result', methods=['GET'])
def resize_result():
    output = session.get('resize_output', 'No data available')
    print(f"Resize Result Output: {output}")  # Debugging line
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
