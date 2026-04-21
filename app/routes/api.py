from flask import Blueprint, session, jsonify, request
from pathlib import Path
from app.services.game import insert_game, finish_game, find_game
from app.services.used_word import insert_used_word, make_used_word_finished
from app.services.leaderboard import add_points
from app.services.word import get_word_from_db

api_bp = Blueprint('api', __name__)

def api_response(success, data=None, error=None, status_code=200):
    return jsonify({
        'success': success,
        'data': data,
        'error': error
    }), status_code

@api_bp.route('/api/user', methods=['GET'])
def get_user():
    if 'user' not in session:
        return api_response(success=False, error='Not authenticated', status_code=401)
    return api_response(success=True, data={'user': session['user']})
    
@api_bp.route('/api/channel', methods=['GET'])
def get_channel():
    if 'user' not in session:
        return api_response(success=False, error='Not authenticated', status_code=401)
    return api_response(success=True, data={'channel': session['user']['login']})


#TODO: Добавить проверку существующей игры
@api_bp.route('/api/existing_game', methods=['GET'])
def check_if_game_exists():
    if 'user' not in session:
        return api_response(success=False, error='Not authenticated', status_code=401)
    data = find_game(session['user']['login'])
    return api_response(success=True, data=data) 

@api_bp.route('/api/word/<int:game_id>', methods=['GET'])
def get_random_word(game_id: int):
    if 'user' not in session:
        return api_response(success=False, error='Not authenticated', status_code=401)
    random_word, forbidden_words = get_word_from_db(game_id)
    insert_used_word(game_id, random_word)

    return api_response(success=True, data={'word': random_word, 'forbidden': forbidden_words})

@api_bp.route('/api/game', methods=['POST'])
def create_game():
    if 'user' not in session:
        return api_response(success=False, error='Not authenticated', status_code=401)
    create_game_request = request.get_json()
    round_limit = create_game_request['round_limit']
    time_limit = create_game_request['time_limit']

    result = insert_game(streamer_id=session['user']['db_id'], round_limit=round_limit, time_limit=time_limit)
    return api_response(success=True, data={'game_id': result})

@api_bp.route('/api/game/<int:game_id>', methods=['PATCH'])
def update_game(game_id):
    if 'user' not in session:
        return api_response(success=False, error='Not authenticated', status_code=401)
    update_game_request = request.get_json()
    if update_game_request.get('status') == 'finished':
        current_word = update_game_request.get('current_word')
        if current_word:
            make_used_word_finished(game_id=game_id, word=current_word)
        finish_game(game_id)
        return api_response(success=True)
    else:
        return api_response(success=False, error='Bad request', status_code=400)
    
@api_bp.route('/api/word/<int:game_id>/<string:word>', methods=['PATCH'])
def update_used_word(game_id, word):
    if 'user' not in session:
        return api_response(success=False, error='Not authenticated', status_code=401)
    update_used_word_request = request.get_json()
    if update_used_word_request.get('status') == 'finished':
        make_used_word_finished(game_id=game_id, word=word)
        return api_response(success=True)
    else:
        return api_response(success=False, error='Bad request', status_code=400)

@api_bp.route('/api/leaderboard/<int:game_id>', methods=['POST'])
def update_leaderboard(game_id):
    if 'user' not in session:
        return api_response(success=False, error='Not authenticated', status_code=401)
    update_leaderboard_request = request.get_json()
    nickname = update_leaderboard_request['nickname']
    add_points(game_id=game_id, nickname=nickname, score=1)
    return api_response(success=True)
