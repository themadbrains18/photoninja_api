from PIL import Image, ImageFilter, ImageEnhance
from flask import session, Flask, jsonify, request
import os
from datetime import datetime
from werkzeug.utils import secure_filename
from flask_cors import cross_origin

ALLOWED_EXTENSIONS = {'png', 'webp', 'jpg', 'jpeg', 'gif'}
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')

def timestampsWithFilename(filename):
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"static/{filename}_{timestamp}_tmb.png"

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def apply_black_and_white(image):
    return image.convert('L')

def apply_blur(image):
    return image.filter(ImageFilter.BLUR)

def apply_edge_enhance(image):
    return image.filter(ImageFilter.EDGE_ENHANCE)

def apply_emboss(image):
    return image.filter(ImageFilter.EMBOSS)

def apply_detail(image):
    return image.filter(ImageFilter.SMOOTH)

def apply_sharpen(image):
    return image.filter(ImageFilter.SHARPEN)

def apply_fade(image):
    alpha = 0.7
    return image.convert("RGBA")._new(image.getdata())._new((r, g, b, int(255 * alpha)) for (r, g, b) in image.getdata())

def apply_cold(image):
    return image.convert("RGB")._new((int(0.7 * r), int(0.7 * g), b) for (r, g, b) in image.convert("RGB").getdata())

def apply_warm(image):
    return image.convert("RGB")._new((int(1.2 * r), g, b) for (r, g, b) in image.convert("RGB").getdata())

def apply_pastel(image):
    return image.point(lambda p: p * 1.5)


def apply_chrome(image):
    return apply_contrast(apply_color(image, 1.5), 1.5)

def apply_mono(image):
    return image.convert("L")

def apply_noir(image):
    return apply_contrast(image.convert("L"), 2.0)

# Add your sepia filter implementation here
def apply_warm(image):
    sepia_data = [
        (0.393, 0.769, 0.189),
        (0.349, 0.686, 0.168),
        (0.272, 0.534, 0.131)
    ]

    sepia_image = Image.new('RGB', image.size)
    image = image.convert('RGB')

    for i in range(image.width):
        for j in range(image.height):
            pixel = image.getpixel((i, j))
            new_pixel = (
                int(pixel[0] * sepia_data[0][0] + pixel[1] * sepia_data[0][1] + pixel[2] * sepia_data[0][2]),
                int(pixel[0] * sepia_data[1][0] + pixel[1] * sepia_data[1][1] + pixel[2] * sepia_data[1][2]),
                int(pixel[0] * sepia_data[2][0] + pixel[1] * sepia_data[2][1] + pixel[2] * sepia_data[2][2])
            )
            sepia_image.putpixel((i, j), new_pixel)

    return sepia_image

# Additional filters
def apply_grayscale(image):
    return image.convert('L')

def apply_contour(image):
    return image.filter(ImageFilter.CONTOUR)

def apply_brightness(image, factor=1.5):
    enhancer = ImageEnhance.Brightness(image)
    return enhancer.enhance(factor)

def apply_color(image, factor=1.5):
    enhancer = ImageEnhance.Color(image)
    return enhancer.enhance(factor)

def apply_contrast(image, factor=1.5):
    enhancer = ImageEnhance.Contrast(image)
    return enhancer.enhance(factor)

# def apply_rotate(image, angle=45):
#     return image.rotate(angle)

def apply_filter(file_path, filter_name):
    original_image = Image.open(file_path)

    try:
        filter_functions = {
            'blur': apply_blur,
            'edgeEnhance': apply_edge_enhance,
            'emboss': apply_emboss,
            'detail': apply_detail,
            'sharpen': apply_sharpen,
            'warm': apply_warm,
            'grayscale': apply_grayscale,
            'contour': apply_contour,
            'brightness': apply_brightness,
            'color': apply_color,
            'contrast': apply_contrast,
            'fade': apply_fade,
            'cold': apply_cold,
            'pastel': apply_pastel,
            'chrome': apply_chrome,
            'mono': apply_mono,
            'noir': apply_noir,
        }

        if filter_name in filter_functions:
            filter_function = filter_functions[filter_name]
            original_image = filter_function(original_image)

        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{secure_filename(file_path)}_{timestamp}_tmb.png"
        output_path = os.path.join('static', filename)  
        original_image.save(output_path)

        session['applied-filter'] = output_path
        return output_path
    except Exception as e:
        print(f"Error applying filter: {e}")
        return None

def filter(app):
    @app.route('/api/filter', methods=['POST'])
    @cross_origin(supports_credentials=True)
    def apply_filter_image():
        filter_name = request.form.get('filterName')
        processed_image_path = session.get("imageFilter")

        if not processed_image_path or not os.path.exists(processed_image_path):
            return jsonify({'error': 'Invalid or missing image file'})

        output_path = apply_filter(processed_image_path, filter_name)
        return jsonify({'filename': output_path})
        if output_path:
            # Optionally, you can clean up the session or remove the original uploaded file
            # del session['imageFilter']
            # os.remove(processed_image_path)
            return jsonify({'filename': output_path})
        else:
            return jsonify({'error': 'Error applying filter'})
        
        
def apply_filter_route(app):
    @app.route('/api/apply-filter', methods=['POST'])
    @cross_origin(supports_credentials=True)
    def apply_filter_api():
        
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'})

        file = request.files['file']
        if file.filename == '' or not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file'})

        # Save the uploaded file to the UPLOAD_FOLDER
        file_path = os.path.join(UPLOAD_FOLDER, secure_filename(file.filename))
        file.save(file_path)

        session['imageFilter'] = file_path
        return jsonify({'message': 'File uploaded successfully'})
