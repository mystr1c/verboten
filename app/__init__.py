from flask import Flask
from flask_session import Session
from flask_socketio import SocketIO
from app.config import Config
from app.routes.main import main_bp
from app.routes.auth import auth_bp
from app.routes.api import api_bp

socketio = SocketIO()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    Session(app)
    socketio.init_app(app)

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(api_bp)
    
    return app