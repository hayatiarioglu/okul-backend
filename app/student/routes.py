from flask import Blueprint, jsonify, request
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
