from PIL import Image
from rembg import remove
from flask import jsonify, request, send_from_directory
from flask_cors import cross_origin
import os
from datetime import datetime
from werkzeug.utils import secure_filename
import cv2

ALLOWED_EXTENSIONS = {'png', 'webp', 'jpg', 'jpeg', 'gif'}
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
BACKGROUND_FOLDER = os.path.join(os.getcwd(), 'backgrounds')  # Path to the folder containing background images

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Route for uploading an image
def profile_maker(app):
    @app.route('/api/profile_maker', methods=['POST'])
    @cross_origin()
    def upload_file_for_profile_maker():
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'})
        
        file = request.files['file']
        
        if file.filename == '' or not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file'})
        
        # Save the uploaded file
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # Process the uploaded image
        output_filename = process_image(filepath)
        
        if output_filename is None:
            return jsonify({'error': 'Failed to process image'})
        
        return jsonify({'profilePics': output_filename})

# Function to process the uploaded image with multiple background images
def process_image(filepath):
    if filepath is None:
        return None
    
    background_filenames = [os.path.join(BACKGROUND_FOLDER, bg_file) for bg_file in os.listdir(BACKGROUND_FOLDER)]
    
    processed_filenames = []  # List to store processed image filenames
    
    for background_filename in background_filenames:
        # Remove background from the uploaded image
        with open(filepath, "rb") as f_in:
            with open("output.png", "wb") as f_out:
                f_out.write(remove(f_in.read()))

        # Open the processed image
        processed_image = Image.open("output.png")
        
        # Open the background image
        background_image = Image.open(background_filename)
        
        # Resize the background image to match the size of the processed image
        background_image = background_image.resize(processed_image.size)
        
        # Paste processed image onto the background
        background_image.paste(processed_image, (0, 0), processed_image)
        
        # Save the processed image
        processed_filename = f"processed_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
        processed_filepath = os.path.join("static", processed_filename)
        background_image.save(processed_filepath)
        
        # Append the processed filename to the list
        processed_filenames.append(processed_filename)
        
        # Remove the temporary processed image
        os.remove("output.png")
    
    # Transform processed filenames to absolute URLs without the extra prefix
    processed_urls = [request.host_url + f"static/{filename}" for filename in processed_filenames]
    return processed_urls

# Route to serve static files (processed images)
def serve_static_file(app):
    @app.route('/static/<path:filename>')
    def serve_file(filename):
        return send_from_directory('static', filename)
