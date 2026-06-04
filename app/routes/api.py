from flask import Blueprint, session, jsonify, request
from app.services.game import insert_game, finish_game, find_game
from app.services.used_word import insert_used_word, make_used_word_finished
from app.services.leaderboard import add_points
from app.services.word import get_word_from_db
from app.middleware.auth import login_required
from pydantic import ValidationError
from app.schemas.game import CreateGameSchema, UpdateGameSchema
from app.schemas.leaderboard import UpdateLeaderboardSchema
from app.schemas.word import UpdateUsedWord

api_bp = Blueprint('api', __name__)

def api_response(success, data=None, error=None, status_code=200):
    return jsonify({
        'success': success,
        'data': data,
        'error': error
    }), status_code

@api_bp.route('/api/user', methods=['GET'])
@login_required
def get_user():
    return api_response(success=True, data={'user': session['user']})
    
@api_bp.route('/api/channel', methods=['GET'])
@login_required
def get_channel():
    return api_response(success=True, data={'channel': session['user']['login']})

@api_bp.route('/api/existing_game', methods=['GET'])
@login_required
def check_if_game_exists():
    data = find_game(session['user']['login'])
    return api_response(success=True, data=data) 

@api_bp.route('/api/word/<int:game_id>', methods=['GET'])
@login_required
def get_random_word(game_id: int):
    random_word, forbidden_words = get_word_from_db(game_id)
    insert_used_word(game_id, random_word)
    return api_response(success=True, data={'word': random_word, 'forbidden': forbidden_words})

@api_bp.route('/api/game', methods=['POST'])
@login_required
def create_game():
    try:
        create_game_data = CreateGameSchema(**request.get_json())
    except ValidationError as e:
        return api_response(success=False, error=str(e), status_code=400)
    
    round_limit = create_game_data.round_limit
    time_limit = create_game_data.time_limit

    result = insert_game(streamer_id=session['user']['db_id'], round_limit=round_limit, time_limit=time_limit)
    return api_response(success=True, data={'game_id': result})

@api_bp.route('/api/game/<int:game_id>', methods=['PATCH'])
@login_required
def update_game(game_id):
    try:
        update_game_data = UpdateGameSchema(**request.get_json())
    except ValidationError as e:
        return api_response(success=False, error=str(e), status_code=400)
    
    if update_game_data.status == 'finished':
        current_word = update_game_data.current_word
        if current_word:
            make_used_word_finished(game_id=game_id, word=current_word)
        finish_game(game_id)
        return api_response(success=True)
    else:
        return api_response(success=False, error='Bad request', status_code=400)
    
@api_bp.route('/api/word/<int:game_id>/<string:word>', methods=['PATCH'])
@login_required
def update_used_word(game_id, word):
    try:
        update_used_word_data = UpdateUsedWord(**request.get_json())
    except ValidationError as e:
        return api_response(success=False, error=str(e), status_code=400)
    
    if update_used_word_data.status == 'finished':
        make_used_word_finished(game_id=game_id, word=word)
        return api_response(success=True)
    else:
        return api_response(success=False, error='Bad request', status_code=400)

@api_bp.route('/api/leaderboard/<int:game_id>', methods=['POST'])
@login_required
def update_leaderboard(game_id):
    try:
        update_leaderboard_data = UpdateLeaderboardSchema(**request.get_json())
    except ValidationError as e:
        return api_response(success=False, error=str(e), status_code=400)
    nickname = update_leaderboard_data.nickname
    add_points(game_id=game_id, nickname=nickname, score=1)
    return api_response(success=True)
