import os

# app/__init__.py dosyasını bulup içeriğini tamamen yeniliyoruz
base_dir = os.getcwd()
init_path = os.path.join(base_dir, 'app', '__init__.py')

yeni_icerik = """from flask import Flask
from config import Config
from app.extensions import db, migrate, login_manager

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Veritabanı ve Giriş sistemini başlat
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # 1. AUTH (Giriş/Çıkış) Modülü
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    # 2. STUDENT (Öğrenci) Modülü
    from app.student import bp as student_bp
    app.register_blueprint(student_bp, url_prefix='/student')

    # 3. TEACHER (Öğretmen) Modülü - İŞTE EKSİK OLAN BU SATIRDI!
    from app.teacher import bp as teacher_bp
    app.register_blueprint(teacher_bp, url_prefix='/teacher')

    return app
"""

with open(init_path, 'w', encoding='utf-8') as f:
    f.write(yeni_icerik)

print("-" * 40)
print("✅ KABLO BAĞLANDI: Öğretmen modülü sisteme tanıtıldı.")
print("Şimdi 'python run.py' komutunu tekrar çalıştır.")
print("-" * 40)