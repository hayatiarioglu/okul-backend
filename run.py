from app import create_app, db
from app.models import User

app = create_app()

# Uygulama her başladığında veritabanını kontrol et
with app.app_context():
    db.create_all()
    # Test kullanıcısı yoksa oluştur
    if not User.query.filter_by(username='deneme').first():
        print("🛠️ Test kullanıcısı 'deneme' oluşturuluyor...")
        u = User(username='deneme', email='deneme@okul.com', role='student')
        u.set_password('1234')
        db.session.add(u)
        db.session.commit()
        print("✅ Kullanıcı hazır: deneme / 1234")

if __name__ == '__main__':
    # 0.0.0.0 sayesinde telefondan erişilebilir
    app.run(debug=True, host='0.0.0.0', port=5000)
