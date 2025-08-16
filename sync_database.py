#!/usr/bin/env python3
"""
Script para sincronizar datos entre base de datos local y producción
"""

import os
import sqlite3
import json
from datetime import datetime

def export_local_data():
    """Exporta datos de SQLite local a JSON"""
    
    sqlite_path = os.path.join('instance', 'entrelineas.db')
    
    if not os.path.exists(sqlite_path):
        print("❌ No se encontró la base de datos local")
        return None
    
    try:
        conn = sqlite3.connect(sqlite_path)
        cursor = conn.cursor()
        
        # Obtener estructura de la tabla
        cursor.execute("PRAGMA table_info(phrase)")
        columns = [col[1] for col in cursor.fetchall()]
        
        # Obtener todas las frases
        cursor.execute("SELECT * FROM phrase ORDER BY created_at DESC")
        phrases = cursor.fetchall()
        
        # Convertir a formato JSON
        data = []
        for phrase in phrases:
            phrase_dict = dict(zip(columns, phrase))
            # Convertir datetime a string para JSON
            if 'created_at' in phrase_dict and phrase_dict['created_at']:
                phrase_dict['created_at'] = str(phrase_dict['created_at'])
            data.append(phrase_dict)
        
        conn.close()
        
        # Guardar en archivo JSON
        export_file = 'local_data_export.json'
        with open(export_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Exportadas {len(data)} frases a {export_file}")
        return export_file
        
    except Exception as e:
        print(f"❌ Error exportando datos: {e}")
        return None

def import_to_production(export_file):
    """Importa datos desde JSON a producción (PostgreSQL)"""
    
    if not os.path.exists(export_file):
        print(f"❌ No se encontró el archivo {export_file}")
        return
    
    try:
        # Cargar datos desde JSON
        with open(export_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"📚 Cargadas {len(data)} frases desde {export_file}")
        
        # Aquí necesitarías conectarte a tu base de datos de producción
        # Por ahora, solo mostramos los datos
        print("\n📋 Datos a importar:")
        for i, phrase in enumerate(data, 1):
            print(f"  {i}. {phrase.get('original_emotion', 'N/A')} -> {phrase.get('generated_phrase', 'N/A')[:50]}...")
        
        print("\n💡 Para importar a producción:")
        print("1. Configura DATABASE_URL en Render")
        print("2. Ejecuta: python database_setup.py")
        print("3. Los datos se migrarán automáticamente")
        
    except Exception as e:
        print(f"❌ Error importando datos: {e}")

def backup_local_database():
    """Crea un backup de la base de datos local"""
    
    sqlite_path = os.path.join('instance', 'entrelineas.db')
    backup_path = f"backup_entrelineas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    
    if not os.path.exists(sqlite_path):
        print("❌ No se encontró la base de datos local")
        return
    
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
    
    print("🔄 Sincronización de Base de Datos")
    print("=" * 40)
    
    while True:
        print("\n📋 Opciones:")
        print("1. Exportar datos locales a JSON")
        print("2. Crear backup de base de datos local")
        print("3. Ver contenido de exportación")
        print("4. Salir")
        
        choice = input("\nSelecciona una opción (1-4): ").strip()
        
        if choice == "1":
            export_file = export_local_data()
            if export_file:
                print(f"\n📁 Archivo creado: {export_file}")
        
        elif choice == "2":
            backup_file = backup_local_database()
            if backup_file:
                print(f"\n💾 Backup guardado: {backup_file}")
        
        elif choice == "3":
            export_file = 'local_data_export.json'
            if os.path.exists(export_file):
                import_to_production(export_file)
            else:
                print("❌ No hay archivo de exportación. Ejecuta la opción 1 primero.")
        
        elif choice == "4":
            print("👋 ¡Hasta luego!")
            break
        
        else:
            print("❌ Opción inválida. Intenta de nuevo.")

if __name__ == "__main__":
    main() 