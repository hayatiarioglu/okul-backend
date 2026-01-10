import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'cok-gizli-anahtar'
    
    # Render'dan gelen adresi al
    database_url = os.environ.get('DATABASE_URL')
    
    # Eğer adres varsa ve 'postgres://' ile başlıyorsa 'postgresql://' yap
    if database_url and database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
        
    # Yoksa yerel sqlite kullan
    SQLALCHEMY_DATABASE_URI = database_url or 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False