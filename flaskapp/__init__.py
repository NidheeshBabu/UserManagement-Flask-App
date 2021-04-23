
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect


app = Flask(__name__)



app.config['SECRET_KEY'] = 'bdd6e371570eb1ff9c525ce63088ddae0b2f037a519fa8350aa777ee4c7812f32046318b7ff0732c8bd41e587da4684027b4'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sample.db'
db = SQLAlchemy(app)

bcrypt = Bcrypt(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

migrate = Migrate(app, db)

csrf = CSRFProtect(app)

from flaskapp import routes

