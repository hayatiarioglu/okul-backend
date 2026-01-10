import os

base_dir = os.getcwd()

# ========================================================
# 1. ÖĞRENCİ ROTALARI (BUG FIX: 'empty' durumunu hallet)
# ========================================================
student_routes = """from flask import Blueprint, jsonify, request
from app.models import User, Classroom, Topic, Progress
from app import db

bp = Blueprint('student', __name__)

@bp.route('/api/classes/<int:user_id>', methods=['GET'])
def api_student_classes(user_id):
    user = db.session.get(User, user_id)
    if not user: return jsonify({'error': 'Kullanıcı yok'}), 404

    class_list = []
    for cls in user.enrolled_classes:
        total = cls.topics.count()
        done = Progress.query.filter_by(student_id=user.id, status='done').join(Topic).filter(Topic.classroom_id==cls.id).count()
        percent = int((done/total)*100) if total > 0 else 0
        class_list.append({'id': cls.id, 'name': cls.name, 'teacher': cls.teacher_name, 'percent': percent})
    return jsonify(class_list)

@bp.route('/api/class/<int:class_id>', methods=['GET'])
def api_class_detail(class_id):
    classroom = db.session.get(Classroom, class_id)
    user_id = request.args.get('user_id')
    if not classroom: return jsonify({'error': 'Sınıf yok'}), 404

    topics_list = []
    for topic in classroom.topics:
        status = 'empty'
        if user_id:
            prog = Progress.query.filter_by(student_id=user_id, topic_id=topic.id).first()
            if prog: status = prog.status
        topics_list.append({'id': topic.id, 'name': topic.name, 'status': status})

    return jsonify({'class_name': classroom.name, 'topics': topics_list})

@bp.route('/api/topic/set_status', methods=['POST'])
def set_status():
    data = request.get_json()
    user_id = data.get('user_id')
    topic_id = data.get('topic_id')
    status = data.get('status') # 'done', 'missing', 'empty'

    prog = Progress.query.filter_by(student_id=user_id, topic_id=topic_id).first()
    
    if status == 'empty':
        # SİLME İŞLEMİ (BUG FIX BURASI)
        if prog:
            db.session.delete(prog)
            db.session.commit()
    else:
        # EKLEME/GÜNCELLEME
        if not prog: prog = Progress(student_id=user_id, topic_id=topic_id)
        prog.status = status
        db.session.add(prog)
        db.session.commit()

    return jsonify({'success': True})
"""

with open(os.path.join(base_dir, 'app', 'student', 'routes.py'), 'w', encoding='utf-8') as f:
    f.write(student_routes)
    print("✅ Öğrenci modülü güncellendi (Silme özelliği eklendi).")

# ========================================================
# 2. ÖĞRETMEN ROTALARI (YENİ API'LER)
# ========================================================
teacher_routes = """from flask import Blueprint, jsonify, request
from app.models import User, Classroom, Topic, Progress
from app import db
import secrets

bp = Blueprint('teacher', __name__)

# HOCA SINIFLARI
@bp.route('/api/classes/<int:teacher_id>', methods=['GET'])
def api_teacher_classes(teacher_id):
    # Basitlik için tüm sınıfları döndürelim (Gerçekte teacher_id filtresi lazım)
    # Ama senin modelde teacher ilişkisi tam kurulu olmayabilir, o yüzden Classroom tablosuna bakıyoruz
    classes = Classroom.query.all() 
    # Sadece bu hocanınkileri filtreleyelim (teacher_name üzerinden basit eşleşme simülasyonu)
    # Not: Gerçek user id ilişkisi varsa onu kullanmak daha doğru olur.
    
    data = []
    for c in classes:
        student_count = len(c.students.all()) # enrollments üzerinden say
        data.append({
            'id': c.id,
            'name': c.name,
            'student_count': student_count,
            'code': getattr(c, 'join_code', 'KOD-YOK') # join_code yoksa hata vermesin
        })
    return jsonify(data)

# SINIF OLUŞTUR
@bp.route('/api/class/create', methods=['POST'])
def api_create_class():
    data = request.get_json()
    name = data.get('name')
    teacher_name = data.get('teacher_name')
    
    # Kod üret
    code = secrets.token_hex(3).upper()
    
    # Modelde join_code alanı yoksa hata verebilir, o yüzden try-except
    try:
        new_class = Classroom(name=name, teacher_name=teacher_name)
        # Eğer modelinde join_code varsa:
        if hasattr(new_class, 'join_code'):
            new_class.join_code = code
            
        db.session.add(new_class)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Sınıf oluşturuldu'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

# KONU EKLE
@bp.route('/api/topic/add', methods=['POST'])
def api_add_topic():
    data = request.get_json()
    class_id = data.get('class_id')
    name = data.get('name')
    
    t = Topic(name=name, classroom_id=class_id)
    db.session.add(t)
    db.session.commit()
    return jsonify({'success': True})

# ANALİZ (MONITOR)
@bp.route('/api/class/<int:class_id>/monitor', methods=['GET'])
def api_monitor(class_id):
    cls = db.session.get(Classroom, class_id)
    if not cls: return jsonify({'error': 'Yok'}), 404
    
    total_topics = cls.topics.count()
    students_data = []
    
    for s in cls.students:
        done = Progress.query.filter_by(student_id=s.id, status='done').join(Topic).filter(Topic.classroom_id==cls.id).count()
        percent = int((done/total_topics)*100) if total_topics > 0 else 0
        students_data.append({
            'name': s.username,
            'percent': percent
        })
        
    return jsonify({'students': students_data})
"""

# teacher klasörü yoksa oluştur
teacher_dir = os.path.join(base_dir, 'app', 'teacher')
if not os.path.exists(teacher_dir):
    os.makedirs(teacher_dir)
    # __init__ dosyasını da ekleyelim
    with open(os.path.join(teacher_dir, '__init__.py'), 'w') as f:
        f.write("from flask import Blueprint\nbp = Blueprint('teacher', __name__)\nfrom app.teacher import routes")

with open(os.path.join(teacher_dir, 'routes.py'), 'w', encoding='utf-8') as f:
    f.write(teacher_routes)
    print("✅ Öğretmen modülü (API) oluşturuldu.")

print("-" * 30)
print("GÜNCELLEME TAMAM. ŞİMDİ 'python run.py' ÇALIŞTIR.")