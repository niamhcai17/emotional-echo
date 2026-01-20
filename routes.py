from flask import render_template, request, redirect, url_for, flash, jsonify, session
from app import app, USE_SUPABASE
from services.openai_service import generate_poetic_phrase
from functools import wraps

# Importar servicios según configuración
if USE_SUPABASE:
    from services.supabase_service import supabase_service
    from config.supabase_config import get_supabase_client
    
    # Función para probar la conexión con Supabase
    def test_supabase_connection():
        """Prueba la conexión con Supabase y las tablas necesarias"""
        try:
            print("🔄 Probando conexión con Supabase...")
            supabase = get_supabase_client()
            
            # Probar tabla users
            response = supabase.table('users').select('*').limit(1).execute()
            print("✅ Conexión con tabla 'users' exitosa")
            
            # Probar tabla phrases
            response = supabase.table('phrases').select('*').limit(1).execute()
            print("✅ Conexión con tabla 'phrases' exitosa")
            
            return True
        except Exception as e:
            print(f"❌ Error de conexión con Supabase: {e}")
            return False
else:
    from app import db
    from models import Phrase

# Decorador para verificar autenticación
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if USE_SUPABASE:
            # Verificar autenticación en Supabase
            supabase = get_supabase_client()
            try:
                # Restaurar sesión si tenemos tokens guardados
                access_token = session.get('sb_access_token')
                refresh_token = session.get('sb_refresh_token')
                if access_token and refresh_token:
                    try:
                        if hasattr(supabase.auth, 'set_session'):
                            supabase.auth.set_session(access_token, refresh_token)
                        elif hasattr(supabase.auth, 'set_auth'):
                            supabase.auth.set_auth(access_token)
                    except Exception as e:
                        print(f"Error restaurando sesión: {e}")
                        # Si falla la restauración, limpiar tokens y redirigir
                        session.pop('sb_access_token', None)
                        session.pop('sb_refresh_token', None)
                        return redirect(url_for('landing'))

                user = supabase.auth.get_user()
                if not user or not user.user:
                    print("❌ Usuario no encontrado en el decorador")
                    # Si no hay usuario después de intentar restaurar la sesión, limpiar tokens
                    session.pop('sb_access_token', None)
                    session.pop('sb_refresh_token', None)
                    return redirect(url_for('landing'))
                
                print(f"✅ Usuario autenticado en decorador: {user.user.id}")
                return f(*args, **kwargs)
            except Exception as e:
                print(f"❌ Error en decorador login_required: {e}")
                return redirect(url_for('landing'))
        else:
            # Verificar nombre de usuario en cookies (modo legacy)
            user_name = request.cookies.get('user_name', '')
            if not user_name:
                return redirect(url_for('landing'))
            return f(*args, **kwargs)
    return decorated_function

@app.route('/')
@login_required
def index():
    """Main page with emotion input and style selection."""
    if USE_SUPABASE:
        # Obtener información del usuario autenticado
        supabase = get_supabase_client()
        try:
            user = supabase.auth.get_user()
            if user.user:
                # Obtener información del usuario desde la tabla users
                user_info = supabase_service.get_user_info(user.user.id)
                user_name = user_info.get('user_name', 'Usuario') if user_info else 'Usuario'
                return render_template('index.html', user_name=user_name, user_id=user.user.id)
        except Exception as e:
            print(f"❌ Error en la función index: {e}")
            return redirect(url_for('landing'))
    else:
        # Modo legacy con cookies
        user_name = request.cookies.get('user_name', '')
        if not user_name:
            return redirect(url_for('landing'))
        return render_template('index.html', user_name=user_name)

@app.route('/landing', methods=['GET', 'POST'])
def landing():
    """Landing page for user authentication"""
    if request.method == 'POST':
        # Esta ruta ya no maneja POST para nombres, solo GET para mostrar el login
        return redirect(url_for('landing'))
    
    # Verificar si ya está autenticado
    if USE_SUPABASE:
        supabase = get_supabase_client()
        try:
            user = supabase.auth.get_user()
            if user.user:
                return redirect(url_for('index'))
        except:
            pass
    
    return render_template('landing.html')

