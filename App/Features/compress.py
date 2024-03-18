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

def timestampsWithFilename(filename):
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"static/{filename}_{timestamp}_tmb.png"

def compress_route(app):
    @app.route('/api/upload-compress', methods=['POST'])
    @cross_origin(supports_credentials=True)
    def upload_file_for_compress():
        if request.method == 'POST':
            if 'file' not in request.files:
                return jsonify({'error': 'No file part'})

            file = request.files['file']
            if file.filename == '' or not allowed_file(file.filename):
                return jsonify({'error': 'Invalid file'})
            
            filename = secure_filename(file.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)
            
            print("session store before")
            session['original_img_for_compression'] = file_path
            print("session store after")
            return jsonify({'filename': filename})

        return jsonify({'error': 'Invalid request'})

def compressing(app):
    @app.route('/api/compressing', methods=['POST'])
    @cross_origin(supports_credentials=True)
    def compressing_file():
        quality = request.form.get('quality')

        session_file_path = session.get('original_img_for_compression')
        print(session_file_path,"sfajksdfhlsdfhlk")
        if session_file_path:
            original_image = cv2.imread(session_file_path, cv2.IMREAD_COLOR)

            if original_image is not None:
                jpeg_quality = int(quality) if quality.isdigit() else 60

                # Generate timestamp
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                filename = os.path.basename(session_file_path)

                # Modify the file name with timestamp
                compressed_filename = f"{filename}_{timestamp}.jpg"

                # Define the path for the compressed image in the 'static' folder
                compressed_file_path = os.path.join('static', compressed_filename)

                # Compress and save the image
                cv2.imwrite(compressed_file_path, original_image, [cv2.IMWRITE_JPEG_QUALITY, jpeg_quality])

                # Return response with filename and quality
                return jsonify({'filename': compressed_file_path, 'quality': jpeg_quality})
            else:
                return jsonify({'error': 'Failed to read the original image'})

        return jsonify({'error': 'Original image path not found in session'})
