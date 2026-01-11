from app import db, login_manager # <-- DÜZELTME: app.extensions yerine app'ten alıyoruz
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20)) # 'student' veya 'teacher' olabilir
    
    # İlişkiler
    enrolled_classes = db.relationship('Classroom', secondary='enrollments', backref=db.backref('students', lazy='dynamic'), lazy='dynamic')
    progress = db.relationship('Progress', backref='student', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Bu kısım kullanıcının oturumunu yönetir
@login_manager.user_loader
def load_user(id):
    return db.session.get(User, int(id))

class Classroom(db.Model):
    __tablename__ = 'classroom'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    teacher_name = db.Column(db.String(120), default="Bilinmiyor")
    topics = db.relationship('Topic', backref='classroom', lazy='dynamic')
    
    def __repr__(self):
        return f'<Classroom {self.name}>'

class Topic(db.Model):
    __tablename__ = 'topic'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    is_covered = db.Column(db.Boolean, default=False)
    classroom_id = db.Column(db.Integer, db.ForeignKey('classroom.id'))

    def __repr__(self):
        return f'<Topic {self.name}>'

class Progress(db.Model):
    __tablename__ = 'progress'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'))
    status = db.Column(db.String(20)) # 'done' veya 'missing'

# Ara tablo (Çoka-çok ilişki için)
enrollments = db.Table('enrollments',
    db.Column('student_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('classroom_id', db.Integer, db.ForeignKey('classroom.id'))
)