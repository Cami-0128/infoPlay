# complete_rebuild_db.py
import os
from app import create_app, db

def rebuild_database():
    app = create_app()
    
    with app.app_context():
        print("🔍 檢查並載入所有模型...")
        
        # 明確匯入所有模型以確保它們被載入
        from app.models import User, ToDo, Record, GameRecord
        
        print("✅ 模型載入完成:")
        print(f"  - User: {User.__table__.name}")
        print(f"  - ToDo: {ToDo.__table__.name}")
        print(f"  - Record: {Record.__table__.name}")
        print(f"  - GameRecord: {GameRecord.__table__.name}")
        
        # 顯示 GameRecord 的所有欄位
        print(f"\n📋 GameRecord 模型欄位:")
        for column_name, column in GameRecord.__table__.columns.items():
            print(f"  - {column_name}: {column.type}")
        
        # 刪除資料庫檔案（如果存在）
        db_path = app.config.get('SQLALCHEMY_DATABASE_URI', '').replace('sqlite:///', '')
        if db_path and os.path.exists(db_path):
            print(f"\n🗑️ 刪除舊資料庫檔案: {db_path}")
            os.remove(db_path)
        
        print("\n🔨 建立新資料庫...")
        db.create_all()
        
        # 驗證表格建立
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"✅ 建立的表格: {tables}")
        
        # 詳細檢查 game_record 表格
        if 'game_record' in tables:
            columns = inspector.get_columns('game_record')
            print(f"\n📊 game_record 表格詳細結構:")
            for col in columns:
                print(f"  - {col['name']}: {col['type']} {'(nullable)' if col['nullable'] else '(not null)'}")
            
            # 檢查必要欄位
            column_names = [col['name'] for col in columns]
            required_fields = ['id', 'user_id', 'game_type', 'score', 'level', 'reaction_time', 'date']
            missing_fields = [field for field in required_fields if field not in column_names]
            
            if not missing_fields:
                print("✅ 所有必要欄位都存在")
            else:
                print(f"❌ 缺少欄位: {missing_fields}")
        
        # 測試插入和查詢
        print("\n🧪 測試資料庫操作...")
        try:
            # 建立測試用戶
            test_user = User(username='test_user', password='test_password')
            db.session.add(test_user)
            db.session.flush()  # 獲取 user_id 但不提交
            
            # 建立測試遊戲記錄
            test_record = GameRecord(
                user_id=test_user.id,
                game_type='snake',
                score=150,
                level=2,
                reaction_time=0.5
            )
            db.session.add(test_record)
            db.session.commit()
            
            # 查詢測試
            query_result = GameRecord.query.filter_by(game_type='snake').first()
            if query_result:
                print(f"✅ 查詢測試成功: {query_result}")
            else:
                print("❌ 查詢測試失敗")
            
            # 清除測試資料
            db.session.delete(test_record)
            db.session.delete(test_user)
            db.session.commit()
            
            print("✅ 資料庫操作測試成功")
            
        except Exception as e:
            print(f"❌ 資料庫操作測試失敗: {e}")
            db.session.rollback()
        
        print("\n🎯 資料庫重建完成！")

if __name__ == '__main__':
    rebuild_database()