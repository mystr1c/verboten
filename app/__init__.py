from flask import Flask
from flask_session import Session
from flask_socketio import SocketIO
from app.config import settings
from app.routes.main import main_bp
from app.routes.auth import auth_bp
from app.routes.api import api_bp
from app.database import init_db

socketio = SocketIO()

from app.sockets import twitch_chat

def create_app(config_class=settings):

    app = Flask(__name__)
    app.config.from_object(config_class)

    Session(app)
    socketio.init_app(app)

    init_db()

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(api_bp)
    
    return app
