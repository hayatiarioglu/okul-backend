from flask import jsonify, request, Blueprint
from app import db
from app.models import User, Classroom, Topic
from flask_login import login_user, logout_user, current_user, login_required

# Garson Ekibini Kuruyoruz (Blueprint)
bp = Blueprint('api', __name__, url_prefix='/api')

# 1. KAYIT OLMA (Register)
@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json() # Telefondan gelen veriyi al
    
    # Basit kontroller
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': 'Bu kullanıcı adı zaten var', 'success': False}), 400
        
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'Bu email zaten var', 'success': False}), 400

    # Yeni kullanıcı oluştur
    user = User(username=data['username'], email=data['email'], role='student')
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({'message': 'Kayıt başarılı!', 'success': True}), 201

# 2. GİRİŞ YAPMA (Login)
@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()

    if user and user.check_password(data['password']):
        login_user(user) # Oturumu aç
        return jsonify({'message': 'Giriş başarılı', 'success': True, 'username': user.username, 'role': user.role})
    
    return jsonify({'message': 'Hatalı kullanıcı adı veya şifre', 'success': False}), 401

# 3. DERSLERİ GETİR (Classroom List)
@bp.route('/classes', methods=['GET'])
def get_classes():
    classes = Classroom.query.all()
    # Veritabanındaki dersleri JSON listesine çevir
    output = []
    for c in classes:
        output.append({
            'id': c.id,
            'name': c.name,
            'teacher': c.teacher_name
        })
    return jsonify({'classes': output, 'success': True})