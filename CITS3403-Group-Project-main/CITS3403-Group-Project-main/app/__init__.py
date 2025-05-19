from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf import CSRFProtect
from flask_migrate import Migrate
from .config import basedir

# Initialize the database and CSRF protection
db = SQLAlchemy()
csrf = CSRFProtect()

def create_app(config_name):
    app = Flask(__name__)

    app.config.from_object(config_name)

    from .routes import main
    app.register_blueprint(main)

    # Initialize extensions
    db.init_app(app)
    csrf.init_app(app)
    Migrate(app, db)

    # Flask-Login setup
    login_manager = LoginManager()
    login_manager.login_view = 'main.login'
    login_manager.session_protection = 'strong'
    login_manager.init_app(app)

    # Import your models so Flask-Login can load users
    from .models import User, Transaction, Group, GroupMembership, Category, Note, GroupType, GroupRole, GroupBalance

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # 3) Before *every* request, mark the session permanent (so it uses that 1 hr timeout)
    @app.before_request
    def make_session_permanent():
        session.permanent = True

    return app
