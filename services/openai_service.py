import os
import json
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

# The newest OpenAI model is "gpt-4o" which was released May 13, 2024.
# Do not change this unless explicitly requested by the user
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

def detect_language(text):
    """
    Detect the language of the input text using OpenAI.
    Returns 'en' for English, 'es' for Spanish, or 'es' as default.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Detect the language of the following text. Respond only with 'en' for English or 'es' for Spanish."},
                {"role": "user", "content": f"Detect language: {text}"}
            ],
            max_tokens=5,
            temperature=0.1
        )
        
        detected_lang = response.choices[0].message.content.strip().lower()
        return 'en' if detected_lang == 'en' else 'es'
    except Exception as e:
        print(f"Error detecting language: {e}")
        return 'es'  # Default to Spanish

def generate_poetic_phrase(emotion, style):
    """
    Generate a poetic phrase based on user emotion and selected style.
    Maximum 20 words in the same language as the input.
    Returns a tuple: (phrase, language)
    """
    
    # Detect the language of the input
    language = detect_language(emotion)
    
    if language == 'en':
        # English prompts
        style_prompts = {
            "poetica_minimalista": "Create a minimalist and elegant poetic phrase",
            "indirecta_redes": "Create an indirect and subtle phrase, perfect for social media",
            "diario_intimo": "Create an intimate and personal phrase, like for a diary",
            "reflexiva": "Create a reflective and profound phrase"
        }
        
        prompt = f"""
        You are an expert poet skilled in expressing emotions delicately and elegantly.
        
        The user feels: "{emotion}"
        
        {style_prompts.get(style, "Create a poetic and elegant phrase")} that captures this emotion.
        
        Requirements:
        - Maximum 20 words
        - In English
        - Delicate and indirect
        - Poetic and emotional
        - Elegant and refined
        
        Respond ONLY with the phrase, without quotes or additional explanations.
        """
        
        system_message = "You are an expert poet who creates brief, elegant, and emotional phrases in English."
    else:
        # Spanish prompts (default)
        style_prompts = {
            "poetica_minimalista": "Crea una frase poética minimalista y elegante",
            "indirecta_redes": "Crea una frase indirecta y sutil, perfecta para redes sociales",
            "diario_intimo": "Crea una frase íntima y personal, como para un diario",
            "reflexiva": "Crea una frase reflexiva y profunda"
        }
        
        prompt = f"""
        Eres un poeta experto en expresar emociones de forma delicada y elegante.
        
        El usuario siente: "{emotion}"
        
        {style_prompts.get(style, "Crea una frase poética y elegante")} que capture esta emoción.
        
        Requisitos:
        - Máximo 20 palabras
        - En español
        - Delicada e indirecta
        - Poética y emotiva
        - Elegante y refinada
        
        Responde SOLO con la frase, sin comillas ni explicaciones adicionales.
        """
        
        system_message = "Eres un poeta experto que crea frases breves, elegantes y emotivas en español."
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            max_tokens=50,
            temperature=0.8
        )
        
        phrase = response.choices[0].message.content.strip()
        
        # Ensure the phrase doesn't exceed 20 words
        words = phrase.split()
        if len(words) > 20:
            phrase = ' '.join(words[:20])
        
        return phrase, language
    
    except Exception as e:
        print(f"Error generating phrase: {e}")
        # Return None instead of a generic phrase to indicate failure
        return None, None
