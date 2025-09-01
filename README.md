# 🌟 Entrelíneas - Transforma tus emociones en frases poéticas

Una aplicación web que utiliza inteligencia artificial para transformar tus emociones en hermosas frases poéticas, con autenticación segura y base de datos en la nube.

## ✨ Características

- 🎭 **Generación de frases poéticas** usando OpenAI GPT
- 🔐 **Autenticación segura** con Google OAuth
- ☁️ **Base de datos en la nube** con Supabase
- 🌍 **Soporte multilingüe** (Español e Inglés)
- 💾 **Guardado automático** de frases generadas
- ❤️ **Sistema de favoritos** para tus frases preferidas
- 📊 **Estadísticas personales** de uso
- 📱 **Diseño responsive** y moderno

## 🏗️ Estructura del Proyecto

```
EmotionalEcho/
├── 📁 config/                 # Configuraciones
│   └── supabase_config.py     # Configuración de Supabase
├── 📁 services/               # Servicios de la aplicación
│   ├── supabase_service.py    # Servicio de base de datos
│   └── openai_service.py      # Servicio de OpenAI
├── 📁 templates/              # Plantillas HTML
│   ├── base.html              # Template base
│   ├── index.html             # Página principal
│   ├── landing.html           # Página de login
│   ├── collection.html        # Colección de frases
│   └── stats.html             # Estadísticas
├── 📁 static/                 # Archivos estáticos
│   ├── css/                   # Estilos CSS
│   └── js/                    # JavaScript
├── 📁 docs/                   # Documentación
├── 📁 sandbox/                # Archivos de prueba
├── app.py                     # Aplicación principal Flask
├── main.py                    # Punto de entrada
├── routes.py                  # Rutas de la aplicación
├── database.py                # Helpers de base de datos
├── models.py                  # Modelos de datos
├── requirements.txt           # Dependencias Python
└── pyproject.toml            # Configuración del proyecto
```

## 🚀 Instalación y Configuración

### 1. Prerrequisitos

