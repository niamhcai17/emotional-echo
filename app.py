import os
import logging
from dotenv import load_dotenv

from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

# Cargar variables de entorno desde .env
load_dotenv()

# Configure logging for debugging
logging.basicConfig(level=logging.DEBUG)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Verificar si Supabase está configurado
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
SUPABASE_ANON_KEY = os.environ.get("SUPABASE_ANON_KEY")

if SUPABASE_URL and SUPABASE_KEY:
    # Usar Supabase
    print("🔗 Configurando Supabase...")
    try:
        from config.supabase_config import test_supabase_connection
        if test_supabase_connection():
            print("✅ Supabase configurado correctamente")
            USE_SUPABASE = True
        else:
            print("❌ Error en Supabase. Verifica tu configuración.")
            USE_SUPABASE = False
    except Exception as e:
        print(f"❌ Error configurando Supabase: {e}")
        USE_SUPABASE = False
else:
    # No hay configuración de Supabase
    print("❌ No se encontró configuración de Supabase")
    print("📝 Asegúrate de tener las variables SUPABASE_URL y SUPABASE_KEY en tu archivo .env")
    USE_SUPABASE = False

# Configurar variables de Supabase para el frontend
app.config['SUPABASE_URL'] = SUPABASE_URL
app.config['SUPABASE_ANON_KEY'] = SUPABASE_ANON_KEY

# Configurar base de datos
if USE_SUPABASE:
    # Importar servicio de Supabase
    from services.supabase_service import supabase_service
    print("✅ Aplicación configurada con Supabase")
else:
    print("❌ No se puede iniciar la aplicación sin Supabase configurado")
    print("📝 Por favor, configura Supabase en tu archivo .env")
    exit(1)

# Import routes
from routes import *

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
