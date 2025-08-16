import os
import logging

from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging for debugging
logging.basicConfig(level=logging.DEBUG)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Verificar si Supabase está configurado
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if SUPABASE_URL and SUPABASE_KEY:
    # Usar Supabase
    print("🔗 Configurando Supabase...")
    try:
        from supabase_config import test_supabase_connection
        if test_supabase_connection():
            print("✅ Supabase configurado correctamente")
            USE_SUPABASE = True
        else:
            print("⚠️  Error en Supabase, usando SQLite local")
            USE_SUPABASE = False
    except Exception as e:
        print(f"⚠️  Error configurando Supabase: {e}")
        USE_SUPABASE = False
else:
    # Usar SQLite local
    print("📁 Usando SQLite local")
    USE_SUPABASE = False

# Configurar base de datos según disponibilidad
if USE_SUPABASE:
    # Importar servicio de Supabase
    from supabase_service import supabase_service
    print("✅ Aplicación configurada con Supabase")
else:
    # Configurar SQLite
    from database import db
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///entrelineas.db"
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    db.init_app(app)
    
    with app.app_context():
        import models
        db.create_all()
    print("✅ Aplicación configurada con SQLite local")

# Import routes
from routes import *

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
