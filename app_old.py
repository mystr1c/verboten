from flask import Flask, jsonify, render_template, redirect, session, url_for, request
from flask_session import Session
from flask_socketio import SocketIO, emit, join_room, leave_room
import asyncio
import websockets
import threading
import time
import logging
import requests
import os
import random, json
from dotenv import load_dotenv

load_dotenv(dotenv_path="env.config")

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'super-secret-key-change-in-production')

app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = 'flask_session'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True

Session(app)
socketio = SocketIO(
    app,
    cors_allowed_origins='*',
    manage_session=False,
    async_mode='threading',
    ping_timeout=60,
    ping_interval=25,
    logger=False,
    engineio_logger=False
)

logging.basicConfig(level=logging.INFO)
logging.getLogger('websockets').setLevel(logging.WARNING)

twitch_connections = {} # channel -> {'thread': Thread, 'stop_event': Event}
connections_lock = threading.Lock() 

@app.route('/')
def index():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template("index.html")

@app.route('/login')
def login():
    return render_template("login.html")

@app.route('/auth/twitch')
def auth_twitch():
    client_id = os.getenv('TWITCH_CLIENT_ID')
    redirect_uri = os.getenv('TWITCH_REDIRECT_URI')
    scopes = os.getenv('TWITCH_OAUTH_SCOPES', 'user:read:chat')
    
    auth_url = f'https://id.twitch.tv/oauth2/authorize?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code&scope={scopes}'
    return redirect(auth_url)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    if not code:
        return redirect(url_for('login'))
    
    client_id = os.getenv('TWITCH_CLIENT_ID')
    client_secret = os.getenv('TWITCH_CLIENT_SECRET')
    redirect_uri = os.getenv('TWITCH_REDIRECT_URI')
    
    token_url = 'https://id.twitch.tv/oauth2/token'
    data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'code': code,
        'grant_type': 'authorization_code',
        'redirect_uri': redirect_uri
    }
    
    response = requests.post(token_url, data=data)
    if response.status_code != 200:
        return redirect(url_for('login'))
    
    token_data = response.json()
    access_token = token_data.get('access_token')
    
    user_url = 'https://api.twitch.tv/helix/users'
    headers = {
        'Client-ID': client_id,
        'Authorization': f'Bearer {access_token}'
    }
    
    user_response = requests.get(user_url, headers=headers)
    if user_response.status_code != 200:
        return redirect(url_for('login'))
    
    user_data = user_response.json()
    user_info = user_data['data'][0]
    
    session['user'] = {
        'id': user_info['id'],
        'login': user_info['login'],
        'display_name': user_info['display_name'],
        'profile_image_url': user_info['profile_image_url']
    }
    session['access_token'] = access_token
    
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/api/user')
def get_user():
    if 'user' not in session:
        return jsonify({'authenticated': False})
    return jsonify({'authenticated': True, 'user': session['user']})

@app.route('/api/channel')
def get_channel():
    if 'user' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    return jsonify({'channel': session['user']['login']})

@app.route('/api/word')
def get_random_word():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(base_dir, 'data', 'words.json')
    
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    words = list(data.keys())
    random_word = random.choice(words)
    
    return jsonify({
        'word': random_word,
        'forbidden': data[random_word]
    })

@socketio.on('connect_chat')
def handle_connect_chat(data):
    try:
        if not data:
            emit('chat_error', {'message': 'Channel name required'})
            return

        channel = data.get('channel', '')
        if not channel:
            emit('chat_error', {'message': 'Channel name required'})
            return

        channel = channel.lower()
        room = f'chat_{channel}'
        join_room(room)

        # Просто просим “обеспечить воркер”, внутри он сам решит, нужен новый или нет
        start_twitch_connection(channel)

        emit('chat_connected', {'channel': channel})
    except Exception as e:
        emit('chat_error', {'message': f'Error: {str(e)}'})


@socketio.on('disconnect_chat')
def handle_disconnect_chat(data):
    if not data:
        return
    
    channel = data.get('channel', '').lower()
    if not channel:
        return
    
    room = f'chat_{channel}'
    leave_room(room)



async def connect_to_twitch(channel: str, stop_event: threading.Event):
    uri = 'wss://irc-ws.chat.twitch.tv:443'

    try:
        async with websockets.connect(uri) as websocket:
            await websocket.send('CAP REQ :twitch.tv/tags twitch.tv/commands twitch.tv/membership')
            await websocket.send(f'NICK justinfan{int(time.time() % 10000)}')
            await websocket.send(f'JOIN #{channel}')

            socketio.emit(
                'chat_status',
                {'channel': channel, 'status': 'connected'},
                room=f'chat_{channel}',
            )

            async for message in websocket:
                # Поток попросили остановиться – выходим из цикла [web:71][web:123]
                if stop_event.is_set():
                    break

                if 'PING' in message:
                    await websocket.send('PONG :tmi.twitch.tv')
                elif 'PRIVMSG' in message:
                    parsed = parse_twitch_message(message)
                    if parsed:
                        socketio.emit('chat_message', parsed, room=f'chat_{channel}')
                elif '376' in message:
                    socketio.emit(
                        'chat_status',
                        {'channel': channel, 'status': 'joined'},
                        room=f'chat_{channel}',
                    )
                elif 'NOTICE' in message and 'Login unsuccessful' in message:
                    socketio.emit(
                        'chat_error',
                        {'message': 'Failed to join channel', 'channel': channel},
                        room=f'chat_{channel}',
                    )

    except Exception as e:
        socketio.emit(
            'chat_error',
            {'message': str(e), 'channel': channel},
            room=f'chat_{channel}',
        )

    finally:
        # Аккуратно чистим запись, если это ещё “актуальный” воркер
        with connections_lock:
            conn = twitch_connections.get(channel)
            if conn and conn['stop_event'] is stop_event:
                del twitch_connections[channel]

        socketio.emit(
            'chat_status',
            {'channel': channel, 'status': 'disconnected'},
            room=f'chat_{channel}',
        )


def parse_twitch_message(message):
    parts = message.split(';')
    username = 'Unknown'
    text = ''
    
    for part in parts:
        if part.startswith('display-name='):
            username = part.split('=', 1)[1]
        elif 'PRIVMSG' in part:
            privmsg_parts = part.split(':')
            if len(privmsg_parts) >= 3:
                text = ':'.join(privmsg_parts[2:]).strip()
    
    return {'username': username, 'text': text} if text else None

def start_twitch_connection(channel: str):
    channel = channel.lower()

    with connections_lock:
        conn = twitch_connections.get(channel)

        # Если поток уже есть и жив – новый не создаём [web:116][web:67]
        if conn is not None and conn['thread'].is_alive():
            return

        stop_event = threading.Event()

        thread = threading.Thread(
            target=lambda: asyncio.run(connect_to_twitch(channel, stop_event)),
            daemon=True,
        )

        twitch_connections[channel] = {
            'thread': thread,
            'stop_event': stop_event,
        }

        thread.start()

def stop_twitch_connection(channel: str):
    with connections_lock:
        conn = twitch_connections.get(channel)
        if not conn:
            return
        conn['stop_event'].set()


if __name__ == '__main__':
    os.makedirs('flask_session', exist_ok=True)
    socketio.run(app, debug=True, port=5000, allow_unsafe_werkzeug=True)
