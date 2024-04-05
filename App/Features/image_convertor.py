from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from pathlib import Path
from PIL import Image
import numpy as np

UPLOAD_FOLDER = Path.cwd() / 'uploads'
STATIC_FOLDER = Path.cwd() / 'static'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp', 'svg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
            
            output_format = request.form.get('output_format', '').lower().strip()
            if output_format not in ALLOWED_EXTENSIONS:
                return jsonify({'error': 'Invalid output format. Allowed formats: ' + ', '.join(ALLOWED_EXTENSIONS)}), 400
            
            output_path = STATIC_FOLDER / f'converted_{filename}.{output_format}'
            
            if output_format == 'svg':
                # Convert the image to SVG format using convert_to_svg function
                input_image_path = UPLOAD_FOLDER / filename
                output_svg_path = output_path
                convert_to_svg(input_image_path, output_svg_path)
            else:
                # Convert the image to the specified format (other than SVG)
                image = Image.open(UPLOAD_FOLDER / filename)
                image.save(output_path)
            
            converted_image_url = f"/static/converted_{filename}.{output_format}"
            return jsonify({'converted_image_url': converted_image_url}), 200
        except Exception as e:
            return jsonify({'error': f'Error converting image: {str(e)}'}), 500

def convert_to_svg(image_path, output_path):
    # Convert image to grayscale
    img = Image.open(image_path).convert('L')
    
    # Convert grayscale image to BMP format
    bmp_path = image_path.with_suffix('.bmp')
    img.save(bmp_path)
    
    # Convert BMP to SVG
    width, height = img.size
    block_size = 1
    svg_code = f'<svg xmlns="http://www.w3.org/2000/svg" version="1.1" width="{width}" height="{height}" viewBox="0 0 {width} {height}">'
    
    for y in range(0, height, block_size):
        for x in range(0, width, block_size):
            block = img.crop((x, y, x + block_size, y + block_size))
            if np.mean(np.array(block)) < 80:  # Thresholding to determine black or white
                color = 'black'
            else:
                color = 'white'
            svg_code += f'<rect x="{x}" y="{y}" width="{block_size}" height="{block_size}" fill="{color}" stroke="none"/>'
    
    svg_code += '</svg>'
    
    # Save SVG to output path
    with open(output_path, 'w') as f:
        f.write(svg_code)
    
    # Remove temporary BMP file
    bmp_path.unlink()
