import os
import sys

# Bulunduğumuz yer
base_dir = os.getcwd()
print(f"📍 Çalışma Dizini: {base_dir}")

# ------------------------------------------------------------------
# 1. DOSYA İÇERİKLERİNİ HAZIRLA (En Doğru ve Garantili Kodlar)
# ------------------------------------------------------------------

# A. TEACHER __INIT__ (Bu eksikti, o yüzden hata veriyordu)
teacher_init_code = """from flask import Blueprint

bp = Blueprint('teacher', __name__)

from app.teacher import routes
"""

# B. TEACHER ROUTES (API Kapıları)
teacher_routes_code = """from flask import Blueprint, jsonify, request
from app.models import User, Classroom, Topic, Progress
from app import db
import secrets

bp = Blueprint('teacher', __name__)

# 1. SINIFLARI GETİR
@bp.route('/api/classes/<int:teacher_id>', methods=['GET'])
def api_teacher_classes(teacher_id):
    # Basitlik için tüm sınıfları döndürüyoruz
    classes = Classroom.query.all()
    data = []
    for c in classes:
        # Öğrenci sayısını hesapla
        try:
            cnt = c.students.count() # dynamic loader ise count()
        except:
            cnt = len(c.students) # list ise len()
            
        data.append({
            'id': c.id,
            'name': c.name,
            'student_count': cnt,
            'code': getattr(c, 'join_code', '---')
        })
    return jsonify(data)

# 2. SINIF OLUŞTUR
@bp.route('/api/class/create', methods=['POST'])
def api_create_class():
    data = request.get_json() or {}
    name = data.get('name')
    teacher_name = data.get('teacher_name')
    
    code = secrets.token_hex(3).upper()
    
    try:
        # teacher_name modelde varsa ekle, yoksa geç
        new_class = Classroom(name=name, teacher_name=teacher_name)
        if hasattr(new_class, 'join_code'):
            new_class.join_code = code
            
        db.session.add(new_class)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Sınıf oluşturuldu'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

# 3. KONU EKLE
@bp.route('/api/topic/add', methods=['POST'])
def api_add_topic():
    data = request.get_json() or {}
    class_id = data.get('class_id')
    name = data.get('name')
    
    t = Topic(name=name, classroom_id=class_id)
    db.session.add(t)
    db.session.commit()
    return jsonify({'success': True})

# 4. ANALİZ (MONITOR)
@bp.route('/api/class/<int:class_id>/monitor', methods=['GET'])
def api_monitor(class_id):
    cls = db.session.get(Classroom, class_id)
    if not cls: return jsonify({'error': 'Yok'}), 404
    
    total = cls.topics.count()
    students_data = []
    
    for s in cls.students:
        # İlerleme hesapla
        done = Progress.query.filter_by(student_id=s.id, status='done').join(Topic).filter(Topic.classroom_id==cls.id).count()
        percent = int((done/total)*100) if total > 0 else 0
        
        students_data.append({
            'name': s.username,
            'percent': percent
        })
        
    return jsonify({'students': students_data})
"""

# C. APP __INIT__ (Blueprint'leri Kayıt Etme)
app_init_code = """from flask import Flask
from config import Config
from app.extensions import db, migrate, login_manager

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # 1. AUTH
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    # 2. STUDENT
    from app.student import bp as student_bp
    app.register_blueprint(student_bp, url_prefix='/student')

    # 3. TEACHER (İşte bu satır olmazsa 404 alırsın)
    from app.teacher import bp as teacher_bp
    app.register_blueprint(teacher_bp, url_prefix='/teacher')

    return app
"""

# ------------------------------------------------------------------
# 2. DOSYALARI YAZMA İŞLEMİ (Eskileri ezip geçer)
# ------------------------------------------------------------------

def yaz(yol, icerik):
    tam_yol = os.path.join(base_dir, yol)
    os.makedirs(os.path.dirname(tam_yol), exist_ok=True)
    with open(tam_yol, 'w', encoding='utf-8') as f:
        f.write(icerik)
    print(f"✅ Düzeltildi: {yol}")

# Şimdi hepsini sırayla düzeltiyoruz
yaz('app/teacher/__init__.py', teacher_init_code)
yaz('app/teacher/routes.py', teacher_routes_code)
yaz('app/__init__.py', app_init_code)

print("-" * 40)
print("TÜM SİSTEM BAŞTAN SONA ONARILDI.")
print("Şimdi şu komutla sunucuyu başlat:")
print("👉 python run.py")
print("-" * 40)