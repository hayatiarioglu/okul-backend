import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'bu-cok-gizli-bir-anahtardir-degistir'
    
    # DATABASE AYARI (KRİTİK KISIM)
    # 1. Önce Render'dan gelen DATABASE_URL'i alıyoruz.
    uri = os.environ.get('DATABASE_URL')
    
    # 2. Eğer URL varsa ve 'postgres://' ile başlıyorsa düzeltiyoruz (SQLAlchemy hatasını önler)
    if uri and uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)
    
    # 3. Eğer URL yoksa (bilgisayarındaysan) yerel SQLite kullan.
    SQLALCHEMY_DATABASE_URI = uri or 'sqlite:///' + os.path.join(basedir, 'app.db')
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False