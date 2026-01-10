from flask import Flask
from config import Config
from app.extensions import db, migrate, login_manager
import os

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # --- AMELİYAT BURADA BAŞLIYOR ---
    # Render'ın verdiği veya Config'den gelen hatalı adresi burada zorla düzeltiyoruz.
    # Config dosyasını tamamen yok saysa bile bu kod çalışır.
    
    mevcut_adres = app.config.get('SQLALCHEMY_DATABASE_URI')
    
    if mevcut_adres:
        # Eğer adres 'postgres://' ile başlıyorsa, acımadan 'postgresql://' yapıyoruz.
        if mevcut_adres.startswith('postgres://'):
            yeni_adres = mevcut_adres.replace('postgres://', 'postgresql://', 1)
            app.config['SQLALCHEMY_DATABASE_URI'] = yeni_adres
            print(f"⚠️ DÜZELTME YAPILDI: Adres 'postgresql://' formatına çevrildi.")
    # -------------------------------

    # Başlatıcılar
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    from app import models

    # Blueprintler
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.student import bp as student_bp
    app.register_blueprint(student_bp, url_prefix='/student')
    
    from app.teacher import bp as teacher_bp
    app.register_blueprint(teacher_bp, url_prefix='/teacher')

    return app