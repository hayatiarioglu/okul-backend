from flask import Blueprint, jsonify, request
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
