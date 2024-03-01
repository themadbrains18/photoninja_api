# inpaint.py
import cv2
import numpy as np
from flask import Flask, request, jsonify
from datetime import datetime
from PIL import Image
import io
import base64

def inpaint_colored_object(original_image_blob, mask_blob):
    original_image = np.array(Image.open(io.BytesIO(original_image_blob)))
    mask = np.array(Image.open(io.BytesIO(mask_blob)))

    if mask.ndim == 3:
        mask = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)

    mask = cv2.convertScaleAbs(mask)

    inpainted_result = cv2.inpaint(original_image, mask, inpaintRadius=3, flags=cv2.INPAINT_TELEA)

    retval, buffer = cv2.imencode('.png', inpainted_result)
    inpainted_base64 = base64.b64encode(buffer).decode('utf-8')

    return inpainted_base64

def inpaint_route(app):
    @app.route('/api/remove-colored-object', methods=['POST'])
    def remove_colored_object():
        try:
            if 'originalImage' not in request.files or 'coloredMask' not in request.files:
                return jsonify({'error': 'Invalid request data'})

            original_image_blob = request.files['originalImage'].read()
            colored_mask_blob = request.files['coloredMask'].read()

            inpainted_result_base64 = inpaint_colored_object(original_image_blob, colored_mask_blob)

            return jsonify({'inpaintedResult': inpainted_result_base64})

        except IndexError:
            return jsonify({'error': 'Index error - check if the provided data has the correct structure'})

        except Exception as e:
            return jsonify({'error': str(e)})