@app.route('/login', methods=['POST'])
def login():
    """Handle login form submission with email and password"""
    if not USE_SUPABASE:
        flash('Autenticación no disponible en modo local', 'error')
        return redirect(url_for('landing'))
    
    email = request.form.get('email', '').strip()
    password = request.form.get('password', '')
    
    if not email or not password:
        flash('Por favor, completa todos los campos.', 'error')
        return redirect(url_for('landing'))
    
    try:
        # Probar conexión con Supabase antes de proceder
        if not test_supabase_connection():
            flash('Error de conexión con la base de datos. Por favor, intenta más tarde.', 'error')
            return redirect(url_for('landing'))
        
        supabase = get_supabase_client()
        
        # Intentar iniciar sesión con email y contraseña
        response = supabase.auth.sign_in_with_password({
            'email': email,
            'password': password
        })

        print(f"Respuesta de login: {response}")
        print(f"Tipo de respuesta: {type(response)}")
        
        # Manejar la nueva estructura de respuesta de Supabase
        session_data = None
        if hasattr(response, 'data') and response.data:
            user = getattr(response.data, 'user', None)
            session_data = getattr(response.data, 'session', None)
        elif hasattr(response, 'user') or hasattr(response, 'session'):
            user = getattr(response, 'user', None)
            session_data = getattr(response, 'session', None)
        else:
            print(f"Estructura de respuesta inesperada: {response}")
            flash('Credenciales incorrectas. Por favor, verifica tu email y contraseña.', 'error')
            return redirect(url_for('landing'))

        # Guardar tokens en la sesión de Flask para futuras solicitudes
        if session_data:
            access_token = getattr(session_data, 'access_token', None)
            refresh_token = getattr(session_data, 'refresh_token', None)
            if access_token is None and isinstance(session_data, dict):
                access_token = session_data.get('access_token')
                refresh_token = session_data.get('refresh_token')
            if access_token:
                session['sb_access_token'] = access_token
            if refresh_token:
                session['sb_refresh_token'] = refresh_token
        
        if user and hasattr(user, 'id'):
            print(f"🔍 Usuario autenticado: {user.id}, email: {email}")
            
            # Verificar si el usuario existe en la tabla users
            user_info = supabase_service.get_user_info(user.id)
            print(f"🔍 Resultado get_user_info: {user_info}")
            
            if user_info:
                print("✅ Usuario encontrado en la base de datos")
                flash('¡Bienvenido! Has iniciado sesión correctamente.', 'success')
                return redirect(url_for('index'))
            else:
                print("⚠️ Usuario no encontrado, creando nuevo usuario...")
                # Usuario no existe en la tabla users, crear uno básico
                created_user = supabase_service.create_user(user.id, email, email.split('@')[0])
                print(f"🔍 Resultado create_user: {created_user}")
                
                if created_user:
                    print("✅ Usuario creado exitosamente")
                    flash('¡Bienvenido! Tu cuenta ha sido configurada.', 'success')
                else:
                    print("❌ Error creando usuario")
                    flash('Que pena! Has iniciado sesión correctamente.', 'success')
                
                return redirect(url_for('index'))
        else:
            flash('Credenciales incorrectas. Por favor, verifica tu email y contraseña.', 'error')
            return redirect(url_for('landing'))
            
    except Exception as e:
        print(f"Error en login: {e}")
        error_message = str(e).lower()
        
        if "invalid login credentials" in error_message:
            flash('Credenciales incorrectas. Por favor, verifica tu email y contraseña.', 'error')
        else:
            flash('Error al iniciar sesión. Por favor, inténtalo de nuevo.', 'error')
        return redirect(url_for('landing'))

