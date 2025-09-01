#!/usr/bin/env python3
"""
Modelos de datos para la aplicación
Definiciones de estructuras de datos compatibles con Supabase
"""

from datetime import datetime
from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict

@dataclass
class User:
    """Modelo de usuario"""
    id: str
    email: str
    full_name: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el modelo a diccionario"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """Crea un usuario desde un diccionario"""
        return cls(**data)

@dataclass
class Phrase:
    """Modelo de frase poética"""
    id: str
    user_id: str
    original_emotion: str
    style: str
    generated_phrase: str
    language: str = 'es'
    is_favorite: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el modelo a diccionario"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Phrase':
        """Crea una frase desde un diccionario"""
        return cls(**data)
    
    def __repr__(self) -> str:
        return f'<Phrase {self.id}: {self.generated_phrase[:30]}...>'

# Constantes para estilos de frases
STYLE_OPTIONS = {
    'poetica_minimalista': 'Poética Minimalista',
    'romantica_clasica': 'Romántica Clásica',
    'moderna_urbana': 'Moderna Urbana',
    'filosofica_profunda': 'Filosófica Profunda',
    'naturaleza_organica': 'Naturaleza Orgánica'
}

# Constantes para idiomas
LANGUAGE_OPTIONS = {
    'es': 'Español',
    'en': 'English'
}
