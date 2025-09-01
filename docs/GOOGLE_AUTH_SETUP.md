# Configuración de Autenticación con Google en Supabase

## 🚀 Resumen de Cambios

Hemos actualizado tu aplicación **Entrelíneas** para usar autenticación con Google en lugar de nombres de usuario simples. Esto proporciona:

- ✅ Autenticación segura con Google
- ✅ Base de datos asociada a IDs únicos de usuario
- ✅ Sin duplicación de nombres
- ✅ Separación completa de datos entre usuarios
- ✅ Sistema de autenticación robusto

## 📋 Script SQL para Supabase

Ejecuta este script en el **SQL Editor** de tu dashboard de Supabase:

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

-- Crear índices para mejor rendimiento
CREATE INDEX idx_phrases_user_id ON phrases(user_id);
CREATE INDEX idx_phrases_created_at ON phrases(created_at);

-- Habilitar RLS (Row Level Security)
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE phrases ENABLE ROW LEVEL SECURITY;

-- Políticas para users
CREATE POLICY "Users can view own profile" ON users
  FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON users
  FOR UPDATE USING (auth.uid() = id);

-- Políticas para phrases
CREATE POLICY "Users can view own phrases" ON phrases
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own phrases" ON phrases
  FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own phrases" ON phrases
  FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own phrases" ON phrases
  FOR DELETE USING (auth.uid() = user_id);

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

## 🔧 Configuración en Supabase Dashboard

### 1. Habilitar Google Auth

1. Ve a **Authentication** → **Providers**
2. Habilita **Google**
3. Configura tu **Client ID** y **Client Secret** de Google OAuth
4. Agrega tu dominio a los **Redirect URLs**

### 2. Obtener Credenciales de Google

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un nuevo proyecto o selecciona uno existente
3. Habilita la **Google+ API**
4. Ve a **Credentials** → **Create Credentials** → **OAuth 2.0 Client IDs**
5. Configura las URLs de redirección:
   - `https://tu-proyecto.supabase.co/auth/v1/callback`
   - `http://localhost:5000/auth/callback` (para desarrollo)

## 🌍 Variables de Entorno

Crea un archivo `.env` en tu proyecto con estas variables:

```bash
# Configuración de Supabase
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_KEY=tu-service-role-key-aqui
SUPABASE_ANON_KEY=tu-anon-key-aqui

# Configuración de OpenAI
OPENAI_API_KEY=tu-openai-api-key-aqui

# Configuración de sesión
SESSION_SECRET=tu-secret-key-aqui-cambiar-en-produccion

# Configuración de Google OAuth (para el frontend)
GOOGLE_CLIENT_ID=tu-google-client-id-aqui
```

## 🚀 Ejecutar Migración

Si prefieres usar el script de migración automática:

```bash
python migrate_to_auth.py
```

## 📱 Cambios en la Aplicación

### Landing Page
- ✅ Reemplazado formulario de nombre por botón de login con Google
- ✅ Integración con Supabase Auth
- ✅ Redirección automática si ya está autenticado

### Autenticación
- ✅ Decorador `@login_required` para proteger rutas
- ✅ Verificación automática de autenticación
- ✅ Manejo de sesiones con Supabase
- ✅ Ruta de callback para OAuth

### Base de Datos
- ✅ Nueva estructura con `user_id` en lugar de `user_name`
- ✅ Tabla `users` vinculada a `auth.users`
- ✅ Tabla `phrases` con referencia a usuario
- ✅ Row Level Security (RLS) habilitado

### Servicios
- ✅ `SupabaseService` actualizado para usar `user_id`
- ✅ Métodos para obtener información del usuario
- ✅ Filtrado automático por usuario autenticado

## 🔒 Seguridad

- **Row Level Security (RLS)**: Cada usuario solo ve sus propios datos
- **Políticas de acceso**: Control granular sobre operaciones CRUD
- **Autenticación JWT**: Tokens seguros de Supabase
- **Validación de usuario**: Verificación en cada operación

## 🧪 Pruebas

1. **Ejecuta la migración** en Supabase
2. **Configura Google OAuth** en el dashboard
3. **Actualiza las variables de entorno**
4. **Reinicia la aplicación**
5. **Prueba el login** con una cuenta de Google

## 🐛 Solución de Problemas

### Error: "No se pudo conectar a Supabase"
- Verifica que `SUPABASE_URL` y `SUPABASE_KEY` estén correctos
- Asegúrate de que la conexión a internet esté funcionando

### Error: "Google OAuth no configurado"
- Verifica que Google Auth esté habilitado en Supabase
- Confirma que las credenciales de Google sean correctas

### Error: "Tabla no encontrada"
- Ejecuta el script SQL completo en Supabase
- Verifica que las tablas se hayan creado correctamente

### Error: "Políticas de seguridad no funcionan"
- Asegúrate de que RLS esté habilitado
- Verifica que las políticas se hayan creado correctamente

## 📞 Soporte

Si encuentras problemas:

1. Revisa los logs de la aplicación
2. Verifica la configuración en Supabase Dashboard
3. Confirma que todas las variables de entorno estén configuradas
4. Ejecuta el script de migración nuevamente

## 🎯 Beneficios de la Nueva Implementación

- **Seguridad**: Autenticación robusta con Google
- **Escalabilidad**: Base de datos preparada para múltiples usuarios
- **Mantenibilidad**: Código más limpio y organizado
- **Experiencia de usuario**: Login simple y rápido
- **Datos únicos**: Sin duplicación de información de usuario
