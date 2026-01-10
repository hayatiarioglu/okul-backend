import os

base_dir = os.getcwd()

# 1. MODELLERİ GÜNCELLE (Progress Tablosu Ekle)
models_code = """from app.extensions import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20))
    enrolled_classes = db.relationship('Classroom', secondary='enrollments', backref=db.backref('students', lazy='dynamic'), lazy='dynamic')
    progress = db.relationship('Progress', backref='student', lazy='dynamic') # YENİ

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
    teacher_name = db.Column(db.String(120), default="Bilinmiyor")
    topics = db.relationship('Topic', backref='classroom', lazy='dynamic')

class Topic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    is_covered = db.Column(db.Boolean, default=False)
    classroom_id = db.Column(db.Integer, db.ForeignKey('classroom.id'))

# YENİ: İLERLEME TABLOSU
class Progress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'))
    status = db.Column(db.String(20)) # 'done' (Tamam) veya 'missing' (Eksik)

enrollments = db.Table('enrollments',
    db.Column('student_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('classroom_id', db.Integer, db.ForeignKey('classroom.id'))
)
"""

with open(os.path.join(base_dir, 'app', 'models.py'), 'w', encoding='utf-8') as f:
    f.write(models_code)

# 2. ROTALARI GÜNCELLE (İşaretleme API'si Ekle)
routes_code = """from flask import Blueprint, jsonify, request
from app.models import User, Classroom, Topic, Progress
from app import db

bp = Blueprint('student', __name__)

@bp.route('/api/classes/<int:user_id>', methods=['GET'])
def api_student_classes(user_id):
    user = db.session.get(User, user_id)
    if not user: return jsonify({'error': 'Kullanıcı yok'}), 404

    # Test verisi oluşturucu
    if user.enrolled_classes.count() == 0:
        c1 = Classroom(name="9-A Matematik", teacher_name="Ahmet Hoca")
        c2 = Classroom(name="10-B Fizik", teacher_name="Mehmet Hoca")
        db.session.add_all([c1, c2])
        user.enrolled_classes.append(c1)
        user.enrolled_classes.append(c2)
        db.session.commit()

    class_list = []
    for cls in user.enrolled_classes:
        # İlerleme hesapla
        total = cls.topics.count()
        done = Progress.query.filter_by(student_id=user.id, status='done').join(Topic).filter(Topic.classroom_id==cls.id).count()
        percent = int((done/total)*100) if total > 0 else 0
        
        class_list.append({
            'id': cls.id,
            'name': cls.name,
            'teacher': cls.teacher_name,
            'percent': percent
        })
    return jsonify(class_list)

@bp.route('/api/class/<int:class_id>', methods=['GET'])
def api_class_detail(class_id):
    classroom = db.session.get(Classroom, class_id)
    user_id = request.args.get('user_id') # Telefondan user_id de gelecek artık
    
    if not classroom: return jsonify({'error': 'Sınıf yok'}), 404

    # Test konuları
    if classroom.topics.count() == 0:
        t1 = Topic(name="Giriş ve Temel Kavramlar", classroom_id=classroom.id)
        t2 = Topic(name="Ünite 2: Zor Konular", classroom_id=classroom.id)
        t3 = Topic(name="Final Hazırlık", classroom_id=classroom.id)
        db.session.add_all([t1, t2, t3])
        db.session.commit()

    topics_list = []
    for topic in classroom.topics:
        # Bu öğrenci bu konuyu yapmış mı?
        status = 'empty'
        if user_id:
            prog = Progress.query.filter_by(student_id=user_id, topic_id=topic.id).first()
            if prog: status = prog.status

        topics_list.append({
            'id': topic.id,
            'name': topic.name,
            'status': status # 'done', 'missing', 'empty'
        })

    return jsonify({
        'class_name': classroom.name,
        'topics': topics_list
    })

# YENİ: DURUM GÜNCELLEME KAPISI
@bp.route('/api/topic/set_status', methods=['POST'])
def set_status():
    data = request.get_json()
    user_id = data.get('user_id')
    topic_id = data.get('topic_id')
    status = data.get('status') # 'done' veya 'missing'

    prog = Progress.query.filter_by(student_id=user_id, topic_id=topic_id).first()
    if not prog:
        prog = Progress(student_id=user_id, topic_id=topic_id)
    
    prog.status = status
    db.session.add(prog)
    db.session.commit()

    return jsonify({'success': True})
"""

with open(os.path.join(base_dir, 'app', 'student', 'routes.py'), 'w', encoding='utf-8') as f:
    f.write(routes_code)

print("✅ LEVEL 3 GÜNCELLEMESİ TAMAM.")
print("Lütfen 'app.db' dosyasını silip 'python run.py' komutunu tekrar çalıştır.")