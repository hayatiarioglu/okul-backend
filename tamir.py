import os

# Neredeyiz?
base_dir = os.getcwd()

# 1. AUTH MODÜLÜNÜ DÜZELT (Hata veren yer)
path_auth = os.path.join(base_dir, 'app', 'auth', '__init__.py')
with open(path_auth, 'w') as f:
    f.write("from .routes import bp")

# 2. STUDENT MODÜLÜNÜ DÜZELT (Sıradaki hata vermesin diye)
path_student = os.path.join(base_dir, 'app', 'student', '__init__.py')
with open(path_student, 'w') as f:
    f.write("from .routes import bp")

print("-" * 30)
print("✅ KABLO KOPUKLUĞU GİDERİLDİ.")
print("Şimdi tekrar 'python run.py' yazabilirsin.")
print("-" * 30)