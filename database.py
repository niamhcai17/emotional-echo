#!/usr/bin/env python3
"""
Módulo de base de datos para Supabase
Contiene helpers y funciones de conexión
"""

import os
from typing import Optional, Dict, Any
from supabase import create_client, Client
from config.supabase_config import get_supabase_client

class SupabaseDatabase:
    """Clase helper para operaciones de base de datos con Supabase"""
    
    def __init__(self):
        self.client = get_supabase_client()
    
    def test_connection(self) -> bool:
        """Prueba la conexión a Supabase"""
        try:
            # Intentar una consulta simple
            response = self.client.table('users').select('count').limit(1).execute()
            return True
        except Exception as e:
            print(f"Error de conexión a Supabase: {e}")
            return False
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene un usuario por ID"""
        try:
            response = self.client.table('users').select('*').eq('id', user_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error obteniendo usuario: {e}")
            return None
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Obtiene un usuario por email"""
        try:
            response = self.client.table('users').select('*').eq('email', email).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error obteniendo usuario por email: {e}")
            return None

# Instancia global de la base de datos
db = SupabaseDatabase() 