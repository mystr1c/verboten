from app import create_app, socketio
from app.database import init_db

app = create_app()

if __name__ == '__main__':
    init_db()
    socketio.run(app, debug=True, port=5000)
