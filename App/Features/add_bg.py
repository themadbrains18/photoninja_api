from flask import Flask, request, jsonify, session, send_file
from PIL import Image
from flask import session
from werkzeug.utils import secure_filename
from datetime import datetime
from flask_cors import CORS, cross_origin

def add_bg_route(app):
    @app.route('/api/add-bg', methods=['POST'])
    @cross_origin(supports_credentials=True)
    def apply_background():
        background_color = request.form.get('background_color')
        processed_image_path = session.get('bg_removed_img')
        
        if processed_image_path:
            original_image = Image.open(processed_image_path)

            # Apply background color if provided
            if background_color:
                new_bg_image = Image.new('RGB', original_image.size, color=background_color)
                original_image = Image.alpha_composite(new_bg_image.convert('RGBA'), original_image.convert('RGBA'))

            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")     
            output_path = f"{processed_image_path}_{timestamp}_tmb.png"
            original_image.save(output_path)
         
            session['added-bg-image'] = output_path

            return jsonify({'filename': output_path})

        return jsonify({'error': 'Processed image not found in session'})
