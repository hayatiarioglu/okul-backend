import os

base_dir = os.getcwd()
routes_path = os.path.join(base_dir, 'app', 'auth', 'routes.py')

# Mevcut dosyanın yedeğini almadan direkt altına ekliyoruz
api_register_code = """

# --- TELEFONDAN KAYIT OLMA EKLENTİSİ ---
@bp.route('/api/register', methods=['POST'])
def api_register():
    data = request.get_json() or {}
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', 'student') # Varsayılan öğrenci

    if not username or not password:
        return jsonify({'success': False, 'message': 'Eksik bilgi!'}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({'success': False, 'message': 'Bu kullanıcı adı zaten alınmış!'}), 400

    # Yeni kullanıcı oluştur
    user = User(username=username, email=email, role=role)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return jsonify({'success': True, 'message': 'Kayıt başarılı!'})
"""

with open(routes_path, 'a', encoding='utf-8') as f:
    f.write(api_register_code)

print("✅ SİSTEM GÜNCELLENDİ: Artık telefondan kayıt olunabilir.")
print("Lütfen 'python run.py' komutunu kapatıp TEKRAR AÇ.")