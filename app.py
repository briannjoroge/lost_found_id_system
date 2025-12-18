import os
from flask import Flask
from flask_login import LoginManager
from dotenv import load_dotenv

from db import init_db
from auth import auth_bp, load_user
from routes import main_bp

load_dotenv()

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'development_key_for_testing')

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

login_manager.user_loader(load_user)

app.register_blueprint(auth_bp)
app.register_blueprint(main_bp)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)