from flask import jsonify
from app.main import bp

@bp.route('/')
def index():
    return jsonify({
        'status': 'success',
        'message': 'OKUL BACKEND CALISIYOR! (Render)',
        'version': '1.0'
    })
