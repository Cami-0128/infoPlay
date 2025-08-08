from app import create_app, db

app = create_app()

with app.app_context():
    print("⚠️ 找不到現有的資料庫，將建立新的資料庫")
    db.create_all()
    print("資料庫建立完成")
