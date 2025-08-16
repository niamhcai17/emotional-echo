#!/usr/bin/env python3
"""
Configuración para Supabase
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Cargar variables de entorno desde .env
load_dotenv()

# Configuración de Supabase
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

def get_supabase_client() -> Client:
    """Crea y retorna el cliente de Supabase"""
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("SUPABASE_URL y SUPABASE_KEY deben estar configurados")
    
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def test_supabase_connection():
    """Prueba la conexión con Supabase"""
    try:
        supabase = get_supabase_client()
        
        # Intentar hacer una consulta simple
        response = supabase.table('phrase').select('*').limit(1).execute()
        
        print("✅ Conexión a Supabase exitosa")
        print(f"📊 Tabla 'phrase' encontrada")
        return True
        
    except Exception as e:
        print(f"❌ Error conectando a Supabase: {e}")
        return False

def create_tables_supabase():
    """Crea las tablas en Supabase usando SQL"""
    
    # SQL para crear la tabla phrase
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS phrase (
        id SERIAL PRIMARY KEY,
        user_name VARCHAR(50),
        original_emotion TEXT NOT NULL,
        style VARCHAR(50) NOT NULL,
        generated_phrase VARCHAR(200) NOT NULL,
        language VARCHAR(2) DEFAULT 'es',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_favorite BOOLEAN DEFAULT FALSE
    );
    """
    
    try:
        supabase = get_supabase_client()
        
        # Ejecutar SQL para crear tabla
        result = supabase.rpc('exec_sql', {'sql': create_table_sql}).execute()
        
        print("✅ Tabla 'phrase' creada en Supabase")
        return True
        
    except Exception as e:
        print(f"⚠️  La tabla ya existe o error: {e}")
        return True  # Asumimos que la tabla ya existe

if __name__ == "__main__":
    print("🔄 Probando conexión con Supabase...")
    print(f"🔍 SUPABASE_URL: {SUPABASE_URL}")
    print(f"🔍 SUPABASE_KEY: {SUPABASE_KEY[:10] + '...' if SUPABASE_KEY else 'No encontrada'}")
    
    if test_supabase_connection():
        print("✅ Configuración de Supabase completada")
    else:
        print("❌ Verifica las variables de entorno SUPABASE_URL y SUPABASE_KEY")
        print("💡 Asegúrate de que el archivo .env esté configurado correctamente") 