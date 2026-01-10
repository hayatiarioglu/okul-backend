from app import create_app, db
from app.models import User, Classroom, Topic, Progress
from datetime import datetime

app = create_app()

with app.app_context():
    print("☁️ VERİTABANI KURULUYOR...")
    db.create_all()
    
    if not User.query.filter_by(username='deneme').first():
        print("🌱 Veriler ekleniyor...")
        # Kullanıcılar
        u = User(username='deneme', email='test@okul.com', role='student'); u.set_password('1234')
        h = User(username='hoca', email='hoca@okul.com', role='teacher'); h.set_password('1234')
        db.session.add_all([u, h])
        db.session.commit()
        
        # Sınıf
        c = Classroom(name="Bulut Sınıfı", teacher_name="Sistem", join_code="BULUT1")
        db.session.add(c)
        db.session.commit()
        u.enrolled_classes.append(c)
        
        # Konu
        t = Topic(name="Veritabanı Bağlantısı", classroom_id=c.id)
        db.session.add(t)
        db.session.commit()
        
        # İlerleme (Kırmızı Kutu)
        p = Progress(student_id=u.id, topic_id=t.id, status='missing', last_reviewed=datetime.utcnow())
        db.session.add(p)
        db.session.commit()
        print("✅ TAMAMLANDI! Kullanıcı: deneme / 1234")
    else:
        print("⚠️ Zaten veri var.")