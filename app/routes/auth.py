from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import User
from app.forms import LoginForm, RegisterForm
from app.extensions import db

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.dashboard_view'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            flash("登入成功", "success")
            return redirect(url_for('dashboard.dashboard_view'))
        flash("登入失敗，請確認帳號或密碼", "danger")
    
    return render_template('login.html', form=form)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.dashboard_view'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        exist = User.query.filter_by(username=form.username.data).first()
        if exist:
            flash("帳號已存在", "danger")
        else:
            user = User(
                username=form.username.data,
                password=generate_password_hash(form.password.data)
            )
            db.session.add(user)
            db.session.commit()
            flash("註冊成功，請登入", "success")
            return redirect(url_for('auth.login'))
    
    return render_template('register.html', form=form)

@auth.route('/logout')
def logout():
    logout_user()
    flash("你已登出", "info")
    return redirect(url_for('auth.login'))