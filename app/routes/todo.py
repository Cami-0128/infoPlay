from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import ToDo, Record
from app.extensions import db
from datetime import datetime

account = Blueprint('account', __name__)

@account.route('/', methods=['GET', 'POST'])
@login_required
def account_home():
    if request.method == 'POST':
        # 處理待辦事項新增
        if 'content' in request.form and request.form['content'].strip():
            new_todo = ToDo(content=request.form['content'], user_id=current_user.id)
            db.session.add(new_todo)
            db.session.commit()
            flash("新增待辦事項成功", "success")
            return redirect(url_for('account.account_home'))
        
        # 處理記帳新增
        elif 'description' in request.form and 'amount' in request.form:
            try:
                amount = float(request.form['amount'])
                new_record = Record(
                    description=request.form['description'], 
                    amount=amount,
                    user_id=current_user.id, 
                    date=datetime.now()
                )
                db.session.add(new_record)
                db.session.commit()
                flash("新增記帳成功", "success")
                return redirect(url_for('account.account_home'))
            except ValueError:
                flash("金額格式錯誤", "danger")
                return redirect(url_for('account.account_home'))
    
    # GET 請求：顯示頁面
    todos = ToDo.query.filter_by(user_id=current_user.id).all()
    recs = Record.query.filter_by(user_id=current_user.id).order_by(Record.date.desc()).all()
    return render_template('account.html', todos=todos, records=recs)

@account.route('/toggle_todo/<int:id>')
@login_required
def toggle_todo(id):
    todo = ToDo.query.get_or_404(id)
    if todo.user_id == current_user.id:
        todo.done = not todo.done
        db.session.commit()
        flash("待辦事項狀態已更新", "success")
    return redirect(url_for('account.account_home'))

@account.route('/delete_todo/<int:id>')
@login_required  
def delete_todo(id):
    todo = ToDo.query.get_or_404(id)
    if todo.user_id == current_user.id:
        db.session.delete(todo)
        db.session.commit()
        flash("待辦事項已刪除", "success")
    return redirect(url_for('account.account_home'))

@account.route('/delete_record/<int:id>')
@login_required
def delete_record(id):
    record = Record.query.get_or_404(id)
    if record.user_id == current_user.id:
        db.session.delete(record)
        db.session.commit()
        flash("記帳記錄已刪除", "success")
    return redirect(url_for('account.account_home'))