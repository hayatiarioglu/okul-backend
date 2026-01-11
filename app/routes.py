from flask import Blueprint, jsonify, request
from app import db
from app.models import User, Classroom, Topic, Progress

bp = Blueprint('api', __name__, url_prefix='/api')

# 1. GİRİŞ & KAYIT (Standart)
@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    if User.query.filter_by(username=data.get('username')).first():
        return jsonify({'success': False, 'message': 'Kullanıcı adı dolu'}), 400
    user = User(username=data['username'], email=f"{data['username']}@okul.com", role=data.get('role', 'student'))
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Kayıt Başarılı'})

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    user = User.query.filter_by(username=data.get('username')).first()
    if user and user.check_password(data.get('password')):
        return jsonify({'success': True, 'user': {'id': user.id, 'username': user.username, 'role': user.role}})
    return jsonify({'success': False, 'message': 'Hatalı giriş'}), 401

# --- 2. DASHBOARD (ANA SAYFA VERİLERİ) ---
@bp.route('/dashboard/<username>', methods=['GET'])
def get_dashboard(username):
    user = User.query.filter_by(username=username).first()
    if not user: return jsonify({'success': False}), 404

    # A. Eksik Konular (Kırmızı Alan)
    eksikler = []
    missing_progress = Progress.query.filter_by(student_id=user.id, status='missing').all()
    for p in missing_progress:
        topic = Topic.query.get(p.topic_id)
        if topic:
            eksikler.append({'konu': topic.name, 'ders': topic.classroom.name})

    # B. Ders İlerlemeleri
    dersler_data = []
    classes = Classroom.query.all()
    for c in classes:
        total_topics = c.topics.count()
        completed = Progress.query.join(Topic).filter(
            Progress.student_id == user.id,
            Progress.status == 'done',
            Topic.classroom_id == c.id
        ).count()
        
        yuzde = int((completed / total_topics) * 100) if total_topics > 0 else 0
        dersler_data.append({
            'id': c.id, 'name': c.name, 'teacher': c.teacher_name,
            'progress': yuzde, 'total': total_topics
        })

    return jsonify({'success': True, 'eksikler': eksikler, 'dersler': dersler_data})

# --- 3. DERS DETAYI VE KONULAR ---
@bp.route('/class/<int:class_id>/<username>', methods=['GET'])
def get_class_detail(class_id, username):
    user = User.query.filter_by(username=username).first()
    classroom = Classroom.query.get(class_id)
    
    topics_data = []
    for topic in classroom.topics:
        # Bu öğrenci bu konuda ne yapmış?
        prog = Progress.query.filter_by(student_id=user.id, topic_id=topic.id).first()
        status = prog.status if prog else 'none' # none, done, missing
        
        topics_data.append({
            'id': topic.id, 'name': topic.name, 'status': status
        })

    return jsonify({'success': True, 'class_name': classroom.name, 'topics': topics_data})

# --- 4. İLERLEME GÜNCELLEME (BUTONA BASINCA) ---
@bp.route('/progress/update', methods=['POST'])
def update_progress():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    topic_id = data['topic_id']
    new_status = data['status'] # 'done', 'missing', 'none'

    # Eski kaydı bul
    prog = Progress.query.filter_by(student_id=user.id, topic_id=topic_id).first()

    if new_status == 'none':
        if prog: db.session.delete(prog) # Kaydı sil (sıfırla)
    else:
        if prog:
            prog.status = new_status # Güncelle
        else:
            new_prog = Progress(student_id=user.id, topic_id=topic_id, status=new_status)
            db.session.add(new_prog) # Yeni ekle
            
    db.session.commit()
    return jsonify({'success': True})