from PIL import ImageEnhance
from flask import Flask, request, jsonify, session
from flask_cors import CORS, cross_origin
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from PIL import Image


ALLOWED_EXTENSIONS = {'png', 'webp', 'jpg', 'jpeg', 'gif'}
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def apply_image_enhancer(image_path, factor=1.5):
    original_image = Image.open(image_path)
    
    enhancer = ImageEnhance.Contrast(original_image)
    enhanced_image = enhancer.enhance(factor)

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{secure_filename(image_path)}_enhanced_{timestamp}_tmb.png"
    output_path = os.path.join('static', filename)
    
    enhanced_image.save(output_path)

    session['enhanced_image'] = output_path
    return output_path

def image_enhance_route(app):
    @app.route('/api/enhance', methods=['POST'])
    @cross_origin(supports_credentials=True)
    def enhance_image():
        try:
            if 'file' not in request.files:
                return jsonify({'error': 'No file part'})

            file = request.files['file']
            if file.filename == '' or not allowed_file(file.filename):
                return jsonify({'error': 'Invalid file'})

            file_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file.filename))
            file.save(file_path)

            session['original_image'] = file_path
            enhanced_image_path = apply_image_enhancer(file_path)

            return jsonify({'filename': enhanced_image_path})

        except Exception as e:
            print(f"Error enhancing image: {e}")
            return jsonify({'error': 'Error enhancing image'})
