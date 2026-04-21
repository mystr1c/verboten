from app import socketio
from flask_socketio import emit, join_room, leave_room
from app.services.twitch_irc import start_twitch_connection

def on_twitch_event(reason: str, data: dict):
    socketio.emit(
                reason,
                data,
                room=f"chat_{data['channel']}"
            )

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
        start_twitch_connection(channel, on_twitch_event)

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
