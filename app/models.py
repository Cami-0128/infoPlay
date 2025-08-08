# models.py - 與當前數據庫兼容的版本
from .extensions import db
from flask_login import UserMixin
from datetime import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    todos = db.relationship('ToDo', backref='user', lazy=True)
    records = db.relationship('Record', backref='user', lazy=True)
    game_records = db.relationship('GameRecord', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'

class ToDo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    done = db.Column(db.Boolean, default=False, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    # 移除 created_at 字段，因為數據庫中沒有這個列

    def __repr__(self):
        return f'<ToDo {self.content} Done:{self.done}>'

class Record(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f'<Record {self.description}: {self.amount}>'

class GameRecord(db.Model):
    __tablename__ = 'game_record'  # 明確指定表格名稱
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    game_type = db.Column(db.String(50), nullable=False)  # 'snake', 'space_shooter', 'reflex'
    score = db.Column(db.Integer, nullable=False)
    level = db.Column(db.Integer, default=1)
    reaction_time = db.Column(db.Float, nullable=True)  # 只有反應遊戲使用
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<GameRecord user:{self.user_id}, game:{self.game_type}, score:{self.score}>'