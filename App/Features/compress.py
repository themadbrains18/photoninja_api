# compress.py
from flask import Flask, request, jsonify, session
from flask_cors import CORS, cross_origin
from flask_session import Session
import os
from datetime import datetime
from werkzeug.utils import secure_filename
import cv2

ALLOWED_EXTENSIONS = {'png', 'webp', 'jpg', 'jpeg', 'gif'}
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_timestamped_filename(filename):
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"{filename}_{timestamp}.jpg"

def compress_route(app):
    @app.route('/api/upload-compress', methods=['POST'])
    @cross_origin(supports_credentials=True)
    def upload_file_for_compress():
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'})

        file = request.files['file']
        if file.filename == '' or not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file'})

        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        return jsonify({'filename': filename})

def compressing(app):
    @app.route('/api/compressing', methods=['POST'])
    @cross_origin(supports_credentials=True)
    def compressing_file():
        quality = request.form.get('quality')
        file = request.files.get('file')

        if not file:
            return jsonify({'error': 'File not provided'})

        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        file.save(file_path)

        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found'})

        original_image = cv2.imread(file_path, cv2.IMREAD_COLOR)

        if original_image is not None:
            jpeg_quality = int(quality) if quality.isdigit() else 60

            compressed_filename = generate_timestamped_filename(filename)
            compressed_file_path = os.path.join('static', compressed_filename)

            cv2.imwrite(compressed_file_path, original_image, [cv2.IMWRITE_JPEG_QUALITY, jpeg_quality])

            return jsonify({'filename': compressed_file_path, 'quality': jpeg_quality})
        else:
            return jsonify({'error': 'Failed to read the original image'})




