from flask import Blueprint, redirect, url_for, render_template, session, request
from app.config import Config
import requests

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login')
def login():
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))

@auth_bp.route('/auth/twitch')
def auth_twitch():
    client_id = Config.TWITCH_CLIENT_ID
    redirect_uri = Config.TWITCH_REDIRECT_URI
    scopes = Config.TWITCH_OAUTH_SCOPES

    auth_url = f'https://id.twitch.tv/oauth2/authorize?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code&scope={scopes}'
    return redirect(auth_url)

@auth_bp.route('/callback')
def callback():
    
    code = request.args.get('code')

    if not code:
        return redirect(url_for('auth.login'))
    
    client_id = Config.TWITCH_CLIENT_ID
    redirect_uri = Config.TWITCH_REDIRECT_URI
    client_secret = Config.TWITCH_CLIENT_SECRET

    token_url = 'https://id.twitch.tv/oauth2/token'

    parameters = {
        'client_id' : client_id,
        'client_secret' : client_secret,
        'code' : code,
        'grant_type' : 'authorization_code',
        'redirect_uri' : redirect_uri
    }

    response = requests.post(token_url, data = parameters)

    if response.status_code != 200:
        return redirect(url_for('auth.login'))
    
    token_data = response.json()
    access_token = token_data.get('access_token')

    get_users_url = "https://api.twitch.tv/helix/users"

    headers = {
        'Client-ID': client_id,
        'Authorization': f'Bearer {access_token}'
    }

    user_response = requests.get(get_users_url, headers=headers)
    if user_response.status_code != 200:
        return redirect(url_for('auth.login'))
    
    user_data = user_response.json()
    user_info = user_data['data'][0]

    session['user'] = {
        'id': user_info['id'],
        'login': user_info['login'],
        'display_name': user_info['display_name'],
        'profile_image_url': user_info['profile_image_url']
    }
    session['access_token'] = access_token


    return redirect(url_for('main.index'))