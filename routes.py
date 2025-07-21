from flask import render_template, request, redirect, url_for, flash, jsonify
from app import app, db
from models import Phrase
from openai_service import generate_poetic_phrase

@app.route('/')
def index():
    """Main page with emotion input and style selection"""
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_phrase():
    """Generate a poetic phrase from user emotion and style"""
    emotion = request.form.get('emotion', '').strip()
    style = request.form.get('style', 'poetica_minimalista')
    
    if not emotion:
        flash('Por favor, describe cómo te sientes.', 'error')
        return redirect(url_for('index'))
    
    if len(emotion) > 500:
        flash('La descripción es demasiado larga. Máximo 500 caracteres.', 'error')
        return redirect(url_for('index'))
    
    try:
        # Generate phrase using OpenAI
        generated_phrase = generate_poetic_phrase(emotion, style)
        
        # Check if phrase generation failed
        if generated_phrase is None:
            flash('No se pudo generar tu frase en este momento. Por favor, verifica tu clave de API de OpenAI o inténtalo más tarde. Es posible que hayas excedido tu cuota.', 'error')
            return redirect(url_for('index'))
        
        # Save to database
        phrase = Phrase(
            original_emotion=emotion,
            style=style,
            generated_phrase=generated_phrase
        )
        db.session.add(phrase)
        db.session.commit()
        
        return render_template('index.html', 
                             phrase=generated_phrase, 
                             phrase_id=phrase.id,
                             original_emotion=emotion,
                             style=style)
    
    except Exception as e:
        print(f"Error generating phrase: {e}")
        flash('Hubo un error al generar tu frase. Inténtalo de nuevo.', 'error')
        return redirect(url_for('index'))

@app.route('/favorite/<int:phrase_id>', methods=['POST'])
def toggle_favorite(phrase_id):
    """Toggle favorite status of a phrase"""
    phrase = Phrase.query.get_or_404(phrase_id)
    phrase.is_favorite = not phrase.is_favorite
    db.session.commit()
    
    return jsonify({'success': True, 'is_favorite': phrase.is_favorite})

@app.route('/collection')
def collection():
    """View all saved phrases"""
    phrases = Phrase.query.order_by(Phrase.created_at.desc()).all()
    return render_template('collection.html', phrases=phrases)

@app.route('/collection/favorites')
def favorites():
    """View favorite phrases only"""
    phrases = Phrase.query.filter_by(is_favorite=True).order_by(Phrase.created_at.desc()).all()
    return render_template('collection.html', phrases=phrases, show_favorites=True)

@app.route('/delete/<int:phrase_id>', methods=['POST'])
def delete_phrase(phrase_id):
    """Delete a phrase from collection"""
    phrase = Phrase.query.get_or_404(phrase_id)
    db.session.delete(phrase)
    db.session.commit()
    
    flash('Frase eliminada correctamente.', 'success')
    return redirect(url_for('collection'))

@app.route('/api/phrase/<int:phrase_id>')
def get_phrase_api(phrase_id):
    """API endpoint to get phrase data"""
    phrase = Phrase.query.get_or_404(phrase_id)
    return jsonify(phrase.to_dict())

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
