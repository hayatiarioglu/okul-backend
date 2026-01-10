import os

base_dir = os.getcwd()

# ---------------------------------------------------------
# 1. MODELLER (VERİTABANI YAPISI - TARİH ALANLARI EKLENDİ)
# ---------------------------------------------------------
models_code = """from app.extensions import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20))
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
    teacher_name = db.Column(db.String(120), default="Bilinmiyor")
    join_code = db.Column(db.String(10), unique=True)
    topics = db.relationship('Topic', backref='classroom', lazy='dynamic')

class Topic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    classroom_id = db.Column(db.Integer, db.ForeignKey('classroom.id'))

class Progress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'))
    status = db.Column(db.String(20)) # 'done', 'missing'
    
    # EBBINGHAUS ALANLARI
    last_reviewed = db.Column(db.DateTime, default=datetime.utcnow)
    next_review_date = db.Column(db.DateTime)
    interval = db.Column(db.Integer, default=0) # 0, 1, 3, 7, 30...

enrollments = db.Table('enrollments',
    db.Column('student_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('classroom_id', db.Integer, db.ForeignKey('classroom.id'))
)
"""

# ---------------------------------------------------------
# 2. ÖĞRENCİ ROTALARI (ALGORİTMA BURADA)
# ---------------------------------------------------------
student_routes_code = """from flask import Blueprint, jsonify, request
from app.models import User, Classroom, Topic, Progress
from app import db
from datetime import datetime, timedelta

bp = Blueprint('student', __name__)

# --- AKILLI DASHBOARD (KIRMIZI/MAVİ ALANLAR) ---
@bp.route('/api/dashboard/<int:user_id>', methods=['GET'])
def api_dashboard(user_id):
    user = db.session.get(User, user_id)
    if not user: return jsonify({'error': 'Yok'}), 404

    now = datetime.utcnow()
    
    # 1. KIRMIZI (Eksikler)
    missing = []
    missing_progs = Progress.query.filter_by(student_id=user.id, status='missing').all()
    for p in missing_progs:
        t = db.session.get(Topic, p.topic_id)
        if t: missing.append({'topic_name': t.name, 'class_name': t.classroom.name, 'topic_id': t.id})

    # 2. MAVİ (Bugün Tekrar Edilecekler)
    due = []
    # Statusu 'done' olup, tarihi bugün veya geçmişte olanlar
    done_progs = Progress.query.filter(
        Progress.student_id == user.id,
        Progress.status == 'done',
        Progress.next_review_date <= now
    ).all()
    
    for p in done_progs:
        t = db.session.get(Topic, p.topic_id)
        if t: due.append({'topic_name': t.name, 'class_name': t.classroom.name, 'topic_id': t.id})

    return jsonify({'red_zone': missing, 'blue_zone': due})

# --- DERS LİSTESİ ---
@bp.route('/api/classes/<int:user_id>', methods=['GET'])
def api_classes(user_id):
    user = db.session.get(User, user_id)
    data = []
    if user:
        for c in user.enrolled_classes:
            total = c.topics.count()
            done = Progress.query.filter_by(student_id=user.id, status='done').join(Topic).filter(Topic.classroom_id==c.id).count()
            percent = int((done/total)*100) if total > 0 else 0
            data.append({'id': c.id, 'name': c.name, 'teacher': c.teacher_name, 'percent': percent})
    return jsonify(data)

# --- DERS DETAYI ---
@bp.route('/api/class/<int:class_id>', methods=['GET'])
def api_class_detail(class_id):
    c = db.session.get(Classroom, class_id)
    uid = request.args.get('user_id')
    topics = []
    if c:
        for t in c.topics:
            stat = 'empty'
            if uid:
                p = Progress.query.filter_by(student_id=uid, topic_id=t.id).first()
                if p: stat = p.status
            topics.append({'id': t.id, 'name': t.name, 'status': stat})
    return jsonify({'topics': topics})

# --- DURUM GÜNCELLEME (EBBINGHAUS HESABI) ---
@bp.route('/api/topic/set_status', methods=['POST'])
def set_status():
    data = request.get_json()
    uid = data.get('user_id')
    tid = data.get('topic_id')
    status = data.get('status') # 'done', 'missing', 'empty'

    p = Progress.query.filter_by(student_id=uid, topic_id=tid).first()
    
    if status == 'empty':
        if p: 
            db.session.delete(p)
            db.session.commit()
        return jsonify({'success': True})

    if not p:
        p = Progress(student_id=uid, topic_id=tid)
    
    p.status = status
    p.last_reviewed = datetime.utcnow()

    # EĞER TAMAMLANDIYSA TARİHİ HESAPLA
    if status == 'done':
        # Algoritma: 1 -> 3 -> 7 -> 30
        current_interval = p.interval
        if current_interval == 0: new_interval = 1
        elif current_interval == 1: new_interval = 3
        elif current_interval == 3: new_interval = 7
        elif current_interval == 7: new_interval = 30
        else: new_interval = 30 # Max 30'da kalsın
        
        p.interval = new_interval
        p.next_review_date = datetime.utcnow() + timedelta(days=new_interval)
    else:
        # Eksikse veya boşa düştüyse aralığı sıfırla
        p.interval = 0
        p.next_review_date = None

    db.session.add(p)
    db.session.commit()
    return jsonify({'success': True})
"""

# Dosyaları Yaz
with open(os.path.join(base_dir, 'app', 'models.py'), 'w', encoding='utf-8') as f:
    f.write(models_code)

with open(os.path.join(base_dir, 'app', 'student', 'routes.py'), 'w', encoding='utf-8') as f:
    f.write(student_routes_code)

print("✅ SİSTEM GÜNCELLENDİ (Ebbinghaus Algoritması Eklendi).")
print("⚠️ LÜTFEN 'app.db' DOSYASINI SİL VE 'python run.py' ÇALIŞTIR.")