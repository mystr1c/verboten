from dotenv import load_dotenv
import os

load_dotenv(dotenv_path="env.config")

class Config:
    SECRET_KEY =  os.environ.get('SECRET_KEY')

    SESSION_TYPE = "filesystem"
    SESSION_FILE_DIR = 'flask_session'
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True

    TWITCH_IRC_URI = 'wss://irc-ws.chat.twitch.tv:443'

    TWITCH_CLIENT_ID =  os.environ.get('TWITCH_CLIENT_ID')
    TWITCH_CLIENT_SECRET =  os.environ.get('TWITCH_CLIENT_SECRET')
    TWITCH_REDIRECT_URI = os.getenv('TWITCH_REDIRECT_URI')
    TWITCH_OAUTH_SCOPES = os.getenv('TWITCH_OAUTH_SCOPES', 'user:read:chat')