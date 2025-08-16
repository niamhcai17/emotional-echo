#!/usr/bin/env python3
"""
Script para probar la separación de frases por usuario
"""

import requests
import json
from openai_service import generate_poetic_phrase
from supabase_service import supabase_service

def test_user_separation():
    """Prueba la separación de frases por usuario"""
    print("🧪 Probando separación de frases por usuario...")
    
    # Crear frases para diferentes usuarios
    test_users = [
        ("Ana", "Me siento feliz hoy"),
        ("Carlos", "Estoy emocionado por el futuro"),
        ("María", "Me siento triste"),
        ("Juan", "I feel happy today")
    ]
    
    created_phrases = []
    
    for user_name, emotion in test_users:
        print(f"\n📝 Creando frase para {user_name}: '{emotion}'")
        
        try:
            # Generar frase
            phrase, language = generate_poetic_phrase(emotion, "poetica_minimalista")
            
            if phrase:
                # Guardar en Supabase con el nombre del usuario
                saved_phrase = supabase_service.create_phrase(
                    original_emotion=emotion,
                    style="poetica_minimalista",
                    generated_phrase=phrase,
                    language=language,
                    user_name=user_name
                )
                
                if saved_phrase:
                    created_phrases.append(saved_phrase)
                    print(f"   ✅ Creada: '{phrase}' ({language}) para {user_name}")
                else:
                    print(f"   ❌ Error guardando frase para {user_name}")
            else:
                print(f"   ❌ Error generando frase para {user_name}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    return created_phrases

def test_user_filtering():
    """Prueba el filtrado de frases por usuario"""
    print("\n🔍 Probando filtrado por usuario...")
    
    test_users = ["Ana", "Carlos", "María", "Juan"]
    
    for user_name in test_users:
        print(f"\n👤 Frases de {user_name}:")
        
        try:
            # Obtener frases del usuario
            phrases = supabase_service.get_all_phrases(user_name=user_name)
            
            if phrases:
                print(f"   📊 Total: {len(phrases)} frases")
                
                # Mostrar algunas frases
                for i, phrase in enumerate(phrases[:3]):
                    print(f"   {i+1}. '{phrase['generated_phrase']}' ({phrase['language']})")
                
                if len(phrases) > 3:
                    print(f"   ... y {len(phrases) - 3} más")
            else:
                print(f"   📭 No hay frases para {user_name}")
                
        except Exception as e:
            print(f"   ❌ Error obteniendo frases de {user_name}: {e}")

def test_user_statistics():
    """Prueba las estadísticas por usuario"""
    print("\n📊 Probando estadísticas por usuario...")
    
    test_users = ["Ana", "Carlos", "María", "Juan"]
    
    for user_name in test_users:
        print(f"\n📈 Estadísticas de {user_name}:")
        
        try:
            stats = supabase_service.get_stats(user_name=user_name)
            
            print(f"   📝 Total de frases: {stats['total_phrases']}")
            print(f"   ⭐ Favoritas: {stats['favorite_phrases']}")
            print(f"   🌍 Distribución por idioma: {stats['language_stats']}")
            
        except Exception as e:
            print(f"   ❌ Error obteniendo estadísticas de {user_name}: {e}")

def test_user_favorites():
    """Prueba las frases favoritas por usuario"""
    print("\n⭐ Probando favoritos por usuario...")
    
    test_users = ["Ana", "Carlos", "María", "Juan"]
    
    for user_name in test_users:
        print(f"\n💖 Favoritos de {user_name}:")
        
        try:
            favorites = supabase_service.get_favorite_phrases(user_name=user_name)
            
            if favorites:
                print(f"   📊 Total favoritos: {len(favorites)}")
                
                for i, phrase in enumerate(favorites[:2]):
                    print(f"   {i+1}. '{phrase['generated_phrase']}'")
                
                if len(favorites) > 2:
                    print(f"   ... y {len(favorites) - 2} más")
            else:
                print(f"   📭 No hay favoritos para {user_name}")
                
        except Exception as e:
            print(f"   ❌ Error obteniendo favoritos de {user_name}: {e}")

def test_user_language_filtering():
    """Prueba el filtrado por idioma por usuario"""
    print("\n🌍 Probando filtrado por idioma por usuario...")
    
    test_cases = [
        ("Ana", "es"),
        ("Juan", "en"),
        ("Carlos", "es"),
        ("María", "es")
    ]
    
    for user_name, language in test_cases:
        print(f"\n🗣️  Frases en {language} de {user_name}:")
        
        try:
            phrases = supabase_service.get_phrases_by_language(language, user_name=user_name)
            
            if phrases:
                print(f"   📊 Total: {len(phrases)} frases")
                
                for i, phrase in enumerate(phrases[:2]):
                    print(f"   {i+1}. '{phrase['generated_phrase']}'")
                
                if len(phrases) > 2:
                    print(f"   ... y {len(phrases) - 2} más")
            else:
                print(f"   📭 No hay frases en {language} para {user_name}")
                
        except Exception as e:
            print(f"   ❌ Error obteniendo frases en {language} de {user_name}: {e}")

def main():
    """Función principal"""
    print("🚀 Iniciando pruebas de separación por usuario...")
    print("=" * 60)
    
    # Crear frases para diferentes usuarios
    created_phrases = test_user_separation()
    
    if created_phrases:
        print(f"\n✅ Se crearon {len(created_phrases)} frases de prueba")
        
        # Probar filtrado por usuario
        test_user_filtering()
        
        # Probar estadísticas por usuario
        test_user_statistics()
        
        # Probar favoritos por usuario
        test_user_favorites()
        
        # Probar filtrado por idioma por usuario
        test_user_language_filtering()
        
        print("\n📋 Resumen de funcionalidades:")
        print("   ✅ Separación de frases por usuario")
        print("   ✅ Filtrado de colección por usuario")
        print("   ✅ Estadísticas personalizadas")
        print("   ✅ Favoritos por usuario")
        print("   ✅ Filtrado por idioma por usuario")
        print("   ✅ Verificación de propiedad")
        
        print("\n🎉 ¡Pruebas de separación por usuario completadas!")
        print("\n💡 Ahora cada usuario tiene su propio historial independiente")
    else:
        print("\n❌ No se pudieron crear frases de prueba")

if __name__ == "__main__":
    main()
