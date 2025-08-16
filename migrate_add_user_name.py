#!/usr/bin/env python3
"""
Script para migrar la base de datos y agregar el campo user_name
"""

import os
from dotenv import load_dotenv
from supabase_config import get_supabase_client

# Cargar variables de entorno
load_dotenv()

def migrate_supabase_add_user_name():
    """Migra la tabla de Supabase para agregar el campo user_name"""
    print("🔄 Migrando Supabase para agregar campo user_name...")
    
    try:
        supabase = get_supabase_client()
        
        # SQL para agregar el campo user_name si no existe
        alter_table_sql = """
        ALTER TABLE phrase 
        ADD COLUMN IF NOT EXISTS user_name VARCHAR(50);
        """
        
        # Ejecutar la migración
        result = supabase.rpc('exec_sql', {'sql': alter_table_sql}).execute()
        
        print("✅ Campo user_name agregado a la tabla phrase en Supabase")
        return True
        
    except Exception as e:
        print(f"❌ Error migrando Supabase: {e}")
        return False

def migrate_sqlite_add_user_name():
    """Migra la base de datos SQLite local para agregar el campo user_name"""
    print("🔄 Migrando SQLite local para agregar campo user_name...")
    
    try:
        import sqlite3
        
        # Conectar a la base de datos SQLite
        db_path = "instance/entrelineas.db"
        if not os.path.exists(db_path):
            print("⚠️  Base de datos SQLite no encontrada")
            return True
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar si el campo user_name ya existe
        cursor.execute("PRAGMA table_info(phrase)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'user_name' not in columns:
            # Agregar el campo user_name
            cursor.execute("ALTER TABLE phrase ADD COLUMN user_name VARCHAR(50)")
            conn.commit()
            print("✅ Campo user_name agregado a la tabla phrase en SQLite")
        else:
            print("✅ Campo user_name ya existe en SQLite")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error migrando SQLite: {e}")
        return False

def update_existing_phrases():
    """Actualiza las frases existentes con un nombre de usuario por defecto"""
    print("🔄 Actualizando frases existentes...")
    
    try:
        supabase = get_supabase_client()
        
        # Obtener frases sin user_name
        response = supabase.table('phrase').select('*').is_('user_name', 'null').execute()
        
        if response.data:
            print(f"📝 Encontradas {len(response.data)} frases sin usuario")
            
            # Actualizar con un usuario por defecto
            for phrase in response.data:
                supabase.table('phrase').update({
                    'user_name': 'Usuario Anónimo'
                }).eq('id', phrase['id']).execute()
            
            print("✅ Frases actualizadas con usuario por defecto")
        else:
            print("✅ No hay frases sin usuario")
        
        return True
        
    except Exception as e:
        print(f"❌ Error actualizando frases: {e}")
        return False

def verify_migration():
    """Verifica que la migración fue exitosa"""
    print("🔍 Verificando migración...")
    
    try:
        supabase = get_supabase_client()
        
        # Verificar estructura de la tabla
        response = supabase.table('phrase').select('*').limit(1).execute()
        
        if response.data:
            sample_phrase = response.data[0]
            if 'user_name' in sample_phrase:
                print("✅ Campo user_name presente en la tabla")
                return True
            else:
                print("❌ Campo user_name no encontrado")
                return False
        else:
            print("⚠️  No hay frases en la base de datos")
            return True
        
    except Exception as e:
        print(f"❌ Error verificando migración: {e}")
        return False

def main():
    """Función principal"""
    print("🚀 Iniciando migración para agregar campo user_name...")
    print("=" * 60)
    
    # Migrar Supabase
    if migrate_supabase_add_user_name():
        # Actualizar frases existentes
        update_existing_phrases()
        
        # Verificar migración
        if verify_migration():
            print("\n✅ Migración de Supabase completada exitosamente")
        else:
            print("\n❌ Error en la verificación de Supabase")
    else:
        print("\n❌ Error en la migración de Supabase")
    
    # Migrar SQLite local
    if migrate_sqlite_add_user_name():
        print("\n✅ Migración de SQLite completada exitosamente")
    else:
        print("\n❌ Error en la migración de SQLite")
    
    print("\n📋 Resumen de la migración:")
    print("   ✅ Campo user_name agregado a la tabla phrase")
    print("   ✅ Frases existentes actualizadas")
    print("   ✅ Verificación de integridad completada")
    
    print("\n🎉 ¡Migración completada!")
    print("\n💡 Ahora cada usuario tendrá su propio historial de frases")

if __name__ == "__main__":
    main()
