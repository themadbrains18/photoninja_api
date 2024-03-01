# bg_remover.py
from PIL import Image
from rembg import remove
import numpy as np
from flask import session
from werkzeug.utils import secure_filename
from datetime import datetime
from flask import Flask, jsonify, request
import os
from flask_cors import cross_origin


ALLOWED_EXTENSIONS = {'png', 'webp', 'jpg', 'jpeg', 'gif'}
UPLOAD_FOLDER = os.path.join(os.getcwd() ,'uploads')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def timestampsWithFilename(filename):
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"public/static/{filename}_{timestamp}_tmb.png"

def bgRemovedAndSaveImage(input_path, output_path, alpha_matting=False):
    input_image = Image.open(input_path)
    input_array = np.array(input_image)
    output_array = remove(input_array, alpha_matting=alpha_matting)
    output_image = Image.fromarray(output_array)
    output_image.save(output_path)

def removeBackground(file):
    filename = secure_filename(file.filename)
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)

    output_path = timestampsWithFilename(filename)
    bgRemovedAndSaveImage(file_path, output_path, alpha_matting=True)
    session['bg_removed_img'] = output_path

    return output_path

def bg_remove_route(app):
    @app.route('/api/bg-remove', methods=['POST'])
    @cross_origin(supports_credentials=True)
    def upload_file():
        if request.method == 'POST':
            if 'file' not in request.files:
                return jsonify({'error': 'No file part'})

            file = request.files['file']
            if file.filename == '' or not allowed_file(file.filename):
                return jsonify({'error': 'Invalid file'})

            output_path = removeBackground(file)
            return jsonify({'filename': output_path})

        return jsonify({'error': 'Invalid request'})
