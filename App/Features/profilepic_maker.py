from PIL import Image, ImageDraw
from rembg import remove
from flask import jsonify, request, send_from_directory
from flask_cors import cross_origin
from werkzeug.utils import secure_filename
import os
from datetime import datetime

ALLOWED_EXTENSIONS = {'png', 'webp', 'jpg', 'jpeg', 'gif'}
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
BACKGROUND_FOLDER = os.path.join(os.getcwd(), 'backgrounds')
STATIC_FOLDER = os.path.join(os.getcwd(), 'static')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def apply_ellipse_mask(image):
    width, height = image.size
    mask = Image.new("L", (width, height), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, width, height), fill=255)
    result = Image.new("RGBA", (width, height))
    result.paste(image, (0, 0), mask)
    return result

def process_image(filepath, background_filenames, start_index, end_index):
    processed_filenames = []

    for background_filename in background_filenames[start_index:end_index]:
        with open(filepath, "rb") as f_in:
            with open("output.png", "wb") as f_out:
                f_out.write(remove(f_in.read()))

        processed_image = Image.open("output.png")
        background_image = Image.open(background_filename)
        background_image = background_image.resize(processed_image.size)
        background_image.paste(processed_image, (0, 0), processed_image)
        
        processed_filename = f"processed_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
        processed_filepath = os.path.join(STATIC_FOLDER, processed_filename)
        
        # Apply circular mask
        circular_image = apply_ellipse_mask(background_image)
        
        circular_image.save(processed_filepath)
        
        processed_filenames.append(processed_filename)
        os.remove("output.png")
    
    processed_urls = [request.host_url + f"static/{filename}" for filename in processed_filenames]
    return processed_urls

def profile_maker_routes(app):
    @app.route('/api/profile_maker', methods=['POST'])
    @cross_origin()
    def upload_file_for_profile_maker():
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['file']
        
        if file.filename == '' or not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file'}), 400
        
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        page = int(request.args.get('page', 1))  # Get the page number from the query parameters
        num_backgrounds_per_page = 8  # Number of backgrounds to process per page
        start_index = (page - 1) * num_backgrounds_per_page
        end_index = page * num_backgrounds_per_page
        
        background_filenames = [os.path.join(BACKGROUND_FOLDER, bg_file) for bg_file in os.listdir(BACKGROUND_FOLDER)]
        
        processed_filenames = process_image(filepath, background_filenames, start_index, end_index)
        
        return jsonify({'profilePics': processed_filenames}), 200

    @app.route('/static/<path:filename>')
    def serve_file(filename):
        return send_from_directory('static', filename)
