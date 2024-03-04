from flask import Flask, request, jsonify, session, send_file
from flask_cors import CORS, cross_origin
from flask_session import Session
import os
from datetime import datetime
from werkzeug.utils import secure_filename
import cv2
import numpy as np
from PIL import Image

ALLOWED_EXTENSIONS = {'png', 'webp', 'jpg', 'jpeg', 'gif', 'svg'}
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def timestampsWithFilename(filename):
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"static/{filename}_{timestamp}_tmb.png"

def convert_image(file_path, output_format):
    original_image = cv2.imread(file_path)
    
    # Convert color channels from BGR to RGB
    original_image_rgb = cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB)
    
    # Convert the image to the desired format
    if output_format == 'png':
        output_image_path = file_path.replace('.jpg', '_converted.png')
        cv2.imwrite(output_image_path, original_image)
    elif output_format == 'webp':
        output_image_path = file_path.replace('.jpg', '_converted.webp')
        cv2.imwrite(output_image_path, original_image, [cv2.IMWRITE_WEBP_QUALITY, 100])
    elif output_format == 'svg':
        # Convert to grayscale
        gray_image = cv2.cvtColor(original_image_rgb, cv2.COLOR_RGB2GRAY)
        
        # Use a threshold to create a binary image
        _, binary_image = cv2.threshold(gray_image, 128, 255, cv2.THRESH_BINARY)
        
        # Save the binary image as SVG
        output_image_path = file_path.replace('.jpg', '_converted.svg')
        Image.fromarray(binary_image).save(output_image_path)
    
    return output_image_path

def image_convertor_route(app):
    @app.route('/api/upload', methods=['POST'])
    @cross_origin(supports_credentials=True)
    def upload_file_for_image_converter():
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'})

        file = request.files['file']
        if file.filename == '' or not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file'})

        # Save the uploaded file to the UPLOAD_FOLDER
        file_path = os.path.join(UPLOAD_FOLDER, secure_filename(file.filename))
        file.save(file_path)

        session['imageFilter'] = file_path
        return jsonify({'message': 'File uploaded successfully'})
