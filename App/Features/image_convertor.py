from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from pathlib import Path
import aspose.words as aw
from PIL import Image

# Set up file upload and static folders
UPLOAD_FOLDER = Path.cwd() / 'uploads'
STATIC_FOLDER = Path.cwd() / 'static'

# Define allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp', 'svg'}

# Function to check if file extension is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def convert_to_svg(image_path, output_path):
    doc = aw.Document()
    builder = aw.DocumentBuilder(doc)
    builder.insert_image(str(image_path))
    doc.save(str(output_path), aw.SaveFormat.SVG)

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
                convert_to_svg(UPLOAD_FOLDER / filename, output_path)
            else:
                image = Image.open(UPLOAD_FOLDER / filename)
                image.save(output_path)
            
            converted_image_url = f"/static/converted_{filename}.{output_format}"
            return jsonify({'converted_image_url': converted_image_url}), 200
        except Exception as e:
            return jsonify({'error': f'Error converting image: {str(e)}'}), 500
