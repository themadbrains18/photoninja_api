# bg_remove.py

import os
from flask import Flask, jsonify, request, send_file
from PIL import Image
from rembg import remove
import numpy as np
from werkzeug.utils import secure_filename
from datetime import datetime
from flask_cors import cross_origin

ALLOWED_EXTENSIONS = {'png', 'webp', 'jpg', 'jpeg', 'gif'}
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def timestampsWithFilename(filename):
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"static/{filename}_{timestamp}_tmb.png"

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

    return output_path  # Return the path of the background removed image

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
            return jsonify({'filename': output_path})  # Return the path of the background removed image

        return jsonify({'error': 'Invalid request'})

    return app

def add_bg_route(app):
    @app.route('/api/add-bg', methods=['POST'])
    @cross_origin(supports_credentials=True)
    def apply_background():
        background_color = request.form.get('background_color')
        processed_image_path = request.form.get('processed_image_path')
        if processed_image_path:
            original_image = Image.open(processed_image_path)

            # Apply background color if provided
            if background_color:
                new_bg_image = Image.new('RGB', original_image.size, color=background_color)
                original_image = Image.alpha_composite(new_bg_image.convert('RGBA'), original_image.convert('RGBA'))

            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            output_path = f"{processed_image_path}_{timestamp}_tmb.png"
            original_image.save(output_path)

            return jsonify({'filename': output_path})

        return jsonify({'error': 'Processed image not provided'})