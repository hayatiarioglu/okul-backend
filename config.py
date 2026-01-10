import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Güvenlik Anahtarı (Bulutta gizli, burada açık)
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'cok-gizli-ve-zor-bir-sifre-buraya'
    
    # DATABASE AYARI (KRİTİK NOKTA)
    # Eğer sunucudaysan (DATABASE_URL varsa) onu kullan, yoksa yerel SQLite kullan.
    # Render.com bazen 'postgres://' verir, onu 'postgresql://' ile düzeltiyoruz.
    database_url = os.environ.get('DATABASE_URL')
    
    if database_url and database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
        
    SQLALCHEMY_DATABASE_URI = database_url or 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False