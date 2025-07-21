import os
import json
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

# The newest OpenAI model is "gpt-4o" which was released May 13, 2024.
# Do not change this unless explicitly requested by the user
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

def generate_poetic_phrase(emotion, style):
    """
    Generate a poetic phrase based on user emotion and selected style.
    Maximum 20 words in Spanish.
    """
    
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
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Eres un poeta experto que crea frases breves, elegantes y emotivas en español."},
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
        
        return phrase
    
    except Exception as e:
        print(f"Error generating phrase: {e}")
        # Return None instead of a generic phrase to indicate failure
        return None
