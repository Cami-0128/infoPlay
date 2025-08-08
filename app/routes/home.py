from flask import Blueprint, redirect, url_for

home_bp = Blueprint('home', __name__)

@home_bp.route('/')
def home_redir():
    return redirect(url_for('dashboard.dashboard_view'))