@app.route('/register', methods=['POST'])
def register():
    """Handle user registration with username, email, and password"""
    if not USE_SUPABASE:
        flash('Registro no disponible en modo local', 'error')
        return redirect(url_for('landing'))
    
    username = request.form.get('username', '').strip()
    email = request.form.get('email', '').strip()
    password = request.form.get('password', '')
    
    if not username or not email or not password:
        flash('Por favor, completa todos los campos.', 'error')
        return redirect(url_for('landing'))
    
    if len(password) < 6:
        flash('La contraseña debe tener al menos 6 caracteres.', 'error')
        return redirect(url_for('landing'))
    
    try:
        supabase = get_supabase_client()
        
        # Crear nuevo usuario en Supabase Auth
        response = supabase.auth.sign_up({
            'email': email,
            'password': password,
            'options': {
                'data': {
                    'user_name': username
                }
            }
        })
        
        print(f"Respuesta de registro: {response}")
        print(f"Tipo de respuesta: {type(response)}")
        print(f"Atributos de respuesta: {dir(response)}")
        
        # Manejar la nueva estructura de respuesta de Supabase
        if hasattr(response, 'data') and response.data and hasattr(response.data, 'user'):
            user = response.data.user
        elif hasattr(response, 'user'):
            user = response.user
        else:
            print(f"Estructura de respuesta inesperada: {response}")
            flash('Error al crear la cuenta. Por favor, inténtalo de nuevo.', 'error')
            return redirect(url_for('landing'))
        
        if user:
            # Crear usuario en la tabla users
            user_created = supabase_service.create_user(user.id, email, username)
            
            if user_created:
                flash('¡Cuenta creada exitosamente! Por favor, verifica tu email para confirmar tu cuenta.', 'success')
            else:
                flash('Cuenta creada pero tienes que confirmar tu cuenta. Revisa tu correo electrónico.', 'warning')
            
            return redirect(url_for('landing'))
        else:
            flash('Error al crear la cuenta. Por favor, inténtalo de nuevo.', 'error')
            return redirect(url_for('landing'))
            
    except Exception as e:
        print(f"Error en registro: {e}")
        print(f"Tipo de error: {type(e)}")
        import traceback
        traceback.print_exc()
        
        error_message = str(e).lower()
        
        if "already registered" in error_message or "already exists" in error_message:
            flash('Este email ya está registrado. Por favor, inicia sesión.', 'error')
        elif "invalid email" in error_message:
            flash('Por favor, ingresa un email válido.', 'error')
        elif "password" in error_message:
            flash('La contraseña debe tener al menos 6 caracteres.', 'error')
        elif "database error" in error_message:
            flash('Error en la base de datos. Por favor, contacta soporte.', 'error')
        else:
            flash(f'Error al crear la cuenta: {str(e)}', 'error')
        return redirect(url_for('landing'))



@app.route('/logout')
def logout():
    """Cerrar sesión"""
    if USE_SUPABASE:
        try:
            supabase = get_supabase_client()
            try:
                supabase.auth.sign_out()
            except:
                pass
            # Limpiar tokens almacenados en la sesión
            session.pop('sb_access_token', None)
            session.pop('sb_refresh_token', None)
            flash('Has cerrado sesión correctamente.', 'info')
        except:
            pass
    else:
        # Modo legacy: limpiar cookie
        response = redirect(url_for('landing'))
        response.delete_cookie('user_name')
        flash('Has cerrado sesión correctamente.', 'info')
        return response
    
    return redirect(url_for('landing'))

