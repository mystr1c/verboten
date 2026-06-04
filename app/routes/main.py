from flask import Blueprint, render_template
from app.middleware.auth import login_required_redirect

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
@login_required_redirect
def index():
    return render_template('index.html')
