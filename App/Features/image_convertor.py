from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os
from PIL import Image

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp', 'svg'}
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
STATIC_FOLDER = os.path.join(os.getcwd(), 'static')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def convert_image_route(app):
    @app.route('/api/image_convertor', methods=['POST'])
    def convert_image():
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            
            output_format = request.form.get('output_format', '').lower()
            if output_format not in ALLOWED_EXTENSIONS:
                return jsonify({'error': 'Invalid output format'}), 400
            
            output_path = os.path.join(STATIC_FOLDER, f'converted_{filename}.{output_format}')
            
            try:
                image = Image.open(os.path.join(UPLOAD_FOLDER, filename))
                image.save(output_path)
                converted_image_url = f"/static/converted_{filename}.{output_format}"
                print(converted_image_url, "aaaaluuu")
                return jsonify({'converted_image_url': converted_image_url}), 200
            except Exception as e:
                return jsonify({'error': f'Error converting image: {str(e)}'}), 500
        else:
            return jsonify({'error': 'Unsupported file format'}), 400

