#!/usr/bin/env python3
"""
Script para migrar datos de SQLite local a Supabase
"""

import os
import sqlite3
from datetime import datetime
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

def migrate_to_supabase():
    """Migra datos de SQLite local a Supabase"""
    
    # Verificar que Supabase esté configurado
    SUPABASE_URL = os.environ.get("SUPABASE_URL")
    print("🔍 SUPABASE_URL:", SUPABASE_URL)
    SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
    print("🔍 SUPABASE_KEY:", SUPABASE_KEY[:10] + "..." if SUPABASE_KEY else "No encontrada")
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ Error: SUPABASE_URL y SUPABASE_KEY deben estar configurados")
        print("💡 Configura las variables de entorno en el archivo .env antes de ejecutar este script")
        print("📝 Ejemplo de .env:")
        print("   SUPABASE_URL=https://tu-proyecto.supabase.co")
        print("   SUPABASE_KEY=tu-anon-key-aqui")
        return False
    
    # Verificar que existe la base de datos local
    sqlite_path = os.path.join('instance', 'entrelineas.db')
    if not os.path.exists(sqlite_path):
        print("❌ No se encontró la base de datos local")
        return False
    
    try:
        # Conectar a SQLite local
        sqlite_conn = sqlite3.connect(sqlite_path)
        sqlite_cursor = sqlite_conn.cursor()
        
        # Obtener todas las frases
        sqlite_cursor.execute("SELECT * FROM phrase ORDER BY created_at DESC")
        phrases = sqlite_cursor.fetchall()
        
        print(f"📚 Encontradas {len(phrases)} frases en SQLite local")
        
        if len(phrases) == 0:
            print("ℹ️  No hay frases para migrar")
            return True
        
        # Importar servicio de Supabase
        from supabase_service import supabase_service
        
        # Verificar si ya existen datos en Supabase
        existing_phrases = supabase_service.get_all_phrases()
        if existing_phrases:
            print(f"⚠️  Ya existen {len(existing_phrases)} frases en Supabase")
            response = input("¿Deseas continuar con la migración? (s/n): ").strip().lower()
            if response != 's':
                print("❌ Migración cancelada")
                return False
        
        # Migrar cada frase
        migrated_count = 0
        for phrase_data in phrases:
            try:
                # Crear la frase en Supabase
                phrase = supabase_service.create_phrase(
                    original_emotion=phrase_data[1],
                    style=phrase_data[2],
                    generated_phrase=phrase_data[3],
                    language=phrase_data[6] if len(phrase_data) > 6 else 'es'
                )
                
                if phrase:
                    migrated_count += 1
                    print(f"✅ Migrada frase #{migrated_count}: {phrase_data[1][:30]}...")
                else:
                    print(f"❌ Error migrando frase: {phrase_data[1][:30]}...")
                    
            except Exception as e:
                print(f"❌ Error migrando frase: {e}")
        
        sqlite_conn.close()
        
        print(f"\n🎉 Migración completada: {migrated_count}/{len(phrases)} frases migradas")
        
        # Mostrar estadísticas finales
        stats = supabase_service.get_stats()
        print(f"\n📊 Estadísticas en Supabase:")
        print(f"  - Total de frases: {stats['total_phrases']}")
        print(f"  - Frases favoritas: {stats['favorite_phrases']}")
        print(f"  - Distribución por idioma: {stats['language_stats']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error durante la migración: {e}")
        return False

def backup_local_database():
    """Crea un backup de la base de datos local antes de migrar"""
    
    sqlite_path = os.path.join('instance', 'entrelineas.db')
    backup_path = f"backup_entrelineas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    
    if not os.path.exists(sqlite_path):
        print("❌ No se encontró la base de datos local")
        return None
    
    try:
        import shutil
        shutil.copy2(sqlite_path, backup_path)
        print(f"✅ Backup creado: {backup_path}")
        return backup_path
    except Exception as e:
        print(f"❌ Error creando backup: {e}")
        return None

def main():
    """Función principal"""
    
    print("🔄 Migración a Supabase")
    print("=" * 40)
    
    # Crear backup
    print("\n📦 Creando backup de la base de datos local...")
    backup_file = backup_local_database()
    
    if not backup_file:
        print("❌ No se pudo crear el backup. ¿Deseas continuar? (s/n): ")
        response = input().strip().lower()
        if response != 's':
            print("❌ Migración cancelada")
            return
    
    # Ejecutar migración
    print("\n🚀 Iniciando migración a Supabase...")
    success = migrate_to_supabase()
    
    if success:
        print("\n✅ Migración completada exitosamente!")
        print("💡 Ahora puedes configurar las variables de entorno en Render:")
        print("   - SUPABASE_URL")
        print("   - SUPABASE_KEY")
    else:
        print("\n❌ La migración falló. Revisa los errores arriba.")

if __name__ == "__main__":
    main() 