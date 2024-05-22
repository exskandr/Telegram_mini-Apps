from flask import Flask, request, redirect, jsonify, send_from_directory, url_for
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.utils import secure_filename
from PIL import Image
import os
import io
import logging
from dotenv import load_dotenv


load_dotenv()

# Login settings
logging.basicConfig(level=logging.INFO,
                    filename='flask_bot.log',
                    filemode='w',
                    format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Configuring server for HTTPS
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1, x_prefix=1)


@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify(error="File is too large"), 413


# resizing the picture
def resize_and_reduce_quality(image_file, max_size=(1024, 1024), quality=50):
    img = Image.open(image_file)
    img.thumbnail(max_size)
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=quality)
    buffer.seek(0)
    return buffer


def clean_upload_folder(folder_path, max_files=10):
    files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if
             os.path.isfile(os.path.join(folder_path, f))]

    if len(files) > max_files:  # checking the number of files in a folder
        files.sort(key=os.path.getctime)  # sort the files by creation time
        for file in files[:-max_files]:  # delete all files except the most recent ones
            os.remove(file)
            logger.info(f"Removed old file: {file}")


@app.before_request
def before_request():
    """Force HTTPS"""
    if not request.is_secure and not app.debug:
        url = request.url.replace("http://", "https://", 1)
        code = 301
        return redirect(url, code=code)


@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return {"error": "No file part"}, 400

    file = request.files['file']
    if file.filename == '':
        return {"error": "No selected file"}, 400

    if file:

        # Checking the image size
        file.seek(0, os.SEEK_END)
        file_length = file.tell()
        file.seek(0)
        if file_length > 10 * 1024 * 1024:  # 10 МБ
            return jsonify(error="File is too large"), 413

        # reduce the size and quality of the image before saving
        resized_file = resize_and_reduce_quality(file)

        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        # save image
        with open(file_path, 'wb') as f:
            f.write(resized_file.read())

        clean_upload_folder(app.config['UPLOAD_FOLDER'])  # deleting obsolete files

        file_url = url_for('uploaded_file', filename=filename, _external=True)
        logger.info(f'url img: {file_url}')
        return {"url": file_url}


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    logger.info(f"upload file {send_from_directory(app.config['UPLOAD_FOLDER'], filename)}")
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


if __name__ == '__main__':
    app.run(port=5000, debug=False)
