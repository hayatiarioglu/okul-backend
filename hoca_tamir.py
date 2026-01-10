import os

base_dir = os.getcwd()
teacher_init_path = os.path.join(base_dir, 'app', 'teacher', '__init__.py')

# Eksik olan dosyanın içeriği
kod = """from flask import Blueprint

bp = Blueprint('teacher', __name__)

from app.teacher import routes
"""

# Dosyayı zorla oluştur (Varsa da üzerine yaz)
with open(teacher_init_path, 'w', encoding='utf-8') as f:
    f.write(kod)

print("-" * 40)
print("✅ HOCA MODÜLÜ TAMİR EDİLDİ.")
print(f"Oluşturulan dosya: {teacher_init_path}")
print("Şimdi 'python run.py' çalıştırabilirsin.")
print("-" * 40)