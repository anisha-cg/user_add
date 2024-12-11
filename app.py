import base64
from flask import Flask, render_template, request, redirect, url_for
import qrcode
from pymongo.mongo_client import MongoClient
import os
from datetime import datetime
import os
import warnings
from datetime import datetime
from bson.objectid import ObjectId
from flask import (Flask, flash, get_flashed_messages, jsonify, redirect,
                   render_template, request, session, url_for)
from flask_httpauth import HTTPBasicAuth
from flask_session import Session
from rich import print
from dotenv import load_dotenv

load_dotenv()

warnings.filterwarnings("ignore")
app = Flask(__name__, static_url_path='/static')
app.config['SECRET_KEY'] = 'secretkey'
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)
auth = HTTPBasicAuth()
# Dictionary to hold username:password pairs for each route
credentials = {
    "/admin": (os.getenv('ADMIN_USERNAME'), os.getenv('ADMIN_PASSWORD')),
}
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

@auth.verify_password
def verify_password(username, password):
    route = request.path
    route_credentials = credentials.get(route)
    if route_credentials:
        return username == route_credentials[0] and password == route_credentials[1]
    return False


uri = os.getenv('MONGO_URI')
uri = MongoClient(uri)
try:
    uri.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
    db = uri['KrishnaData']
    collection = db['clgData']
except Exception as e:
    raise Exception("Unable to connect to MongoDB: ", e)



class Handler:

    @staticmethod
    def admin_alert(alert=None):
        # Flash the error message
        flash(alert, 'Msg')
        return redirect('/admin')
    
    @staticmethod
    def user_alert(alert=None):
        # Flash the error message
        flash(alert, 'Msg')
        return redirect('/user')


def allowed_file(filename):
    """Check if the uploaded file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Define a custom Jinja2 filter
@app.template_filter('b64encode')
def b64encode_filter(data):
    """Encodes bytes into Base64 string."""
    if isinstance(data, bytes):
        return base64.b64encode(data).decode('utf-8')
    return ""

@app.route('/')
def home():
    return redirect(url_for('admin'))


@app.route('/admin', methods=['GET', 'POST'])
@auth.login_required
def admin():
    if request.method == 'POST':
        print(f"{request = }")
        # Get form data
        name = request.form['name']
        post = request.form['post']
        roll_no = request.form['roll_no']
        branch = request.form['branch']
        semester = request.form['semester']
        team = request.form['team']
        photo = request.files['photo']
        
        # Save image in bytes if size < 5MB
        if photo and photo.content_length < 5 * 1024 * 1024:
            photo_bytes = photo.read()
            photo_base64 = base64.b64encode(photo_bytes).decode('utf-8')
        else:
            return Handler.admin_alert("Image size must be less than 5MB")

        # Generate unique ID
        unique_id = str(datetime.now().timestamp()).replace('.', '')


        if collection.find_one({'roll_no': roll_no}):
            return Handler.admin_alert("Roll number already exists")
        # Save data to MongoDB
        collection.insert_one({
            'unique_id': unique_id,
            'name': name,
            'post': post,
            'roll_no': roll_no,
            'branch': branch,
            'semester': semester,
            'team': team,
            'photo': photo_base64
        })

        # Generate QR code
        # qr = qrcode.make(f'/user/{unique_id}')
        # qr_path = os.path.join('static/qr_codes', f'{unique_id}.png')
        # qr.save(qr_path)

        return redirect(url_for('admin'))

    users = collection.find()
    return render_template('admin.html', users=users)

# ?unique_id=12345
@app.route('/user', methods=['GET'])
def user():
    if request.args.get('unique_id'):
        user_data = collection.find_one({'unique_id': request.args.get('unique_id')})
        
        # if user_data:
        return render_template('user_detail.html', user=user_data)
        # else:
        #     return Handler.user_alert("User not found")
    
    else:
        return render_template('user_detail.html', user=None, alert="User not found")
        

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')