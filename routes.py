from flask import render_template, request, redirect, url_for, flash, jsonify
from app import app, USE_SUPABASE
from openai_service import generate_poetic_phrase

# Importar servicios según configuración
if USE_SUPABASE:
    from supabase_service import supabase_service
else:
    from app import db
    from models import Phrase

@app.route('/')
def index():
    """Main page with emotion input and style selection."""
    # Verificar si el usuario tiene un nombre guardado
    user_name = request.cookies.get('user_name', '')
    
    if not user_name:
        # Si no tiene nombre, redirigir al landing
        return redirect(url_for('landing'))
    
    return render_template('index.html', user_name=user_name)

@app.route('/landing', methods=['GET', 'POST'])
def landing():
    """Landing page for user registration"""
    if request.method == 'POST':
        user_name = request.form.get('user_name', '').strip()
        
        if not user_name:
            flash('Por favor, ingresa tu nombre.', 'error')
            return render_template('landing.html')
        
        if len(user_name) > 30:
            flash('El nombre es demasiado largo. Máximo 30 caracteres.', 'error')
            return render_template('landing.html')
        
        # Crear respuesta con cookie
        response = redirect(url_for('index'))
        response.set_cookie('user_name', user_name, max_age=365*24*60*60)  # 1 año
        
        flash(f'¡Bienvenido, {user_name}! Ya puedes comenzar a crear frases poéticas.', 'success')
        return response
    
    return render_template('landing.html')

@app.route('/generate', methods=['POST'])
def generate_phrase():
    """Generate a poetic phrase from user emotion and style"""
    emotion = request.form.get('emotion', '').strip()
    style = request.form.get('style', 'poetica_minimalista')
    user_name = request.cookies.get('user_name', '').strip()  # Obtener de cookies
    
    if not emotion:
        flash('Por favor, describe cómo te sientes.', 'error')
        return redirect(url_for('index'))
    
    if not user_name:
        flash('No se encontró tu nombre. Por favor, vuelve a ingresar tu nombre.', 'error')
        return redirect(url_for('landing'))
    
    if len(emotion) > 500:
        flash('La descripción es demasiado larga. Máximo 500 caracteres.', 'error')
        return redirect(url_for('index'))
    
    try:
        # Generate phrase using OpenAI
        result = generate_poetic_phrase(emotion, style)
        
        # Check if phrase generation failed
        if result[0] is None:
            flash('No se pudo generar tu frase en este momento. Por favor, verifica tu clave de API de OpenAI o inténtalo más tarde. Es posible que hayas excedido tu cuota.', 'error')
            return redirect(url_for('index'))
        
        generated_phrase, language = result
        
        # Save to database
        if USE_SUPABASE:
            phrase = supabase_service.create_phrase(
                original_emotion=emotion,
                style=style,
                generated_phrase=generated_phrase,
                language=language,
                user_name=user_name
            )
            phrase_id = phrase['id'] if phrase else None
        else:
            phrase = Phrase(
                user_name=user_name,
                original_emotion=emotion,
                style=style,
                generated_phrase=generated_phrase,
                language=language
            )
            db.session.add(phrase)
            db.session.commit()
            phrase_id = phrase.id
        
        if phrase_id:
            return render_template('index.html', 
                                 phrase=generated_phrase, 
                                 phrase_id=phrase_id,
                                 original_emotion=emotion,
                                 style=style,
                                 user_name=user_name)
        else:
            flash('Error al guardar la frase en la base de datos.', 'error')
            return redirect(url_for('index'))
    
    except Exception as e:
        print(f"Error generating phrase: {e}")
        flash('Hubo un error al generar tu frase. Inténtalo de nuevo.', 'error')
        return redirect(url_for('index'))

@app.route('/favorite/<int:phrase_id>', methods=['POST'])
def toggle_favorite(phrase_id):
    """Toggle favorite status of a phrase"""
    try:
        user_name = request.cookies.get('user_name', '')
        
        if USE_SUPABASE:
            # Verificar que la frase pertenece al usuario
            phrase = supabase_service.get_phrase_by_id(phrase_id)
            if phrase and phrase.get('user_name') == user_name:
                is_favorite = supabase_service.toggle_favorite(phrase_id)
            else:
                return jsonify({'success': False, 'error': 'No autorizado'})
        else:
            phrase = Phrase.query.get_or_404(phrase_id)
            # Verificar que la frase pertenece al usuario
            if phrase.user_name == user_name:
                phrase.is_favorite = not phrase.is_favorite
                db.session.commit()
                is_favorite = phrase.is_favorite
            else:
                return jsonify({'success': False, 'error': 'No autorizado'})
        
        return jsonify({'success': True, 'is_favorite': is_favorite})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/collection')
def collection():
    """View all saved phrases"""
    try:
        user_name = request.cookies.get('user_name', '')
        
        if USE_SUPABASE:
            phrases = supabase_service.get_all_phrases(user_name=user_name)
        else:
            if user_name:
                phrases = Phrase.query.filter_by(user_name=user_name).order_by(Phrase.created_at.desc()).all()
            else:
                phrases = Phrase.query.order_by(Phrase.created_at.desc()).all()
        
        return render_template('collection.html', phrases=phrases, user_name=user_name)
    except Exception as e:
        flash('Error al cargar la colección.', 'error')
        return redirect(url_for('index'))

