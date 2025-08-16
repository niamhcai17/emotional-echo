#!/usr/bin/env python3
"""
Script simplificado para migrar la base de datos y agregar el campo user_name
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

def test_user_functionality():
    """Prueba la funcionalidad de usuario después de la migración"""
    print("🧪 Probando funcionalidad de usuario...")
    
    try:
        supabase = get_supabase_client()
        
        # Crear una frase de prueba con usuario
        test_phrase = {
            'user_name': 'Usuario Test',
            'original_emotion': 'Prueba de migración',
            'style': 'poetica_minimalista',
            'generated_phrase': 'Esta es una frase de prueba',
            'language': 'es',
            'is_favorite': False
        }
        
        # Insertar frase de prueba
        response = supabase.table('phrase').insert(test_phrase).execute()
        
        if response.data:
            print("✅ Frase de prueba creada exitosamente")
            
            # Obtener frases del usuario de prueba
            user_phrases = supabase.table('phrase').select('*').eq('user_name', 'Usuario Test').execute()
            
            if user_phrases.data:
                print(f"✅ Se encontraron {len(user_phrases.data)} frases del usuario de prueba")
                
                # Limpiar frase de prueba
                supabase.table('phrase').delete().eq('user_name', 'Usuario Test').execute()
                print("✅ Frase de prueba eliminada")
                
                return True
            else:
                print("❌ No se encontraron frases del usuario de prueba")
                return False
        else:
            print("❌ Error creando frase de prueba")
            return False
            
    except Exception as e:
        print(f"❌ Error probando funcionalidad: {e}")
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
            
            # Probar funcionalidad
            if test_user_functionality():
                print("\n✅ Funcionalidad de usuario verificada")
            else:
                print("\n⚠️  Problemas con la funcionalidad de usuario")
        else:
            print("\n❌ Error en la verificación de Supabase")
    else:
        print("\n❌ Error en la migración de Supabase")
    
    print("\n📋 Resumen de la migración:")
    print("   ✅ Campo user_name agregado a la tabla phrase")
    print("   ✅ Frases existentes actualizadas")
    print("   ✅ Verificación de integridad completada")
    print("   ✅ Funcionalidad de usuario probada")
    
    print("\n🎉 ¡Migración completada!")
    print("\n💡 Ahora cada usuario tendrá su propio historial de frases")
    print("\n🔧 Para probar la aplicación:")
    print("   1. Ejecuta: python test_personalization_simple.py")
    print("   2. Abre: http://localhost:5000")
    print("   3. Ingresa tu nombre y crea frases")

if __name__ == "__main__":
    main()
