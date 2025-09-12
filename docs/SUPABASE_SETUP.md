# 🚀 Configuración de Supabase - EmotionalEcho

## 📋 ¿Qué es Supabase?

Supabase es una alternativa open-source a Firebase que proporciona:
- **Base de datos PostgreSQL** en la nube
- **API REST automática**
- **Autenticación** (opcional)
- **Tiempo real** (opcional)
- **Plan gratuito** generoso

## 🎯 Ventajas para tu proyecto

1. **Persistencia:** Los datos se mantienen entre despliegues
2. **Gratuito:** 500MB de base de datos, 50,000 filas/mes
3. **Simple:** API REST automática
4. **Escalable:** Crece con tu aplicación

## 📝 Pasos para configurar Supabase

### **Paso 1: Crear cuenta en Supabase**

1. Ve a [supabase.com](https://supabase.com)
2. Haz clic en "Start your project"
3. Conecta con GitHub o crea cuenta
4. Haz clic en "New Project"

### **Paso 2: Crear proyecto**

1. **Nombre del proyecto:** `emotionalecho` (o el que prefieras)
2. **Contraseña de base de datos:** Genera una contraseña segura
3. **Región:** Elige la más cercana a ti
4. Haz clic en "Create new project"

### **Paso 3: Obtener credenciales**

Una vez creado el proyecto:

1. Ve a **Settings** → **API**
2. Copia:
   - **Project URL** (SUPABASE_URL)
   - **anon public** key (SUPABASE_KEY)

### **Paso 4: Crear tablas, políticas y trigger en Supabase**

Ejecuta el siguiente SQL en el editor de SQL de Supabase para crear las tablas `users` y `phrases`, habilitar RLS con políticas seguras y sincronizar automáticamente `auth.users → public.users`:

```sql
-- ======================================
-- 🚀 Script limpio para Supabase
-- ======================================

-- Crear tabla de usuarios
CREATE TABLE IF NOT EXISTS users (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  email TEXT UNIQUE NOT NULL,
  user_name TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Crear tabla de frases
CREATE TABLE IF NOT EXISTS phrases (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE NOT NULL,
  original_emotion TEXT NOT NULL,
  style VARCHAR(50) NOT NULL,
  phrase VARCHAR(200) NOT NULL,
  language VARCHAR(2) DEFAULT 'es',
  is_favorite BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Crear índices
CREATE INDEX IF NOT EXISTS idx_phrases_user_id ON phrases(user_id);
CREATE INDEX IF NOT EXISTS idx_phrases_created_at ON phrases(created_at);

-- ======================================
-- 🔐 Row Level Security
-- ======================================
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE phrases ENABLE ROW LEVEL SECURITY;

-- Primero limpiar políticas antiguas en users
DROP POLICY IF EXISTS "Users can view own profile" ON users;
DROP POLICY IF EXISTS "Users can update own profile" ON users;
DROP POLICY IF EXISTS "Users can insert own profile" ON users;
DROP POLICY IF EXISTS "Enable insert for authenticated users only" ON users;

-- Crear políticas users
CREATE POLICY "Users can view own profile" ON users
  FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON users
  FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Users can insert own profile" ON users
  FOR INSERT WITH CHECK (auth.uid() = id);

CREATE POLICY "Enable insert for authenticated users only" ON users
  FOR INSERT WITH CHECK (auth.uid() = id OR auth.role() = 'service_role');

-- Primero limpiar políticas antiguas en phrases
DROP POLICY IF EXISTS "Users can view own phrases" ON phrases;
DROP POLICY IF EXISTS "Users can insert own phrases" ON phrases;
DROP POLICY IF EXISTS "Users can update own phrases" ON phrases;
DROP POLICY IF EXISTS "Users can delete own phrases" ON phrases;

-- Crear políticas phrases
CREATE POLICY "Users can view own phrases" ON phrases
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own phrases" ON phrases
  FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own phrases" ON phrases
  FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own phrases" ON phrases
  FOR DELETE USING (auth.uid() = user_id);

-- ======================================
-- 🔄 Trigger para sincronizar auth.users → users
-- ======================================
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
DROP FUNCTION IF EXISTS public.handle_new_user();

-- ✅ Función segura con search_path fijo
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER
SET search_path = public -- <-- Asegura que todo se ejecute en el esquema correcto
AS $$
BEGIN
  INSERT INTO public.users (id, email, user_name)
  VALUES (NEW.id, NEW.email, NEW.raw_user_meta_data->>'user_name');
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW
  EXECUTE FUNCTION public.handle_new_user();

-- ======================================
-- 🔑 Índice único para evitar duplicados de frases
-- ======================================
DROP INDEX IF EXISTS uniq_phrase_per_user;
CREATE UNIQUE INDEX IF NOT EXISTS uniq_phrase_per_user 
ON phrases(user_id, phrase);
```

### **Paso 5: Configurar variables de entorno**

#### **Local (.env):**
```bash
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_KEY=tu-anon-key-aqui
```

#### **Render:**
1. Ve a tu aplicación en Render
2. **Environment** → **Environment Variables**
3. Agrega:
   - `SUPABASE_URL` = tu URL de Supabase
   - `SUPABASE_KEY` = tu anon key

### **Paso 6: Instalar dependencias**

```bash
pip install supabase
```

### **Paso 7: Migrar datos locales**

```bash
python migrate_to_supabase.py
```

## 🔧 Scripts disponibles

- **`supabase_config.py`** - Configuración y prueba de conexión
- **`supabase_service.py`** - Servicio para operaciones de BD
- **`migrate_to_supabase.py`** - Migra datos de SQLite a Supabase
- **`test.py`** - Ver contenido de la base de datos

## 🚀 Configuración automática

La aplicación detecta automáticamente si Supabase está configurado:

- **Con Supabase:** Usa Supabase para persistencia
- **Sin Supabase:** Usa SQLite local (fallback)

## 📊 Verificar configuración

### **Probar conexión:**
```bash
python supabase_config.py
```

### **Ver datos:**
```bash
python test.py
```

### **Migrar datos:**
```bash
python migrate_to_supabase.py
```

## 🔧 Troubleshooting

### **Error: "SUPABASE_URL not found"**
- Verifica que las variables de entorno estén configuradas
- Asegúrate de que los nombres sean exactos

### **Error: "Connection refused"**
- Verifica que el proyecto esté activo en Supabase
- Revisa que la URL sea correcta

### **Error: "Table not found"**
- Crea la tabla `phrase` en Supabase
- Usa el SQL proporcionado arriba

### **Error: "Permission denied"**
- Verifica que estés usando la `anon` key, no la `service_role`
- Revisa las políticas de seguridad en Supabase

## 🎯 Próximos pasos

1. ✅ Crear proyecto en Supabase
2. ✅ Crear tabla `phrase`
3. ✅ Configurar variables de entorno
4. ✅ Migrar datos locales
5. ✅ Probar la aplicación
6. ✅ Desplegar en Render

## 💡 Tips

- **Backup automático:** Supabase hace backups automáticos
- **Escalabilidad:** Puedes actualizar a planes pagados cuando crezcas
- **Seguridad:** Las políticas de seguridad protegen tus datos
- **API:** Puedes usar la API REST directamente si necesitas

---

**🎉 ¡Listo!** Tu aplicación ahora tiene persistencia de datos entre despliegues. 