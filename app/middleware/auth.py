from typing import Callable
from flask import session, redirect, url_for, jsonify
from functools import wraps

def login_required(func: Callable):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'user' not in session:
            return jsonify({
                'success': False,
                'data': None,
                'error': 'Unauthorized'
            }), 401
        return func(*args, **kwargs)
    return wrapper

def login_required_redirect(func: Callable):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('auth.login'))         
        return func(*args, **kwargs)
    return wrapper