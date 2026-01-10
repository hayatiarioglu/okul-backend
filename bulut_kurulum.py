from app import create_app, db
from app.models import User, Classroom, Topic, Progress
from datetime import datetime, timedelta

app = create_app()

with app.app_context():
    print("☁️ BULUT VERİTABANI KURULUYOR...")
    
    # Tabloları oluştur
    db.create_all()
    print("✅ Tablolar oluşturuldu.")

    # Eğer hiç kullanıcı yoksa, örnek verileri bas
    if not User.query.first():
        print("🌱 İlk veriler ekleniyor...")
        
        # 1. Kullanıcı
        u = User(username='deneme', email='test@okul.com', role='student')
        u.set_password('1234')
        
        hoca = User(username='hoca1', email='hoca@okul.com', role='teacher')
        hoca.set_password('1234')
        
        db.session.add_all([u, hoca])
        db.session.commit()
        
        # 2. Sınıf
        c1 = Classroom(name="Cloud 101", teacher_name="Sistem Yöneticisi")
        db.session.add(c1)
        db.session.commit()
        
        # Öğrenciyi sınıfa ekle
        u.enrolled_classes.append(c1)
        
        # 3. Konu
        t1 = Topic(name="Sunucu Mimarisi", classroom_id=c1.id)
        db.session.add(t1)
        db.session.commit()
        
        # 4. İlerleme (Kırmızı kutu testi için)
        p1 = Progress(student_id=u.id, topic_id=t1.id, status='missing', last_reviewed=datetime.utcnow())
        db.session.add(p1)
        db.session.commit()
        
        print("✅ Örnek veriler (deneme/1234) eklendi.")
    else:
        print("⚠️ Veritabanı zaten dolu, dokunulmadı.")

print("🏁 İŞLEM TAMAM.")