- Python 3.8 o superior
- Cuenta en [Supabase](https://supabase.com)
- Cuenta en [OpenAI](https://openai.com)
- Cuenta en [Google Cloud Console](https://console.cloud.google.com)

### 2. Clonar el repositorio

```bash
git clone <tu-repositorio>
cd EmotionalEcho
```

### 3. Crear entorno virtual

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 4. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 5. Configurar variables de entorno

Crea un archivo `.env` en la raíz del proyecto:

```bash
# Configuración de Supabase
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_KEY=tu-service-role-key
SUPABASE_ANON_KEY=tu-anon-key

# Configuración de OpenAI
OPENAI_API_KEY=tu-openai-api-key

# Configuración de sesión
SESSION_SECRET=tu-secret-key-cambiar-en-produccion
```

### 6. Configurar Supabase

#### 6.1 Habilitar Google Auth
1. Ve a tu dashboard de Supabase
2. Navega a **Authentication** → **Providers**
3. Habilita **Google**
4. Configura tu **Client ID** y **Client Secret** de Google OAuth

#### 6.2 Crear tablas en la base de datos
Ejecuta este script en el **SQL Editor** de Supabase:

```sql
-- Crear tabla de usuarios
CREATE TABLE users (
  id UUID REFERENCES auth.users(id) ON DELETE CASCADE PRIMARY KEY,
  email TEXT UNIQUE NOT NULL,
  full_name TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Crear tabla de frases
CREATE TABLE phrases (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE NOT NULL,
  original_emotion TEXT NOT NULL,
  style TEXT NOT NULL,
  generated_phrase TEXT NOT NULL,
  language TEXT DEFAULT 'es',
  is_favorite BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Crear índices
CREATE INDEX idx_phrases_user_id ON phrases(user_id);
CREATE INDEX idx_phrases_created_at ON phrases(created_at);

-- Habilitar RLS
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE phrases ENABLE ROW LEVEL SECURITY;

-- Políticas de seguridad
CREATE POLICY "Users can view own profile" ON users FOR SELECT USING (auth.uid() = id);
CREATE POLICY "Users can update own profile" ON users FOR UPDATE USING (auth.uid() = id);
CREATE POLICY "Users can view own phrases" ON phrases FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own phrases" ON phrases FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own phrases" ON phrases FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own phrases" ON phrases FOR DELETE USING (auth.uid() = user_id);

-- Función para crear usuario automáticamente
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.users (id, email, full_name)
  VALUES (NEW.id, NEW.email, COALESCE(NEW.raw_user_meta_data->>'full_name', NEW.email));
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger para crear usuario automáticamente
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();
```

### 7. Configurar Google OAuth

1. Ve a [Google Cloud Console](https://console.cloud.google.com)
2. Crea un nuevo proyecto o selecciona uno existente
3. Habilita la **Google+ API**
4. Ve a **Credentials** → **Create Credentials** → **OAuth 2.0 Client IDs**
5. Configura las URLs de redirección:
   - `https://tu-proyecto.supabase.co/auth/v1/callback`
   - `http://localhost:5000/auth/callback` (para desarrollo)

## 🏃‍♂️ Ejecutar la Aplicación

### Desarrollo local

```bash
# Activar entorno virtual
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# Ejecutar la aplicación
python main.py
```

La aplicación estará disponible en: `http://localhost:5000`

### Producción

```bash
# Usar gunicorn para producción
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 main:app
```

## 🔧 Uso de la Aplicación

### 1. **Acceso inicial**
- Ve a `http://localhost:5000`
- Serás redirigido a la página de login
- Haz clic en "Continuar con Google"

### 2. **Generar frases**
- Una vez autenticado, describe cómo te sientes
- Selecciona un estilo poético
- Haz clic en "Generar Frase"
- La IA creará una frase poética personalizada

### 3. **Gestionar frases**
- **Mi Colección**: Ver todas tus frases generadas
- **Favoritos**: Marcar y ver tus frases preferidas
- **Estadísticas**: Analizar tu uso y preferencias

## 🛠️ Desarrollo

### Estructura de archivos principales

- **`app.py`**: Configuración principal de Flask y Supabase
- **`routes.py`**: Todas las rutas y lógica de la aplicación
- **`services/`**: Servicios para OpenAI y Supabase
- **`models.py`**: Modelos de datos y constantes
- **`database.py`**: Helpers para operaciones de base de datos

### Agregar nuevas funcionalidades

1. **Nuevas rutas**: Agregar en `routes.py`
2. **Nuevos servicios**: Crear en carpeta `services/`
3. **Nuevos modelos**: Definir en `models.py`
4. **Nuevas plantillas**: Crear en `templates/`

### Testing

```bash
# Ejecutar tests (si existen)
python -m pytest

# Verificar sintaxis
python -m py_compile *.py
```

## 🐛 Solución de Problemas

### Error de conexión a Supabase
- Verifica que `SUPABASE_URL` y `SUPABASE_KEY` estén correctos
- Confirma que la conexión a internet esté funcionando

### Error de autenticación con Google
- Verifica que Google Auth esté habilitado en Supabase
- Confirma que las credenciales de Google sean correctas
- Verifica las URLs de redirección

### Error de OpenAI
- Confirma que `OPENAI_API_KEY` sea válida
- Verifica que tengas créditos disponibles en tu cuenta

### Problemas de base de datos
- Ejecuta el script SQL completo en Supabase
- Verifica que las tablas se hayan creado correctamente
- Confirma que RLS esté habilitado

## 📚 Dependencias Principales

- **Flask**: Framework web
- **Supabase**: Base de datos y autenticación
- **OpenAI**: Generación de frases con IA
- **Bootstrap**: Framework CSS para el frontend
- **Font Awesome**: Iconos

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 📞 Soporte

Si encuentras problemas:

1. Revisa los logs de la aplicación
2. Verifica la configuración en Supabase Dashboard
3. Confirma que todas las variables de entorno estén configuradas
4. Abre un issue en el repositorio

## 🎯 Roadmap

- [ ] Soporte para más idiomas
- [ ] Temas personalizables
- [ ] API REST pública
- [ ] Aplicación móvil
- [ ] Integración con redes sociales
- [ ] Sistema de colaboración entre usuarios

---

**¡Disfruta creando hermosas frases poéticas con Entrelíneas!** ✨
