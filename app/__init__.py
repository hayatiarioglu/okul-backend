from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate  # <-- Yeni Mimarımız
from config import Config

# Veritabanı ve Mimar nesnelerini oluşturuyoruz
db = SQLAlchemy()
migrate = Migrate()  # <-- Mimar beklemede

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Eklentileri başlatıyoruz
    db.init_app(app)
    migrate.init_app(app, db)  # <-- Mimarı dükkana soktuk

    # Buraya senin rota (route) dosyalarını ekleyeceğiz ilerde
    # from app import routes
    # app.register_blueprint(routes.bp)

    return app