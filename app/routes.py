from flask import Blueprint, jsonify, request
from app import db
from app.models import User, Classroom
from flask_login import login_user, logout_user

bp = Blueprint('api', __name__, url_prefix='/api')

# --- 1. KAYIT OL (DÜZELTİLDİ: Email artık zorunlu değil) ---
@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    
    # Sadece Kullanıcı Adı ve Şifre zorunlu olsun
    if 'username' not in data or 'password' not in data:
        return jsonify({'success': False, 'message': 'Kullanıcı adı ve şifre şart!'}), 400

    # Kullanıcı adı zaten var mı?
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'success': False, 'message': 'Bu kullanıcı adı zaten alınmış.'}), 400
        
    # --- İŞTE SİHİRLİ DOKUNUŞ ---
    # Eğer mobil uygulama email göndermediyse, biz uyduralım:
    gelen_email = data.get('email')
    if not gelen_email:
        gelen_email = f"{data['username']}@okul.com" 
    # ----------------------------

    # Email kontrolü (Artık uydurma email olduğu için hata vermez)
    if User.query.filter_by(email=gelen_email).first():
         # Eğer uydurduğumuz email bile varsa sonuna rastgele sayı ekleyelim
        import random
        gelen_email = f"{data['username']}{random.randint(1,999)}@okul.com"

    # Yeni kullanıcı oluştur
    user = User(username=data['username'], email=gelen_email, role='student')
    user.set_password(data['password'])
    
    try:
        db.session.add(user)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Kayıt başarılı! Giriş yapabilirsin.'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Sunucu Hatası: {str(e)}'}), 500

# --- 2. GİRİŞ YAP (Login) ---
@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}

    if 'username' not in data or 'password' not in data:
        return jsonify({'success': False, 'message': 'Kullanıcı adı ve şifre girin.'}), 400

    user = User.query.filter_by(username=data['username']).first()

    if user and user.check_password(data['password']):
        login_user(user)
        return jsonify({
            'success': True, 
            'message': 'Giriş başarılı', 
            'user': {
                'id': user.id,
                'username': user.username,
                'role': user.role
            }
        })
    
    return jsonify({'success': False, 'message': 'Hatalı kullanıcı adı veya şifre.'}), 401

# --- 3. DERSLERİ GETİR ---
@bp.route('/classes', methods=['GET'])
def get_classes():
    classes = Classroom.query.all()
    output = []
    for c in classes:
        output.append({
            'id': c.id,
            'name': c.name,
            'teacher': c.teacher_name,
            'topic_count': c.topics.count()
        })
    return jsonify({'success': True, 'classes': output})