@app.route('/generate', methods=['POST'])
@login_required
def generate_phrase():
    """Generate a poetic phrase from user emotion and style"""
    emotion = request.form.get('emotion', '').strip()
    style = request.form.get('style', 'poetica_minimalista')
    
    if not emotion:
        flash('What do you want to search today?', 'error')
        return redirect(url_for('index'))
    
    if len(emotion) > 500:
        flash('Description exceeds 500 characters.', 'error')
        return redirect(url_for('index'))
    
    try:
        # Generate phrase using OpenAI
        result = generate_poetic_phrase(emotion, style)
        
        # Check if phrase generation failed
        if result[0] is None:
            flash('Unable to generate your phrase right now. Try again later.', 'error')
            return redirect(url_for('index'))
        
        generated_phrase, language = result
        
        # Save to database
        if USE_SUPABASE:
            # Obtener user_id del usuario autenticado
            supabase = get_supabase_client()
            user = supabase.auth.get_user()
            user_id = user.user.id if user.user else None
            
            if not user_id:
                flash('Authentication failed. Please log in again.', 'error')
                return redirect(url_for('landing'))
            
            # Verificar límite de frases (Free Pass: 3 frases)
            phrase_count = supabase_service.get_phrase_count(user_id)
            if phrase_count >= 3:
                print(f"⚠️ Usuario {user_id} ha alcanzado el límite de frases ({phrase_count})")
                
                # Obtener nombre de usuario para mostrar en el template
                user_info = supabase_service.get_user_info(user_id)
                user_name = user_info.get('user_name', 'Usuario') if user_info else 'Usuario'

                return render_template('index.html', 
                                     user_name=user_name,
                                     limit_reached=True,
                                     original_emotion=emotion,
                                     style=style)
            
            phrase, error = supabase_service.create_phrase(
                user_id=user_id,
                original_emotion=emotion,
                style=style,
                phrase=generated_phrase,
                language=language
            )
            
            if error:
                print(f"❌ Error al guardar frase: {error}")
                error_str = str(error).lower()
                if "duplicate" in error_str or "unique constraint" in error_str:
                    flash('¡Vaya! Esta frase ya la tienes guardada en tu colección.', 'warning')
                    # Intentar buscar la frase existente para mostrarla si es posible, o simplemente redirigir
                    return redirect(url_for('index'))
                
                phrase_id = None
                flash(f'Error saving phrase: {error}', 'error')
                return redirect(url_for('index'))
                
            phrase_id = phrase['id'] if phrase else None
        else:
            # Modo legacy
            user_name = request.cookies.get('user_name', '').strip()
            if not user_name:
                flash('Name not found. Please re-enter your name.', 'error')
                return redirect(url_for('landing'))
            
            # Verificar límite de frases (Free Pass: 3 frases) - Modo Legacy
            phrase_count = Phrase.query.filter_by(user_name=user_name).count()
            if phrase_count >= 3:
                print(f"⚠️ Usuario Legacy {user_name} ha alcanzado el límite de frases ({phrase_count})")
                return render_template('index.html', 
                                     user_name=user_name, 
                                     limit_reached=True,
                                     original_emotion=emotion,
                                     style=style)
            
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
            # Obtener nombre de usuario actualizado
            user_name = 'Usuario'
            if USE_SUPABASE:
                user_info = supabase_service.get_user_info(user_id)
                user_name = user_info.get('user_name', 'Usuario') if user_info else 'Usuario'
            else:
                user_name = request.cookies.get('user_name', 'Usuario')

            return render_template('index.html', 
                                user_name=user_name,
                                generated_phrase=generated_phrase,
                                original_emotion=emotion,
                                style=style,
                                phrase_id=phrase_id)
        else:
            flash('Failed to save your phrase. Try again.', 'error')
            return redirect(url_for('index'))
            
    except Exception as e:
        print(f"Error generando frase: {e}")
        flash('Something unexpected happened. Please try again later.', 'error')
        return redirect(url_for('index'))

