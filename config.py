import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'cok-gizli-anahtar'
    
    # 1. Adresi ham haliyle al
    ham_adres = os.environ.get('DATABASE_URL')
    
    # 2. Eğer adres varsa ve 'postgres://' ile başlıyorsa ANINDA düzelt
    if ham_adres and ham_adres.startswith("postgres://"):
        ham_adres = ham_adres.replace("postgres://", "postgresql://", 1)
        
    # 3. Düzeltilmiş adresi sisteme ver (Yoksa sqlite kullan)
    SQLALCHEMY_DATABASE_URI = ham_adres or 'sqlite:///' + os.path.join(basedir, 'app.db')
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False