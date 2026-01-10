import os

# Yollar
base_dir = os.getcwd()
main_dir = os.path.join(base_dir, 'app', 'main')

# 1. Klasörü Oluştur
if not os.path.exists(main_dir):
    os.makedirs(main_dir)
    print("✅ 'app/main' klasörü oluşturuldu.")

# 2. __init__.py Oluştur
init_code = """from flask import Blueprint

bp = Blueprint('main', __name__)

from app.main import routes
"""
with open(os.path.join(main_dir, '__init__.py'), 'w', encoding='utf-8') as f:
    f.write(init_code)

# 3. routes.py Oluştur (Ana Sayfa Karşılaması)
routes_code = """from flask import jsonify
from app.main import bp

@bp.route('/')
def index():
    return jsonify({
        'status': 'success',
        'message': 'OKUL BACKEND CALISIYOR! (Render)',
        'version': '1.0'
    })
"""
with open(os.path.join(main_dir, 'routes.py'), 'w', encoding='utf-8') as f:
    f.write(routes_code)

print("✅ EKSİK PARÇALAR TAMAMLANDI.")
print("Şimdi git komutlarını çalıştır.")