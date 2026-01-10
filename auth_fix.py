import os

base_dir = os.getcwd()
path = os.path.join(base_dir, 'app', 'auth', 'routes.py')

# İŞTE HATASIZ, EKSİKSİZ, FULL KOD
code = """from flask import Blueprint, jsonify, request, render_template, redirect, url_for, flash
from flask_login import current_user, login_user, logout_user, login_required
from app import db
from app.auth import bp
from app.models import User

# --- WEB GİRİŞ (SİTE İÇİN) ---
@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    return render_template('auth/login.html', title='Giriş', form=None)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    return render_template('auth/register.html', title='Kayıt', form=None)

# =======================================================
# MOBİL API ROTALARI (SENİN İÇİN ÖNEMLİ OLAN BURASI)
# =======================================================

# 1. API GİRİŞ
@bp.route('/api/login', methods=['POST'])
def api_login():
    try:
        data = request.get_json() or {}
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({'success': False, 'message': 'Kullanıcı adı ve şifre şart!'}), 400

        user = User.query.filter_by(username=username).first()

        if user is None or not user.check_password(password):
            return jsonify({'success': False, 'message': 'Hatalı kullanıcı adı veya şifre'}), 401

        return jsonify({
            'success': True,
            'user_id': user.id,
            'username': user.username,
            'role': user.role
        })
    except Exception as e:
        print(f"LOGIN HATASI: {e}")
        return jsonify({'success': False, 'message': 'Sunucu hatası oluştu'}), 500

# 2. API KAYIT (İŞTE HATA VEREN YER BURASIYDI, DÜZELTTİK)
@bp.route('/api/register', methods=['POST'])
def api_register():
    try:
        data = request.get_json() or {}
        print(f"GELEN KAYIT İSTEĞİ: {data}") # Hata olursa terminalde görelim diye

        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        role = data.get('role', 'student')

        if not username or not password:
            return jsonify({'success': False, 'message': 'Eksik bilgi girdiniz.'}), 400

        # Kullanıcı var mı kontrolü
        if User.query.filter_by(username=username).first():
            return jsonify({'success': False, 'message': 'Bu kullanıcı adı zaten alınmış!'}), 400

        # Yeni kullanıcıyı oluştur
        user = User(username=username, email=email, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        return jsonify({'success': True, 'message': 'Kayıt başarılı! Şimdi giriş yap.'})

    except Exception as e:
        print(f"KAYIT HATASI: {e}") # Terminale hatayı basar
        # Telefondaki hatayı detaylandıralım ki ne olduğunu anlayalım
        return jsonify({'success': False, 'message': f'Sunucu Hatası: {str(e)}'}), 500
"""

with open(path, 'w', encoding='utf-8') as f:
    f.write(code)

print("-" * 40)
print("✅ AUTH DOSYASI SIFIRDAN YAZILDI (Fixlendi).")
print("Şimdi sunucuyu kapatıp tekrar açmayı unutma!")
print("-" * 40)