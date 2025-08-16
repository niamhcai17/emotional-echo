#!/usr/bin/env python3
"""
Servicio para manejar operaciones de base de datos con Supabase
"""

import os
from datetime import datetime
from dotenv import load_dotenv
from supabase_config import get_supabase_client

# Cargar variables de entorno desde .env
load_dotenv()

class SupabaseService:
    """Servicio para manejar operaciones de base de datos con Supabase"""
    
    def __init__(self):
        self.supabase = get_supabase_client()
    
    def create_phrase(self, original_emotion, style, generated_phrase, language='es', user_name=None):
        """Crea una nueva frase en Supabase"""
        try:
            data = {
                'user_name': user_name,
                'original_emotion': original_emotion,
                'style': style,
                'generated_phrase': generated_phrase,
                'language': language,
                'created_at': datetime.utcnow().isoformat(),
                'is_favorite': False
            }
            
            response = self.supabase.table('phrase').insert(data).execute()
            
            if response.data:
                return response.data[0]
            return None
            
        except Exception as e:
            print(f"Error creando frase: {e}")
            return None
    
    def get_all_phrases(self, user_name=None):
        """Obtiene todas las frases ordenadas por fecha de creación"""
        try:
            query = self.supabase.table('phrase').select('*').order('created_at', desc=True)
            
            if user_name:
                query = query.eq('user_name', user_name)
            
            response = query.execute()
            return response.data
        except Exception as e:
            print(f"Error obteniendo frases: {e}")
            return []
    
    def get_favorite_phrases(self, user_name=None):
        """Obtiene solo las frases favoritas"""
        try:
            query = self.supabase.table('phrase').select('*').eq('is_favorite', True).order('created_at', desc=True)
            
            if user_name:
                query = query.eq('user_name', user_name)
            
            response = query.execute()
            return response.data
        except Exception as e:
            print(f"Error obteniendo frases favoritas: {e}")
            return []
    
    def get_phrases_by_language(self, language, user_name=None):
        """Obtiene frases filtradas por idioma"""
        try:
            query = self.supabase.table('phrase').select('*').eq('language', language).order('created_at', desc=True)
            
            if user_name:
                query = query.eq('user_name', user_name)
            
            response = query.execute()
            return response.data
        except Exception as e:
            print(f"Error obteniendo frases por idioma: {e}")
            return []

    def toggle_favorite(self, phrase_id):
        """Cambia el estado de favorito de una frase"""
        try:
            # Primero obtener la frase actual
            response = self.supabase.table('phrase').select('is_favorite').eq('id', phrase_id).execute()
            
            if response.data:
                current_favorite = response.data[0]['is_favorite']
                new_favorite = not current_favorite
                
                # Actualizar el estado
                update_response = self.supabase.table('phrase').update({'is_favorite': new_favorite}).eq('id', phrase_id).execute()
                
                return new_favorite
            return None
            
        except Exception as e:
            print(f"Error cambiando favorito: {e}")
            return None
    
    def delete_phrase(self, phrase_id):
        """Elimina una frase por ID"""
        try:
            response = self.supabase.table('phrase').delete().eq('id', phrase_id).execute()
            return True
        except Exception as e:
            print(f"Error eliminando frase: {e}")
            return False
    
    def get_phrase_by_id(self, phrase_id):
        """Obtiene una frase específica por ID"""
        try:
            response = self.supabase.table('phrase').select('*').eq('id', phrase_id).execute()
            if response.data:
                return response.data[0]
            return None
        except Exception as e:
            print(f"Error obteniendo frase: {e}")
            return None
    
    def get_stats(self, user_name=None):
        """Obtiene estadísticas de la base de datos"""
        try:
            # Construir query base
            base_query = self.supabase.table('phrase').select('*')
            if user_name:
                base_query = base_query.eq('user_name', user_name)
            
            # Total de frases
            total_response = base_query.execute()
            total_phrases = len(total_response.data)
            
            # Frases favoritas
            favorites_query = base_query.eq('is_favorite', True)
            favorites_response = favorites_query.execute()
            favorite_phrases = len(favorites_response.data)
            
            # Distribución por idioma
            language_stats = {}
            for phrase in total_response.data:
                lang = phrase.get('language', 'es')
                language_stats[lang] = language_stats.get(lang, 0) + 1
            
            return {
                'total_phrases': total_phrases,
                'favorite_phrases': favorite_phrases,
                'language_stats': language_stats,
                'user_name': user_name
            }
            
        except Exception as e:
            print(f"Error obteniendo estadísticas: {e}")
            return {
                'total_phrases': 0,
                'favorite_phrases': 0,
                'language_stats': {},
                'user_name': user_name
            }

# Instancia global del servicio
supabase_service = SupabaseService() 