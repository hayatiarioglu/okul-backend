from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_login import LoginManager # <-- YENİ GELDİ
from config import Config

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager() # <-- YENİ GELDİ
admin = Admin(name='Okul Yönetim', template_mode='bootstrap3')

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Tüm eklentileri başlat
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app) # <-- YENİ GELDİ
    admin.init_app(app)

    # Modelleri içeri al (Hata vermemesi için import sırası önemli)
    from app.models import User, Classroom, Topic, Progress

    # Admin Paneline Tabloları Ekle (Patron Masası Büyüdü)
    admin.add_view(ModelView(User, db.session))
    admin.add_view(ModelView(Classroom, db.session))
    admin.add_view(ModelView(Topic, db.session))
    admin.add_view(ModelView(Progress, db.session))

    return app