@app.route('/favorite/<phrase_id>', methods=['POST'])
@login_required
def toggle_favorite(phrase_id):
    """Toggle favorite status of a phrase"""
    try:
        supabase = get_supabase_client()
        user = supabase.auth.get_user()
        user_id = user.user.id if user.user else None

        if not user_id:
            return jsonify({'success': False, 'error': 'No autorizado'})
        
        if USE_SUPABASE:
            # Verificar que la frase pertenece al usuario
            phrase = supabase_service.get_phrase_by_id(phrase_id)
            if phrase and phrase.get('user_id') == user_id:
                is_favorite = supabase_service.toggle_favorite(phrase_id)
            else:
                return jsonify({'success': False, 'error': 'No autorizado'})
        else:
            phrase = Phrase.query.get_or_404(phrase_id)
            # Verificar que la frase pertenece al usuario
            if phrase.user_name == request.cookies.get('user_name', ''): # Assuming user_name is the key for legacy
                phrase.is_favorite = not phrase.is_favorite
                db.session.commit()
                is_favorite = phrase.is_favorite
            else:
                return jsonify({'success': False, 'error': 'No autorizado'})
        
        return jsonify({'success': True, 'is_favorite': is_favorite})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/collection')
@login_required
def collection():
    """View all saved phrases"""
    try:
        supabase = get_supabase_client()
        user = supabase.auth.get_user()
        user_id = user.user.id if user.user else None
        
        if not user_id:
            flash('Authentication failed. Please log in again.', 'error')
            return redirect(url_for('landing'))
        
        if USE_SUPABASE:
            phrases = supabase_service.get_all_phrases(user_id=user_id)
        else:
            if user_id:
                phrases = Phrase.query.filter_by(user_name=request.cookies.get('user_name', '')).order_by(Phrase.created_at.desc()).all() # Assuming user_name is the key for legacy
            else:
                phrases = Phrase.query.order_by(Phrase.created_at.desc()).all()
        
        # Obtener nombre de usuario
        user_name = 'Usuario'
        if USE_SUPABASE:
            user_info = supabase_service.get_user_info(user_id)
            user_name = user_info.get('user_name', 'Usuario') if user_info else 'Usuario'
        else:
            user_name = request.cookies.get('user_name', 'Usuario')
            
        return render_template('collection.html', phrases=phrases, user_name=user_name)
    except Exception as e:
        flash('Error al cargar la colección.', 'error')
        return redirect(url_for('index'))

@app.route('/collection/favorites')
@login_required
def favorites():
    """View favorite phrases only"""
    try:
        supabase = get_supabase_client()
        user = supabase.auth.get_user()
        user_id = user.user.id if user.user else None
        
        if not user_id:
            flash('Authentication failed. Please log in again.', 'error')
            return redirect(url_for('landing'))
        
        if USE_SUPABASE:
            phrases = supabase_service.get_favorite_phrases(user_id=user_id)
        else:
            if user_id:
                phrases = Phrase.query.filter_by(user_name=request.cookies.get('user_name', '')).order_by(Phrase.created_at.desc()).all() # Assuming user_name is the key for legacy
            else:
                phrases = Phrase.query.filter_by(is_favorite=True).order_by(Phrase.created_at.desc()).all()
        
        # Obtener nombre de usuario
        user_name = 'Usuario'
        if USE_SUPABASE:
            user_info = supabase_service.get_user_info(user_id)
            user_name = user_info.get('user_name', 'Usuario') if user_info else 'Usuario'
        else:
            user_name = request.cookies.get('user_name', 'Usuario')

        return render_template('collection.html', phrases=phrases, show_favorites=True, user_name=user_name)
    except Exception as e:
        flash('Error al cargar los favoritos.', 'error')
        return redirect(url_for('index'))

