from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Record
from datetime import datetime

record_bp = Blueprint('record_bp', __name__, url_prefix='/record')

@record_bp.route('/')
@login_required
def record_home():
    """記帳詳情頁面"""
    records = Record.query.filter_by(user_id=current_user.id).order_by(Record.date.desc()).all()
    return render_template('record.html', records=records)

@record_bp.route('/add', methods=['POST'])
@login_required
def add_record():
    """新增記帳記錄 - 通用端點"""
    description = request.form.get('description', '').strip()
    amount_str = request.form.get('amount', '').strip()
    
    if not description:
        flash("請輸入記帳描述", "error")
        return redirect(request.referrer or url_for('record_bp.record_home'))
    
    if not amount_str:
        flash("請輸入金額", "error")
        return redirect(request.referrer or url_for('record_bp.record_home'))
    
    try:
        amount = float(amount_str)
        new_record = Record(
            description=description,
            amount=amount,
            user_id=current_user.id,
            date=datetime.utcnow()
        )
        db.session.add(new_record)
        db.session.commit()
        flash(f"成功新增記帳：{description} ${amount:.2f}", "success")
    except ValueError:
        flash("金額格式錯誤，請輸入數字", "error")
    except Exception as e:
        flash("新增記帳失敗，請稍後再試", "error")
        print(f"Record error: {e}")
    
    # 檢查請求來源，決定重定向到哪裡
    referer = request.referrer
    if referer and 'account' in referer:
        return redirect(url_for('account.account_home'))
    else:
        return redirect(url_for('record_bp.record_home'))

@record_bp.route('/delete/<int:id>')
@login_required
def delete_record(id):
    """刪除記帳記錄"""
    record = Record.query.filter_by(id=id, user_id=current_user.id).first()
    if record:
        try:
            db.session.delete(record)
            db.session.commit()
            flash("記帳記錄已刪除", "success")
        except Exception as e:
            flash("刪除失敗，請稍後再試", "error")
            print(f"Delete record error: {e}")
    else:
        flash("找不到該記帳記錄", "error")
    
    # 檢查請求來源，決定重定向到哪裡
    referer = request.referrer
    if referer and 'account' in referer:
        return redirect(url_for('account.account_home'))
    else:
        return redirect(url_for('record_bp.record_home'))

@record_bp.route('/stats')
@login_required
def record_stats():
    """記帳統計頁面"""
    records = Record.query.filter_by(user_id=current_user.id).all()
    
    if not records:
        stats = {
            'total_income': 0,
            'total_expense': 0,
            'total_balance': 0,
            'total_records': 0,
            'recent_records': []
        }
    else:
        total_income = sum(r.amount for r in records if r.amount > 0)
        total_expense = sum(abs(r.amount) for r in records if r.amount < 0)
        total_balance = sum(r.amount for r in records)
        recent_records = sorted(records, key=lambda x: x.date, reverse=True)[:5]
        
        stats = {
            'total_income': total_income,
            'total_expense': total_expense,
            'total_balance': total_balance,
            'total_records': len(records),
            'recent_records': recent_records
        }
    
    return render_template('record_stats.html', stats=stats)