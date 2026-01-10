import os

# ==========================================
# BU DOSYA OTOMATİK KURULUM YAPAR
# ==========================================

base_dir = os.getcwd()
app_dir = os.path.join(base_dir, 'app')

# Klasör Yapısı
folders = [
    'app',
    'app/auth',
    'app/main',
    'app/student',
    'app/teacher',
    'app/templates',
]

for folder in folders:
    os.makedirs(os.path.join(base_dir, folder), exist_ok=True)
    print(f"✅ Klasör oluşturuldu: {folder}")

# ---------------------------------------------------------
# DOSYA İÇERİKLERİ
# ---------------------------------------------------------

files = {
    # 1. CONFIG
    'config.py': """import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'cok-gizli-anahtar'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
""",

    # 2. RUN.PY (GERÇEK OLAN - MOBİL UYUMLU)
    'run.py': """from app import create_app, db
from app.models import User

app = create_app()

# Uygulama her başladığında veritabanını kontrol et
with app.app_context():
    db.create_all()
    # Test kullanıcısı yoksa oluştur
    if not User.query.filter_by(username='deneme').first():
        print("🛠️ Test kullanıcısı 'deneme' oluşturuluyor...")
        u = User(username='deneme', email='deneme@okul.com', role='student')
        u.set_password('1234')
        db.session.add(u)
        db.session.commit()
        print("✅ Kullanıcı hazır: deneme / 1234")

if __name__ == '__main__':
    # 0.0.0.0 sayesinde telefondan erişilebilir
    app.run(debug=True, host='0.0.0.0', port=5000)
""",

    # 3. APP INIT
    'app/__init__.py': """from flask import Flask
from config import Config
from app.extensions import db, migrate, login_manager

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.student import bp as student_bp
    app.register_blueprint(student_bp, url_prefix='/student')

    return app
""",

    # 4. EXTENSIONS
    'app/extensions.py': """from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
""",

    # 5. MODELS
    'app/models.py': """from app.extensions import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20))
    
    # İlişkiler
    enrolled_classes = db.relationship('Classroom', secondary='enrollments', backref=db.backref('students', lazy='dynamic'), lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(id):
    return db.session.get(User, int(id))

class Classroom(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    teacher_name = db.Column(db.String(120), default="Bilinmiyor") # Basitleştirildi
    
# Basit kayıt tablosu
enrollments = db.Table('enrollments',
    db.Column('student_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('classroom_id', db.Integer, db.ForeignKey('classroom.id'))
)
""",

    # 6. AUTH ROUTES (MOBİL API DAHİL)
    'app/auth/routes.py': """from flask import Blueprint, jsonify, request
from app.models import User
from flask_login import login_user

bp = Blueprint('auth', __name__)

@bp.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')
    
    user = User.query.filter_by(username=username).first()
    
    if user is None or not user.check_password(password):
        return jsonify({'success': False, 'message': 'Hatalı kullanıcı adı veya şifre'}), 401
    
    return jsonify({
        'success': True,
        'user_id': user.id,
        'username': user.username,
        'role': user.role
    })
""",
    'app/auth/__init__.py': "from . import routes",

    # 7. STUDENT ROUTES (MOBİL API DAHİL)
    'app/student/routes.py': """from flask import Blueprint, jsonify
from app.models import User, Classroom
from app import db

bp = Blueprint('student', __name__)

@bp.route('/api/classes/<int:user_id>', methods=['GET'])
def api_student_classes(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({'error': 'Kullanıcı bulunamadı'}), 404

    # Eğer kullanıcının hiç sınıfı yoksa otomatik 3 tane ekleyelim (Test İçin)
    if user.enrolled_classes.count() == 0:
        c1 = Classroom(name="9-A Matematik", teacher_name="Ahmet Hoca")
        c2 = Classroom(name="10-B Fizik", teacher_name="Mehmet Hoca")
        c3 = Classroom(name="Bireysel Python", teacher_name="Kendim")
        db.session.add_all([c1, c2, c3])
        user.enrolled_classes.append(c1)
        user.enrolled_classes.append(c2)
        user.enrolled_classes.append(c3)
        db.session.commit()

    class_list = []
    for cls in user.enrolled_classes:
        # Rastgele yüzde simülasyonu (Veritabanı boşken dolu gözüksün diye)
        percent = (cls.id * 15) % 100 
        
        class_list.append({
            'name': cls.name,
            'teacher': cls.teacher_name,
            'percent': percent
        })

    return jsonify(class_list)
""",
    'app/student/__init__.py': "from . import routes",
}

# Dosyaları Yaz
for filename, content in files.items():
    filepath = os.path.join(base_dir, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"📄 Dosya oluşturuldu: {filename}")

print("-" * 40)
print("✅ KURULUM TAMAMLANDI!")
print("Şimdi sırasıyla şunları yap:")
print("1. Terminale: pip install flask flask-sqlalchemy flask-migrate flask-login")
print("2. Terminale: python run.py")
print("-" * 40)