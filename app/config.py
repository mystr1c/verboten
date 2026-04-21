from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    SECRET_KEY: str

    SESSION_TYPE: str = "filesystem"
    SESSION_FILE_DIR: str = 'flask_session'
    SESSION_PERMANENT: bool = False
    SESSION_USE_SIGNER: bool = True

    TWITCH_IRC_URI: str = 'wss://irc-ws.chat.twitch.tv:443'

    TWITCH_CLIENT_ID: str 
    TWITCH_CLIENT_SECRET: str
    TWITCH_REDIRECT_URI: str
    TWITCH_OAUTH_SCOPES: str = 'user:read:chat'

    DB_CONNECT: str

    model_config = SettingsConfigDict(env_file=".env", extra='ignore')

settings = Settings()