@app.route('/collection/favorites')
def favorites():
    """View favorite phrases only"""
    try:
        user_name = request.cookies.get('user_name', '')
        
        if USE_SUPABASE:
            phrases = supabase_service.get_favorite_phrases(user_name=user_name)
        else:
            if user_name:
                phrases = Phrase.query.filter_by(user_name=user_name, is_favorite=True).order_by(Phrase.created_at.desc()).all()
            else:
                phrases = Phrase.query.filter_by(is_favorite=True).order_by(Phrase.created_at.desc()).all()
        
        return render_template('collection.html', phrases=phrases, show_favorites=True, user_name=user_name)
    except Exception as e:
        flash('Error al cargar los favoritos.', 'error')
        return redirect(url_for('index'))

@app.route('/collection/language/<language>')
def collection_by_language(language):
    """View phrases filtered by language"""
    try:
        if language not in ['es', 'en']:
            flash('Idioma no válido.', 'error')
            return redirect(url_for('collection'))
        
        user_name = request.cookies.get('user_name', '')
        
        if USE_SUPABASE:
            phrases = supabase_service.get_phrases_by_language(language, user_name=user_name)
        else:
            if user_name:
                phrases = Phrase.query.filter_by(user_name=user_name, language=language).order_by(Phrase.created_at.desc()).all()
            else:
                phrases = Phrase.query.filter_by(language=language).order_by(Phrase.created_at.desc()).all()
        
        language_name = 'Español' if language == 'es' else 'English'
        return render_template('collection.html', phrases=phrases, language_filter=language, language_name=language_name, user_name=user_name)
    except Exception as e:
        flash('Error al cargar las frases por idioma.', 'error')
        return redirect(url_for('collection'))

@app.route('/stats')
def stats():
    """View database statistics"""
    try:
        user_name = request.cookies.get('user_name', '')
        
        if USE_SUPABASE:
            stats_data = supabase_service.get_stats(user_name=user_name)
        else:
            # Calcular estadísticas para SQLite
            if user_name:
                total_phrases = Phrase.query.filter_by(user_name=user_name).count()
                favorite_phrases = Phrase.query.filter_by(user_name=user_name, is_favorite=True).count()
                phrases = Phrase.query.filter_by(user_name=user_name).all()
            else:
                total_phrases = Phrase.query.count()
                favorite_phrases = Phrase.query.filter_by(is_favorite=True).count()
                phrases = Phrase.query.all()
            
            # Distribución por idioma
            language_stats = {}
            for phrase in phrases:
                lang = phrase.language or 'es'
                language_stats[lang] = language_stats.get(lang, 0) + 1
            
            stats_data = {
                'total_phrases': total_phrases,
                'favorite_phrases': favorite_phrases,
                'language_stats': language_stats,
                'user_name': user_name
            }
        
        return render_template('stats.html', stats=stats_data)
    except Exception as e:
        flash('Error al cargar las estadísticas.', 'error')
        return redirect(url_for('index'))

@app.route('/delete/<int:phrase_id>', methods=['POST'])
def delete_phrase(phrase_id):
    """Delete a phrase from collection"""
    try:
        user_name = request.cookies.get('user_name', '')
        
        if USE_SUPABASE:
            # Verificar que la frase pertenece al usuario
            phrase = supabase_service.get_phrase_by_id(phrase_id)
            if phrase and phrase.get('user_name') == user_name:
                success = supabase_service.delete_phrase(phrase_id)
            else:
                flash('No tienes permisos para eliminar esta frase.', 'error')
                return redirect(url_for('collection'))
        else:
            phrase = Phrase.query.get_or_404(phrase_id)
            # Verificar que la frase pertenece al usuario
            if phrase.user_name == user_name:
                db.session.delete(phrase)
                db.session.commit()
                success = True
            else:
                flash('No tienes permisos para eliminar esta frase.', 'error')
                return redirect(url_for('collection'))
        
        if success:
            flash('Frase eliminada correctamente.', 'success')
        else:
            flash('Error al eliminar la frase.', 'error')
        
        return redirect(url_for('collection'))
    except Exception as e:
        flash('Error al eliminar la frase.', 'error')
        return redirect(url_for('collection'))

@app.route('/api/phrase/<int:phrase_id>')
def get_phrase_api(phrase_id):
    """API endpoint to get phrase data"""
    try:
        if USE_SUPABASE:
            phrase = supabase_service.get_phrase_by_id(phrase_id)
        else:
            phrase = Phrase.query.get_or_404(phrase_id)
            phrase = phrase.to_dict()
        
        return jsonify(phrase)
    except Exception as e:
        return jsonify({'error': str(e)}), 404

@app.route('/test-api')
def test_api():
    """Test OpenAI API status"""
    try:
        from openai_service import client
        # Simple test with minimal tokens
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": "Hola"}],
            max_tokens=5
        )
        return jsonify({
            'status': 'success',
            'message': 'API funcionando correctamente',
            'response': response.choices[0].message.content
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        })
