# account.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import ToDo, Record
from app.extensions import db
from datetime import datetime
import logging

account = Blueprint('account', __name__)
logger = logging.getLogger(__name__)

@account.route('/', methods=['GET', 'POST'])
@login_required
def account_home():
    """帳戶首頁 - 顯示待辦事項和記帳記錄"""
    
    # 添加調試信息
    print(f"DEBUG: Current user ID: {current_user.id}")
    print(f"DEBUG: Request method: {request.method}")
    
    if request.method == 'POST':
        # 處理待辦事項的新增
        content = request.form.get('content', '').strip()
        print(f"DEBUG: Form content: '{content}'")
        
        if not content:
            flash("請輸入待辦事項內容", "error")
            return redirect(url_for('account.account_home'))
        
        if len(content) > 200:  # 限制內容長度
            flash("待辦事項內容過長，請限制在200字以內", "error")
            return redirect(url_for('account.account_home'))
        
        try:
            # 創建新的待辦事項
            new_todo = ToDo(
                content=content,
                user_id=current_user.id,
                done=False
            )
            print(f"DEBUG: Created ToDo object: {new_todo}")
            
            db.session.add(new_todo)
            print("DEBUG: Added to session")
            
            db.session.commit()
            print("DEBUG: Committed to database")
            
            flash(f"成功新增待辦事項：{content}", "success")
            logger.info(f"User {current_user.id} added todo: {content}")
            
        except Exception as e:
            db.session.rollback()
            error_msg = f"Add todo error: {e}"
            print(f"DEBUG ERROR: {error_msg}")
            logger.error(error_msg)
            flash(f"新增待辦事項失敗：{str(e)}", "error")
        
        return redirect(url_for('account.account_home'))
    
    # GET 請求 - 顯示頁面
    try:
        print("DEBUG: Fetching todos...")
        todos = ToDo.query.filter_by(user_id=current_user.id).order_by(ToDo.id.desc()).all()
        print(f"DEBUG: Found {len(todos)} todos")
        
        print("DEBUG: Fetching records...")
        records = Record.query.filter_by(user_id=current_user.id).order_by(Record.date.desc()).limit(50).all()
        print(f"DEBUG: Found {len(records)} records")
        
        return render_template('account.html', todos=todos, records=records)
        
    except Exception as e:
        error_msg = f"Account home error: {e}"
        print(f"DEBUG ERROR: {error_msg}")
        logger.error(error_msg)
        flash("載入頁面時發生錯誤", "error")
        return render_template('account.html', todos=[], records=[])

@account.route('/debug_info')
@login_required
def debug_info():
    """顯示調試信息"""
    try:
        # 檢查數據庫連接
        db_status = "Connected"
        
        # 檢查用戶
        user_info = f"User ID: {current_user.id}, Username: {current_user.username}"
        
        # 檢查表是否存在
        from sqlalchemy import text
        
        # 檢查 ToDo 表
        todo_table_check = db.session.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='to_do';")).fetchone()
        todo_table_exists = todo_table_check is not None
        
        # 檢查 Record 表  
        record_table_check = db.session.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='record';")).fetchone()
        record_table_exists = record_table_check is not None
        
        # 統計數據
        todo_count = ToDo.query.filter_by(user_id=current_user.id).count()
        record_count = Record.query.filter_by(user_id=current_user.id).count()
        
        debug_info = {
            'database_status': db_status,
            'user_info': user_info,
            'todo_table_exists': todo_table_exists,
            'record_table_exists': record_table_exists,
            'todo_count': todo_count,
            'record_count': record_count,
        }
        
        return f"<pre>{str(debug_info)}</pre>"
        
    except Exception as e:
        return f"Debug error: {str(e)}"

@account.route('/test_add_todo')
@login_required  
def test_add_todo():
    """測試直接添加待辦事項"""
    try:
        test_todo = ToDo(
            content="測試待辦事項",
            user_id=current_user.id,
            done=False
        )
        
        db.session.add(test_todo)
        db.session.commit()
        
        return "成功添加測試待辦事項！"
        
    except Exception as e:
        db.session.rollback()
        return f"添加失敗：{str(e)}"

@account.route('/toggle_todo/<int:id>', methods=['GET', 'POST'])
@login_required
def toggle_todo(id):
    """切換待辦事項完成狀態"""
    todo = ToDo.query.filter_by(id=id, user_id=current_user.id).first()
    if not todo:
        flash("找不到該待辦事項", "error")
        return redirect(url_for('account.account_home'))
    
    try:
        todo.done = not todo.done
        db.session.commit()
        status = "完成" if todo.done else "未完成"
        flash(f"待辦事項已標記為{status}", "success")
        logger.info(f"User {current_user.id} toggled todo {id} to {todo.done}")
    except Exception as e:
        db.session.rollback()
        logger.error(f"Toggle todo error: {e}")
        flash("更新狀態失敗，請稍後再試", "error")
    
    return redirect(url_for('account.account_home'))

@account.route('/delete_todo/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_todo(id):
    """刪除待辦事項"""
    todo = ToDo.query.filter_by(id=id, user_id=current_user.id).first()
    if not todo:
        flash("找不到該待辦事項", "error")
        return redirect(url_for('account.account_home'))
    
    try:
        content = todo.content  # 保存內容用於日誌
        db.session.delete(todo)
        db.session.commit()
        flash("待辦事項已刪除", "success")
        logger.info(f"User {current_user.id} deleted todo: {content}")
    except Exception as e:
        db.session.rollback()
        logger.error(f"Delete todo error: {e}")
        flash("刪除失敗，請稍後再試", "error")
    
    return redirect(url_for('account.account_home'))

@account.route('/stats')
@login_required
def account_stats():
    """帳戶統計頁面"""
    try:
        records = Record.query.filter_by(user_id=current_user.id).all()
        todos = ToDo.query.filter_by(user_id=current_user.id).all()
        
        # 計算統計數據
        total_income = sum(r.amount for r in records if r.amount > 0)
        total_expense = sum(abs(r.amount) for r in records if r.amount < 0)
        total_balance = sum(r.amount for r in records)
        
        completed_todos = sum(1 for t in todos if t.done)
        pending_todos = len(todos) - completed_todos
        completion_rate = (completed_todos / len(todos) * 100) if todos else 0
        
        stats = {
            'total_income': round(total_income, 2),
            'total_expense': round(total_expense, 2),
            'total_balance': round(total_balance, 2),
            'total_records': len(records),
            'completed_todos': completed_todos,
            'pending_todos': pending_todos,
            'total_todos': len(todos),
            'completion_rate': round(completion_rate, 1)
        }
        
        return render_template('account_stats.html', stats=stats)
    
    except Exception as e:
        logger.error(f"Account stats error: {e}")
        flash("載入統計資料時發生錯誤", "error")
        return redirect(url_for('account.account_home'))