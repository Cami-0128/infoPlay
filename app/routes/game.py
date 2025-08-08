from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app.models import GameRecord
from app.extensions import db

game = Blueprint('game', __name__)

@game.route('/')
@login_required
def game_menu():
    # 獲取使用者的遊戲記錄統計
    snake_best = db.session.query(db.func.max(GameRecord.score)).filter_by(
        user_id=current_user.id, game_type='snake').scalar() or 0
    
    space_best = db.session.query(db.func.max(GameRecord.score)).filter_by(
        user_id=current_user.id, game_type='space_shooter').scalar() or 0
        
    # 改為猜數字遊戲的最高分
    guess_best = db.session.query(db.func.max(GameRecord.score)).filter_by(
        user_id=current_user.id, game_type='guess_number').scalar() or 0
    
    stats = {
        'snake_best': snake_best,
        'space_best': space_best,
        'guess_best': guess_best  # 改為猜數字最佳分數
    }
    
    return render_template('game.html', stats=stats)

@game.route('/snake')
@login_required
def play_snake():
    return render_template('snake_game.html')

@game.route('/space_shooter')
@login_required
def play_space_shooter():
    return render_template('space_shooter.html')

# 改為猜數字遊戲路由
@game.route('/guess_number')
@login_required
def play_guess_number():
    return render_template('guess_number_game.html')

@game.route('/save_score', methods=['POST'])
@login_required
def save_score():
    try:
        data = request.get_json()
        game_type = data.get('game_type')
        score = data.get('score', 0)
        level = data.get('level', 1)
        attempts = data.get('attempts')  # 新增嘗試次數欄位
        
        # 更新有效的遊戲類型
        valid_games = ['snake', 'space_shooter', 'guess_number']
        if game_type not in valid_games:
            return jsonify({'success': False, 'message': '無效的遊戲類型'})
        
        # 建立遊戲記錄
        game_record = GameRecord(
            user_id=current_user.id,
            game_type=game_type,
            score=int(score),
            level=int(level),
            reaction_time=int(attempts) if attempts and game_type == 'guess_number' else None  # 重用此欄位存儲嘗試次數
        )
        
        db.session.add(game_record)
        db.session.commit()
        
        return jsonify({'success': True, 'message': '分數已儲存'})
        
    except Exception as e:
        db.session.rollback()
        print(f"Save score error: {e}")
        return jsonify({'success': False, 'message': '儲存失敗'})

@game.route('/leaderboard/<game_type>')
@login_required
def leaderboard(game_type):
    # 更新有效的遊戲類型
    valid_games = ['snake', 'space_shooter', 'guess_number']
    if game_type not in valid_games:
        return redirect(url_for('game.game_menu'))
    
    if game_type == 'guess_number':
        # 猜數字遊戲按分數排序（越高越好）
        records = GameRecord.query.filter_by(game_type=game_type).order_by(
            GameRecord.score.desc()).limit(10).all()
    else:
        # 其他遊戲按分數排序（越高越好）
        records = GameRecord.query.filter_by(game_type=game_type).order_by(
            GameRecord.score.desc()).limit(10).all()
    
    return render_template('leaderboard.html', records=records, game_type=game_type)