from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
# Admin paneli (Bootstrap3 hatası düzeltilmiş hali)
admin = Admin(name='Okul Yönetim') 

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Eklentileri başlat
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    admin.init_app(app)

    # Modelleri içeri al (Admin paneli için gerekli)
    from app.models import User, Classroom, Topic, Progress

    # Admin Paneline Tabloları Ekle
    admin.add_view(ModelView(User, db.session))
    admin.add_view(ModelView(Classroom, db.session))
    admin.add_view(ModelView(Topic, db.session))
    admin.add_view(ModelView(Progress, db.session))

    # --- ÖNEMLİ: API Rotalarını (Garsonları) Kaydet ---
    from app.routes import bp as api_bp
    app.register_blueprint(api_bp)

    return app