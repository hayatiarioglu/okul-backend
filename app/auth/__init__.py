from flask import Blueprint

# Önce Blueprint'i oluşturuyoruz
bp = Blueprint('auth', __name__)

# SONRA rotaları çağırıyoruz (Sırf bu sıra yüzünden hata alıyordun)
from app.auth import routes
