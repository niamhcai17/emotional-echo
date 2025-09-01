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
    
    def get_user_info(self, user_id):
        """Obtiene información del usuario desde la tabla users"""
        try:
            response = self.supabase.table('users').select('*').eq('id', user_id).execute()
            if response.data:
                return response.data[0]
            return None
        except Exception as e:
            print(f"Error obteniendo información del usuario: {e}")
            return None
    
    def create_user(self, user_id, email, user_name):
        """Crea un nuevo usuario en la tabla users"""
        try:
            data = {
                'id': user_id,
                'email': email,
                'user_name': user_name,
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }
            
            response = self.supabase.table('users').insert(data).execute()
            
            if response.data:
                return response.data[0]
            return None
            
        except Exception as e:
            print(f"Error creando usuario: {e}")
            return None
    
    def update_user_info(self, user_id, update_data):
        """Actualiza información del usuario"""
        try:
            update_data['updated_at'] = datetime.utcnow().isoformat()
            
            response = self.supabase.table('users').update(update_data).eq('id', user_id).execute()
            
            if response.data:
                return response.data[0]
            return None
            
        except Exception as e:
            print(f"Error actualizando usuario: {e}")
            return None
    
    def create_phrase(self, user_id, original_emotion, style, phrase, language='es'):
        """Crea una nueva frase en Supabase"""
        try:
            data = {
                'user_id': user_id,
                'original_emotion': original_emotion,
                'style': style,
                'phrase': phrase,
                'language': language,
                'created_at': datetime.utcnow().isoformat(),
                'is_favorite': False
            }
            
            response = self.supabase.table('phrases').insert(data).execute()
            
            if response.data:
                return response.data[0]
            return None
            
        except Exception as e:
            print(f"Error creando frase: {e}")
            return None
    
    def get_all_phrases(self, user_id=None):
        """Obtiene todas las frases ordenadas por fecha de creación"""
        try:
            query = self.supabase.table('phrases').select('*').order('created_at', desc=True)
            
            if user_id:
                query = query.eq('user_id', user_id)
            
            response = query.execute()
            return response.data
        except Exception as e:
            print(f"Error obteniendo frases: {e}")
            return []
    
    def get_favorite_phrases(self, user_id=None):
        """Obtiene solo las frases favoritas"""
        try:
            query = self.supabase.table('phrases').select('*').eq('is_favorite', True).order('created_at', desc=True)
            
            if user_id:
                query = query.eq('user_id', user_id)
            
            response = query.execute()
            return response.data
        except Exception as e:
            print(f"Error obteniendo frases favoritas: {e}")
            return []
    
    def get_phrases_by_language(self, language, user_id=None):
        """Obtiene frases filtradas por idioma"""
        try:
            query = self.supabase.table('phrases').select('*').eq('language', language).order('created_at', desc=True)
            
            if user_id:
                query = query.eq('user_id', user_id)
            
            response = query.execute()
            return response.data
        except Exception as e:
            print(f"Error obteniendo frases por idioma: {e}")
            return []

    def get_phrase_by_id(self, phrase_id):
        """Obtiene una frase específica por ID"""
        try:
            response = self.supabase.table('phrases').select('*').eq('id', phrase_id).execute()
            if response.data:
                return response.data[0]
            return None
        except Exception as e:
            print(f"Error obteniendo frase por ID: {e}")
            return None

    def toggle_favorite(self, phrase_id):
        """Cambia el estado de favorito de una frase"""
        try:
            # Primero obtener la frase actual
            response = self.supabase.table('phrases').select('is_favorite').eq('id', phrase_id).execute()
            
            if response.data:
                current_favorite = response.data[0]['is_favorite']
                new_favorite = not current_favorite
                
                # Actualizar el estado
                update_response = self.supabase.table('phrases').update({'is_favorite': new_favorite}).eq('id', phrase_id).execute()
                
                return new_favorite
            return None
            
        except Exception as e:
            print(f"Error cambiando favorito: {e}")
            return None
    
    def delete_phrase(self, phrase_id):
        """Elimina una frase"""
        try:
            response = self.supabase.table('phrases').delete().eq('id', phrase_id).execute()
            return True
        except Exception as e:
            print(f"Error eliminando frase: {e}")
            return False
    
    def get_stats(self, user_id=None):
        """Obtiene estadísticas de la base de datos"""
        try:
            # Obtener todas las frases del usuario
            phrases = self.get_all_phrases(user_id)
            
            if not phrases:
                return {
                    'total_phrases': 0,
                    'favorite_phrases': 0,
                    'language_stats': {},
                    'style_stats': {},
                    'emotion_length_stats': {
                        'short': 0,  # < 50 caracteres
                        'medium': 0,  # 50-150 caracteres
                        'long': 0     # > 150 caracteres
                    }
                }
            
            # Calcular estadísticas
            total_phrases = len(phrases)
            favorite_phrases = len([p for p in phrases if p.get('is_favorite', False)])
            
            # Estadísticas por idioma
            language_stats = {}
            for phrase in phrases:
                lang = phrase.get('language', 'es')
                language_stats[lang] = language_stats.get(lang, 0) + 1
            
            # Estadísticas por estilo
            style_stats = {}
            for phrase in phrases:
                style = phrase.get('style', 'unknown')
                style_stats[style] = style_stats.get(style, 0) + 1
            
            # Estadísticas por longitud de emoción
            emotion_length_stats = {'short': 0, 'medium': 0, 'long': 0}
            for phrase in phrases:
                emotion_length = len(phrase.get('original_emotion', ''))
                if emotion_length < 50:
                    emotion_length_stats['short'] += 1
                elif emotion_length < 150:
                    emotion_length_stats['medium'] += 1
                else:
                    emotion_length_stats['long'] += 1
            
            return {
                'total_phrases': total_phrases,
                'favorite_phrases': favorite_phrases,
                'language_stats': language_stats,
                'style_stats': style_stats,
                'emotion_length_stats': emotion_length_stats
            }
            
        except Exception as e:
            print(f"Error obteniendo estadísticas: {e}")
            return {
                'total_phrases': 0,
                'favorite_phrases': 0,
                'language_stats': {},
                'style_stats': {},
                'emotion_length_stats': {'short': 0, 'medium': 0, 'long': 0}
            }

# Instancia global del servicio
supabase_service = SupabaseService() 