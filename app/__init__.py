from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from datetime import timedelta
db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://****:******@localhost/hyperock"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=365)
    app.secret_key = '********'

    db.init_app(app)
    migrate.init_app(app, db)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login_get'
    login_manager.init_app(app)

    from .models import User
    @login_manager.user_loader
    def load_user(uid):
        return User.query.get(uid)

    
    
    # models

    from .main import main as main_bp
    app.register_blueprint(main_bp)
    
    from .admin import admin as admin_bp
    app.register_blueprint(admin_bp)

    from .auth import auth as auth_bp
    app.register_blueprint(auth_bp)

    return app
    


