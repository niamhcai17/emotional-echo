#!/usr/bin/env python3
"""
Script para probar la funcionalidad multilingüe y Supabase
"""

import os
from dotenv import load_dotenv
from openai_service import generate_poetic_phrase, detect_language
from supabase_service import supabase_service

# Cargar variables de entorno
load_dotenv()

def test_language_detection():
    """Prueba la detección de idioma"""
    print("🔍 Probando detección de idioma...")
    
    test_phrases = [
        "I feel happy today",
        "Me siento triste hoy",
        "I am excited about the future",
        "Estoy emocionado por el futuro",
        "The weather is beautiful",
        "El clima está hermoso"
    ]
    
    for phrase in test_phrases:
        detected = detect_language(phrase)
        print(f"  '{phrase}' → {detected}")

def test_phrase_generation():
    """Prueba la generación de frases en ambos idiomas"""
    print("\n✨ Probando generación de frases...")
    
    test_emotions = [
        ("I feel happy and grateful", "en"),
        ("Me siento triste y solo", "es"),
        ("I am excited about my new job", "en"),
        ("Estoy emocionado por mi nuevo trabajo", "es")
    ]
    
    for emotion, expected_lang in test_emotions:
        print(f"\n  Emoción: '{emotion}' (esperado: {expected_lang})")
        try:
            phrase, detected_lang = generate_poetic_phrase(emotion, "poetica_minimalista")
            if phrase:
                print(f"    Frase generada: '{phrase}'")
                print(f"    Idioma detectado: {detected_lang}")
                print(f"    ✅ Coincide: {detected_lang == expected_lang}")
            else:
                print(f"    ❌ Error generando frase")
        except Exception as e:
            print(f"    ❌ Error: {e}")

def test_supabase_integration():
    """Prueba la integración con Supabase"""
    print("\n🗄️  Probando integración con Supabase...")
    
    try:
        # Obtener estadísticas
        stats = supabase_service.get_stats()
        print(f"  📊 Estadísticas actuales:")
        print(f"    Total de frases: {stats['total_phrases']}")
        print(f"    Frases favoritas: {stats['favorite_phrases']}")
        print(f"    Distribución por idioma: {stats['language_stats']}")
        
        # Obtener frases por idioma
        spanish_phrases = supabase_service.get_phrases_by_language('es')
        english_phrases = supabase_service.get_phrases_by_language('en')
        
        print(f"    Frases en español: {len(spanish_phrases)}")
        print(f"    Frases en inglés: {len(english_phrases)}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error con Supabase: {e}")
        return False

def test_create_multilingual_phrases():
    """Crea frases de prueba en ambos idiomas"""
    print("\n📝 Creando frases de prueba...")
    
    test_data = [
        ("I feel happy today", "poetica_minimalista"),
        ("Me siento triste hoy", "reflexiva"),
        ("I am excited about the future", "indirecta_redes"),
        ("Estoy emocionado por el futuro", "diario_intimo")
    ]
    
    created_phrases = []
    
    for emotion, style in test_data:
        try:
            phrase, language = generate_poetic_phrase(emotion, style)
            if phrase:
                # Guardar en Supabase
                saved_phrase = supabase_service.create_phrase(
                    original_emotion=emotion,
                    style=style,
                    generated_phrase=phrase,
                    language=language
                )
                
                if saved_phrase:
                    created_phrases.append(saved_phrase)
                    print(f"  ✅ Creada: '{phrase}' ({language})")
                else:
                    print(f"  ❌ Error guardando frase")
            else:
                print(f"  ❌ Error generando frase para: {emotion}")
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    return created_phrases

def main():
    """Función principal"""
    print("🚀 Iniciando pruebas multilingües...")
    print("=" * 50)
    
    # Probar detección de idioma
    test_language_detection()
    
    # Probar generación de frases
    test_phrase_generation()
    
    # Probar integración con Supabase
    if test_supabase_integration():
        # Crear frases de prueba
        created = test_create_multilingual_phrases()
        
        if created:
            print(f"\n✅ Se crearon {len(created)} frases de prueba")
            
            # Mostrar estadísticas finales
            final_stats = supabase_service.get_stats()
            print(f"\n📊 Estadísticas finales:")
            print(f"    Total de frases: {final_stats['total_phrases']}")
            print(f"    Distribución por idioma: {final_stats['language_stats']}")
    
    print("\n🎉 Pruebas completadas!")

if __name__ == "__main__":
    main()