@app.route('/collection/language/<language>')
@login_required
def collection_by_language(language):
    """View phrases filtered by language"""
    try:
        if language not in ['es', 'en']:
            flash('Idioma no válido.', 'error')
            return redirect(url_for('collection'))
        
        supabase = get_supabase_client()
        user = supabase.auth.get_user()
        user_id = user.user.id if user.user else None
        
        if not user_id:
            flash('Authentication failed. Please log in again.', 'error')
            return redirect(url_for('landing'))
        
        if USE_SUPABASE:
            phrases = supabase_service.get_phrases_by_language(language, user_id=user_id)
        else:
            if user_id:
                phrases = Phrase.query.filter_by(user_name=request.cookies.get('user_name', '')).order_by(Phrase.created_at.desc()).all() # Assuming user_name is the key for legacy
            else:
                phrases = Phrase.query.filter_by(language=language).order_by(Phrase.created_at.desc()).all()
        
        # Obtener nombre de usuario
        user_name = 'Usuario'
        if USE_SUPABASE:
            user_info = supabase_service.get_user_info(user_id)
            user_name = user_info.get('user_name', 'Usuario') if user_info else 'Usuario'
        else:
            user_name = request.cookies.get('user_name', 'Usuario')

        language_name = 'Español' if language == 'es' else 'English'
        return render_template('collection.html', phrases=phrases, language_filter=language, language_name=language_name, user_name=user_name)
    except Exception as e:
        flash('Error al cargar las frases por idioma.', 'error')
        return redirect(url_for('collection'))

@app.route('/stats')
@login_required
def stats():
    """View database statistics"""
    try:
        supabase = get_supabase_client()
        user = supabase.auth.get_user()
        user_id = user.user.id if user.user else None
        
        if not user_id:
            flash('Authentication failed. Please log in again.', 'error')
            return redirect(url_for('landing'))
        
        if USE_SUPABASE:
            stats_data = supabase_service.get_stats(user_id=user_id)
        else:
            # Calcular estadísticas para SQLite
            if user_id:
                total_phrases = Phrase.query.filter_by(user_name=request.cookies.get('user_name', '')).count() # Assuming user_name is the key for legacy
                favorite_phrases = Phrase.query.filter_by(user_name=request.cookies.get('user_name', '')).count() # Assuming user_name is the key for legacy
                phrases = Phrase.query.filter_by(user_name=request.cookies.get('user_name', '')).all() # Assuming user_name is the key for legacy
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
                'user_name': request.cookies.get('user_name', 'Usuario')
            }
        
        # Añadir user_name a stats_data para Supabase también si no está
        if USE_SUPABASE and 'user_name' not in stats_data:
            user_info = supabase_service.get_user_info(user_id)
            stats_data['user_name'] = user_info.get('user_name', 'Usuario') if user_info else 'Usuario'
        
        return render_template('stats.html', stats=stats_data, user_name=stats_data.get('user_name'))
    except Exception as e:
        flash('Error al cargar las estadísticas.', 'error')
        return redirect(url_for('index'))

@app.route('/delete/<phrase_id>', methods=['POST'])
@login_required
def delete_phrase(phrase_id):
    """Delete a phrase from collection"""
    try:
        supabase = get_supabase_client()
        user = supabase.auth.get_user()
        user_id = user.user.id if user.user else None
        
        if not user_id:
            flash('Authentication failed. Please log in again.', 'error')
            return redirect(url_for('landing'))
        
        if USE_SUPABASE:
            # Verificar que la frase pertenece al usuario
            phrase = supabase_service.get_phrase_by_id(phrase_id)
            if phrase and phrase.get('user_id') == user_id:
                success = supabase_service.delete_phrase(phrase_id)
            else:
                flash('No tienes permisos para eliminar esta frase.', 'error')
                return redirect(url_for('collection'))
        else:
            phrase = Phrase.query.get_or_404(phrase_id)
            # Verificar que la frase pertenece al usuario
            if phrase.user_name == request.cookies.get('user_name', ''): # Assuming user_name is the key for legacy
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

@app.route('/api/phrase/<phrase_id>')
@login_required
def get_phrase_api(phrase_id):
    """API endpoint to get phrase data"""
    try:
        supabase = get_supabase_client()
        user = supabase.auth.get_user()
        user_id = user.user.id if user.user else None
        
        if not user_id:
            return jsonify({'error': 'No autorizado'}), 401
        
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
        from services.openai_service import client
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
