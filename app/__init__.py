from flask import Flask
from config import Config
from app.extensions import db, migrate, login_manager

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Başlatıcılar
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Blueprintler
    # Eğer 'main' modülü yok hatası alırsan aşağıdakini yorum satırı yap
    try:
        from app.main import bp as main_bp
        app.register_blueprint(main_bp)
    except ImportError:
        pass 

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.student import bp as student_bp
    app.register_blueprint(student_bp, url_prefix='/student')
    
    from app.teacher import bp as teacher_bp
    app.register_blueprint(teacher_bp, url_prefix='/teacher')

    return app