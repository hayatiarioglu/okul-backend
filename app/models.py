from app.extensions import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20))
    enrolled_classes = db.relationship('Classroom', secondary='enrollments', backref=db.backref('students', lazy='dynamic'), lazy='dynamic')
    progress = db.relationship('Progress', backref='student', lazy='dynamic') # YENİ

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(id):
    return db.session.get(User, int(id))

class Classroom(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    teacher_name = db.Column(db.String(120), default="Bilinmiyor")
    topics = db.relationship('Topic', backref='classroom', lazy='dynamic')

class Topic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    is_covered = db.Column(db.Boolean, default=False)
    classroom_id = db.Column(db.Integer, db.ForeignKey('classroom.id'))

# YENİ: İLERLEME TABLOSU
class Progress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'))
    status = db.Column(db.String(20)) # 'done' (Tamam) veya 'missing' (Eksik)

enrollments = db.Table('enrollments',
    db.Column('student_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('classroom_id', db.Integer, db.ForeignKey('classroom.id'))
)
