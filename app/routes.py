from flask import Blueprint, jsonify, request
from app import db
from app.models import User, Classroom, Topic, Progress

bp = Blueprint('api', __name__, url_prefix='/api')

# --- 1. LOGIN (STANDART) ---
@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    user = User.query.filter_by(username=data.get('username')).first()
    if user and user.check_password(data.get('password')):
        return jsonify({'success': True, 'user': {'id': user.id, 'username': user.username, 'role': user.role}})
    return jsonify({'success': False, 'message': 'Hatalı giriş'}), 401

@bp.route('/register', methods=['POST'])
def register():
    # Basit kayıt (Önceki kodun aynısı)
    data = request.get_json() or {}
    if User.query.filter_by(username=data.get('username')).first(): return jsonify({'success': False, 'message': 'Alınmış'}), 400
    user = User(username=data['username'], email=f"{data['username']}@okul.com", role=data.get('role', 'student'))
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()
    return jsonify({'success': True}), 201

# --- 2. DASHBOARD (WEB SİTESİNDEKİ GİBİ) ---
@bp.route('/dashboard/<username>', methods=['GET'])
def get_dashboard(username):
    user = User.query.filter_by(username=username).first()
    if not user: return jsonify({'success': False}), 404

    # A. KIRMIZI KUTU (Eksik İşaretlenenler)
    eksikler = []
    # Veritabanında 'missing' olarak işaretlenmiş her şeyi çek
    missing_progress = Progress.query.filter_by(student_id=user.id, status='missing').all()
    for p in missing_progress:
        topic = Topic.query.get(p.topic_id)
        if topic:
            eksikler.append({
                'konu': topic.name,
                'ders': topic.classroom.name if topic.classroom else "Genel",
                'kaynak': "10. Sınıf Matematik" # Statik örnek
            })

    # B. DERS KARTLARI (İlerleme Çubukları)
    dersler_data = []
    classes = Classroom.query.all()
    for c in classes:
        total = c.topics.count()
        done = Progress.query.join(Topic).filter(Progress.student_id==user.id, Progress.status=='done', Topic.classroom_id==c.id).count()
        ratio = int((done/total)*100) if total > 0 else 0
        
        dersler_data.append({
            'id': c.id,
            'name': c.name,
            'teacher': c.teacher_name,
            'progress': ratio,
            'topic_count': total
        })

    return jsonify({
        'success': True,
        'eksikler': eksikler,
        'dersler': dersler_data,
        'bugun_tekrar': 2 # Şimdilik sahte veri (Webdeki mavi kutu için)
    })

# --- 3. DERS DETAY (ACCORDION YAPI İÇİN) ---
@bp.route('/class/<int:class_id>/<username>', methods=['GET'])
def get_class_detail(class_id, username):
    user = User.query.filter_by(username=username).first()
    classroom = Classroom.query.get(class_id)
    
    # Konuları Web'deki gibi Ünite Başlıklarına göre gruplayalım
    # Normalde veritabanında 'unit' alanı olmalı ama şimdilik isme göre uyduracağız
    grouped_topics = {} 
    
    for topic in classroom.topics:
        # İsimden ünite uydurma (Eğer 'Türev 1' ise 'Türev' ünitesi sayalım)
        unit_name = topic.name.split(' ')[0].upper() # İlk kelimeyi başlık yap
        if len(unit_name) < 3: unit_name = "GENEL KONULAR"

        prog = Progress.query.filter_by(student_id=user.id, topic_id=topic.id).first()
        status = prog.status if prog else 'none'
        
        if unit_name not in grouped_topics: grouped_topics[unit_name] = []
        grouped_topics[unit_name].append({'id': topic.id, 'name': topic.name, 'status': status})

    # Sözlüğü listeye çevir
    final_list = [{'unit': k, 'topics': v} for k, v in grouped_topics.items()]

    return jsonify({'success': True, 'class_name': classroom.name, 'curriculum': final_list})

# --- 4. DURUM GÜNCELLE (WEB'DEKİ 3'LÜ BUTON) ---
@bp.route('/progress/update', methods=['POST'])
def update_progress():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    
    # Var olanı silip yenisini yazalım (Basit mantık)
    existing = Progress.query.filter_by(student_id=user.id, topic_id=data['topic_id']).first()
    if existing: db.session.delete(existing)
    
    if data['status'] != 'none':
        new_p = Progress(student_id=user.id, topic_id=data['topic_id'], status=data['status'])
        db.session.add(new_p)
        
    db.session.commit()
    return jsonify({'success': True})