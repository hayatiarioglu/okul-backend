from app import create_app, db
from sqlalchemy import text

app = create_app()

with app.app_context():
    print("Veritabani temizleniyor...")
    # Postgres'e özel 'schema' silme komutu. Her şeyi (tabloları, tipleri) kökünden kazır.
    db.session.execute(text("DROP SCHEMA public CASCADE;"))
    db.session.execute(text("CREATE SCHEMA public;"))
    db.session.commit()
    print("Veritabani SIFIRLANDI. Tertemiz bir sayfa açtın.")