from flask import Flask 
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate

from webdata.config import Config

app = Flask(__name__)

app.config.from_object(Config)
thisConfig = Config()

app.config['SECRET_KEY'] = thisConfig.SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = thisConfig.DB_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = 10800
app.config['UPLOAD_FOLDER'] = thisConfig.UPLOAD_FOLDER

db = SQLAlchemy()
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'main.login'
login_manager.login_message_category = 'info'
db.init_app(app)
migrate = Migrate(app, db)
from webdata.main.routes import main
from webdata.admin.routes import admin

app.register_blueprint(main)
app.register_blueprint(admin, url_prefix='/admin')