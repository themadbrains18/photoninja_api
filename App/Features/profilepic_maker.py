from PIL import Image
from rembg import remove
from flask import jsonify, request, send_from_directory
from flask_cors import cross_origin
import os
from datetime import datetime
from werkzeug.utils import secure_filename
import requests
from io import BytesIO
import cv2

ALLOWED_EXTENSIONS = {'png', 'webp', 'jpg', 'jpeg', 'gif'}
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')

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
        
        output_url = f"{request.host_url}static/{output_filename}"
        
        return jsonify({'filename': output_url})

# Function to process the uploaded image
def process_image(filepath):
    
    if filepath is None:
        return None
    
    # Remove background from the cropped image
    with open(filepath, "rb") as f_in:
        with open("output.png", "wb") as f_out:
            f_out.write(remove(f_in.read()))

    # Open the processed image
    processed_image = Image.open("output.png")
    
    # Download the background image from the URL
    background_url = "https://images.pexels.com/photos/1571459/pexels-photo-1571459.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1"
    background_response = requests.get(background_url)
    background_image = Image.open(BytesIO(background_response.content))
    
    # Resize the background image to match the size of the processed image
    background_image = background_image.resize(processed_image.size)
    
    # Paste processed image onto the background
    background_image.paste(processed_image, (0, 0), processed_image)
    
    # Save the processed image
    processed_filename = f"processed_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
    processed_filepath = os.path.join("static", processed_filename)
    background_image.save(processed_filepath)
    
    # Remove the temporary processed image
    os.remove("output.png")
    
    return processed_filename


# Route to serve static files (processed images)
def serve_static_file(app):
    @app.route('/static/<path:filename>')
    def serve_file(filename):
        return send_from_directory('static', filename)
