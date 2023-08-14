from flask import Flask
from flask_login import LoginManager

from app.config import SECRET_KEY
from app.user.views import blueprint as translate_blueprint
from app.user.models import db, User


def create_app():
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
    db.init_app(app)
    app.secret_key = SECRET_KEY
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'user.login'

    app.register_blueprint(translate_blueprint)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(user_id)
    
    with app.app_context():
        db.create_all()
    #     db.drop_all()
    
    return app
