# main.py
from flask import Flask, session, jsonify
from flask_cors import CORS, cross_origin
from flask_session import Session
import os
import secrets
from datetime import datetime, timedelta
import glob
import redis
from datetime import timedelta


# @cross_origin(supports_credentials=True)


from App.Features.bg_remove import bg_remove_route
from App.Features.add_bg import add_bg_route
from App.Features.apply_filters import apply_filter_route
from App.Features.apply_filters import filter
from App.Features.compress import compress_route
from App.Features.compress import compressing
from App.Features.enhance import image_enhance_route
from App.Features.image_convertor import image_convertor_route

from App.Features.profilepic_maker import profile_maker_routes  # Import profile_maker function

app = Flask(__name__, static_url_path='/static', static_folder='static')
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')

SECRET_KEY = "changeme"
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

SESSION_TYPE = 'filesystem'
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False

app.config.from_object(__name__)

# app.secret_key = 'super secret key'
# app.config['SESSION_TYPE'] = 'filesystem'

# Initialize Flask-Session
Session(app)
# app.config.update(SESSION_COOKIE_SAMESITE="None", SESSION_COOKIE_SECURE=True)
# app.config.update(SESSION_COOKIE_SAMESITE="None", SESSION_COOKIE_SECURE=False)

CORS(app, resources={r"/static/*": {"origins": "*"}}, supports_credentials=True)
CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

@app.route('/')
def hello_world():
    return jsonify({'session': session.sid})


bg_remove_route(app)
add_bg_route(app)
apply_filter_route(app)
filter(app)
compress_route(app)
compressing(app)
image_enhance_route(app)
image_convertor_route(app)

# Integrate profile_maker functionality into the Flask application
profile_maker_routes(app)

def delete_old_files(folder_path, max_age_hours=1):
    current_time = datetime.now()
    max_age = timedelta(hours=max_age_hours)

    for file_path in glob.glob(os.path.join(folder_path, '*')):
        file_creation_time = datetime.fromtimestamp(os.path.getctime(file_path))
        if current_time - file_creation_time > max_age:
            os.remove(file_path)
            print(f"Deleted: {file_path}")

# Run the deletion for both folders
delete_old_files(os.path.join(os.getcwd(), 'static'))
delete_old_files(os.path.join(os.getcwd(), 'uploads'))

if __name__ == '__main__':
    app.run(debug=True, port="7001", host="0.0.0.0")
