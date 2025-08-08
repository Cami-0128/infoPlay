# app/__init__.py
from flask import Flask
from app.extensions import db, login_manager
from app.models import User  # 這裡要匯入所有模型以確保它們被載入

def create_app():
    app = Flask(__name__)
    
    # 基本配置
    app.config['SECRET_KEY'] = 'your-secret-key-change-this-in-production'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # 初始化擴展
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = '請先登入才能訪問此頁面'
    login_manager.login_message_category = 'info'
    
    # 重要：確保所有模型都被載入
    from app.models import User, ToDo, Record, GameRecord
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # 匯入並註冊所有 Blueprint
    from app.routes.auth import auth
    from app.routes.dashboard import dashboard
    from app.routes.account import account
    from app.routes.info import info
    from app.routes.game import game  # 直接匯入，不使用 try-except
    
    # 可選的 Blueprint (如果存在的話)
    try:
        from app.routes.home import home_bp
        app.register_blueprint(home_bp)
    except ImportError:
        print("Home blueprint not found, skipping...")
    
    try:
        from app.routes.record import record_bp
        app.register_blueprint(record_bp)
    except ImportError:
        print("Record blueprint not found, skipping...")
    
    # 註冊必要的 Blueprint
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(dashboard, url_prefix='/dashboard')
    app.register_blueprint(account, url_prefix='/account')
    app.register_blueprint(info)  # info 已經在內部設定 url_prefix='/info'
    app.register_blueprint(game, url_prefix='/game')  # 確保註冊 game blueprint
    
    # 首頁路由
    @app.route('/')
    def index():
        from flask import redirect, url_for
        return redirect(url_for('auth.login'))
    
    # 錯誤處理
    @app.errorhandler(404)
    def page_not_found(e):
        return "<h1>404 找不到頁面</h1><p>您要找的頁面不存在</p>", 404
    
    @app.errorhandler(500)
    def internal_server_error(e):
        return "<h1>500 伺服器內部錯誤</h1><p>伺服器發生錯誤，請稍後再試</p>", 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(debug=True)