from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from pathlib import Path
import aspose.words as aw
from PIL import Image

doc = aw.Document()

builder = aw.DocumentBuilder(doc)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp', 'svg'}
UPLOAD_FOLDER = Path.cwd() / 'uploads'
STATIC_FOLDER = Path.cwd() / 'static'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def convert_to_svg(image_path, output_path):
    # Create a new document
    doc = aw.Document()

    # Get the DocumentBuilder
    builder = aw.DocumentBuilder(doc)

    # Load the image into the document
    builder.insert_image(image_path)

    # Save the document in SVG format
    doc.save(output_path, aw.SaveFormat.SVG)

def convert_image_route(app):
    @app.route('/api/image_convertor', methods=['POST'])
    def convert_image():
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        if not allowed_file(file.filename):
            return jsonify({'error': 'Unsupported file format. Allowed formats: ' + ', '.join(ALLOWED_EXTENSIONS)}), 400

        try:
            filename = secure_filename(file.filename)
            file.save(UPLOAD_FOLDER / filename)
            
            output_format = request.form.get('output_format', '').lower()
            if output_format not in ALLOWED_EXTENSIONS:
                return jsonify({'error': 'Invalid output format. Allowed formats: ' + ', '.join(ALLOWED_EXTENSIONS)}), 400
            
            output_path = STATIC_FOLDER / f'converted_{filename}.{output_format}'
            
            if output_format == 'svg':
                # Convert image to SVG using Aspose.Words
                convert_to_svg(UPLOAD_FOLDER / filename, output_path)
            else:
                # Save the image in the desired format
                image = Image.open(UPLOAD_FOLDER / filename)
                image.save(output_path)
            
            converted_image_url = f"/static/converted_{filename}.{output_format}"
            return jsonify({'converted_image_url': converted_image_url}), 200
        except Exception as e:
            return jsonify({'error': f'Error converting image: {str(e)}'}), 500
