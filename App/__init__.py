
# from flask import Flask
# from flask_session import Session  # Import Session from flask_session
# from flask_cors import CORS
# import secrets
# import os
# from app.Features.bg_remove import bg_remove_bp
# from app.Features.add_bg import add_bg_bp

# app = Flask(__name__)
# app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'api', 'uploads')  # Set the UPLOAD_FOLDER here

# # Use secrets.token_hex to generate a secure random key
# app.secret_key = secrets.token_hex(16)

# # Initialize Flask-Session
# server_session = Session(app)
# app.config.update(SESSION_COOKIE_SAMESITE="None", SESSION_COOKIE_SECURE=True)

# CORS(app, resources={r"/api/*": {"origins": "*"}})

# # Register your Blueprint with the app and pass the configuration
# app.register_blueprint(bg_remove_bp, UPLOAD_FOLDER=app.config['UPLOAD_FOLDER'])


# # Register Blueprints
# app.register_blueprint(bg_remove_bp)
# app.register_blueprint(add_bg_bp)

# if __name__ == '__main__':
#     app.run(debug=True)

