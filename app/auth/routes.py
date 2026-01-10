from flask import Blueprint, jsonify, request, render_template, redirect, url_for, flash
from flask_login import current_user, login_user, logout_user, login_required
from app import db
from app.models import User
# Dikkat: bp'yi buradan çağırıyoruz ama __init__ içinde zaten oluşmuş olacak
from app.auth import bp

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
# MOBİL API ROTALARI
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
        print(f"LOGIN HATASI: {str(e)}")
        return jsonify({'success': False, 'message': 'Sunucu hatası oluştu'}), 500

# 2. API KAYIT
@bp.route('/api/register', methods=['POST'])
def api_register():
    try:
        data = request.get_json() or {}
        print(f"GELEN KAYIT İSTEĞİ: {data}")

        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        role = data.get('role', 'student')

        if not username or not password:
            return jsonify({'success': False, 'message': 'Eksik bilgi girdiniz.'}), 400

        if User.query.filter_by(username=username).first():
            return jsonify({'success': False, 'message': 'Bu kullanıcı adı zaten alınmış!'}), 400

        user = User(username=username, email=email, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        return jsonify({'success': True, 'message': 'Kayıt başarılı! Şimdi giriş yap.'})

    except Exception as e:
        print(f"KAYIT HATASI: {str(e)}")
        return jsonify({'success': False, 'message': f'Sunucu Hatası: {str(e)}'}), 500
