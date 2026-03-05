from flask import Blueprint, session, jsonify
from pathlib import Path
import json
import random

api_bp = Blueprint('api', __name__)

def api_response(success, data=None, error=None, status_code=200):
    return jsonify({
        'success': success,
        'data': data,
        'error': error
    }), status_code

@api_bp.route('/api/user')
def get_user():
    if 'user' not in session:
        return api_response(success=False, error='Not authenticated', status_code=401)
    return api_response(success=True, data={'user': session['user']})
    
@api_bp.route('/api/channel')
def get_channel():
    if 'user' not in session:
        return api_response(success=False, error='Not authenticated', status_code=401)
    return api_response(success=True, data={'channel': session['user']['login']})

@api_bp.route('/api/word')
def get_random_word():
    
    BASE_DIR = Path(__file__).parent
    file_path = BASE_DIR / '..' / '..' / 'data' / 'words.json'

    with open(file_path, mode = "r", encoding="utf-8") as file:
        words = json.load(file)
    random_word = random.choice(list(words.keys()))
    forbidden_words = words[random_word]

    return api_response(success=True, data={'word': random_word, 'forbidden': forbidden_words})
