import threading
import asyncio
from app.config import Config
import websockets
import time

twitch_connections = {} # channel -> {'thread': Thread, 'stop_event': Event}
connections_lock = threading.Lock() 

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

async def connect_to_twitch(channel: str, stop_event: threading.Event, callback):
    uri = Config.TWITCH_IRC_URI

    try:
        async with websockets.connect(uri) as websocket:
            await websocket.send('CAP REQ :twitch.tv/tags twitch.tv/commands twitch.tv/membership')
            await websocket.send(f'NICK justinfan{int(time.time() % 10000)}')
            await websocket.send(f'JOIN #{channel}')

            callback('chat_status', {'channel': channel, 'status': 'connected'})


            async for message in websocket:
                if stop_event.is_set():
                    break

                if 'PING' in message:
                    await websocket.send('PONG :tmi.twitch.tv')
                elif 'PRIVMSG' in message:
                    parsed = parse_twitch_message(message)
                    if parsed:
                        callback('chat_message', {'message': parsed, 'channel': channel})
                elif '376' in message:
                    callback('chat_status', {'channel': channel, 'status': 'joined'})
                elif 'NOTICE' in message and 'Login unsuccessful' in message:
                    callback('chat_error', {'message': 'Failed to join channel', 'channel': channel})

    except Exception as e:
        callback('chat_error', {'message': str(e), 'channel': channel})

    finally:
        with connections_lock:
            conn = twitch_connections.get(channel)
            if conn and conn['stop_event'] is stop_event:
                del twitch_connections[channel]
        callback('chat_status', {'channel': channel, 'status': 'disconnected'})

def start_twitch_connection(channel: str, callback):
    channel = channel.lower()

    with connections_lock:
        conn = twitch_connections.get(channel)

        if conn is not None and conn['thread'].is_alive():
            return
        
        stop_event = threading.Event()

        thread = threading.Thread(
            target=lambda: asyncio.run(connect_to_twitch(channel, stop_event, callback)),
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
        