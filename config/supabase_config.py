#!/usr/bin/env python3
"""
Configuración para Supabase
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Cargar variables de entorno desde .env
load_dotenv()

# Configuración de Supabase
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

supabase = None

def get_supabase_client() -> Client:
    """Crea y retorna el cliente de Supabase"""
    global supabase
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("SUPABASE_URL y SUPABASE_KEY deben estar configurados")
    
    try:
        # Intentar crear cliente con configuración estándar
        if supabase is None:
            supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        return supabase
    except Exception as e:
        print(f"Error con configuración estándar: {e}")
        # Si falla, intentar con configuración SSL deshabilitada
        try:
            import httpx
            http_client = httpx.Client(verify=False, timeout=30.0)
            return create_client(
                SUPABASE_URL, 
                SUPABASE_KEY,
                options={'httpx_client': http_client}
            )
        except Exception as e2:
            print(f"Error con SSL deshabilitado: {e2}")
            raise e2

def test_supabase_connection():
    """Prueba la conexión con Supabase"""
    try:
        supabase = get_supabase_client()
        
        # Intentar hacer una consulta simple a la tabla users
        response = supabase.table('users').select('*').limit(1).execute()
        
        print("✅ Conexión a Supabase exitosa")
        print(f"📊 Tabla 'users' encontrada")
        
        # Verificar también la tabla phrases
        response = supabase.table('phrases').select('*').limit(1).execute()
        print(f"📊 Tabla 'phrases' encontrada")
        
        return True
        
    except Exception as e:
        print(f"❌ Error conectando a Supabase: {e}")
        print(f"Tipo de error: {type(e)}")
        import traceback
        traceback.print_exc()
        print("💡 Asegúrate de que las tablas 'users' y 'phrases' existan en tu base de datos")
        return False

def create_tables_supabase():
    """Crea las tablas en Supabase usando SQL"""
    
    # SQL para crear las tablas según el nuevo esquema
    create_tables_sql = """
    -- ======================================
    -- 🚀 Script limpio para Supabase (Definitivo)
    -- ======================================

    -- 1. Crear Tablas (Schema public explícito)
    CREATE TABLE IF NOT EXISTS public.users (
      id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
      email TEXT UNIQUE NOT NULL,
      user_name TEXT,
      created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
      updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );

    CREATE TABLE IF NOT EXISTS public.phrases (
      id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
      user_id UUID REFERENCES public.users(id) ON DELETE CASCADE NOT NULL,
      original_emotion TEXT NOT NULL,
      style VARCHAR(50) NOT NULL,
      phrase VARCHAR(200) NOT NULL,
      language VARCHAR(2) DEFAULT 'es',
      is_favorite BOOLEAN DEFAULT FALSE,
      created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
      updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );

    -- 2. Índices
    CREATE INDEX IF NOT EXISTS idx_phrases_user_id ON public.phrases(user_id);
    CREATE INDEX IF NOT EXISTS idx_phrases_created_at ON public.phrases(created_at);
    CREATE INDEX IF NOT EXISTS idx_users_id ON public.users(id);

    -- 3. Row Level Security (RLS)
    ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
    ALTER TABLE public.phrases ENABLE ROW LEVEL SECURITY;

    -- Limpieza de políticas antiguas para evitar conflictos
    DROP POLICY IF EXISTS "Users can view own profile" ON public.users;
    DROP POLICY IF EXISTS "Users can update own profile" ON public.users;
    DROP POLICY IF EXISTS "Users can insert own profile" ON public.users;
    DROP POLICY IF EXISTS "admins_full_access" ON public.users;
    
    DROP POLICY IF EXISTS "Users can view own phrases" ON public.phrases;
    DROP POLICY IF EXISTS "Users can insert own phrases" ON public.phrases;
    DROP POLICY IF EXISTS "Users can update own phrases" ON public.phrases;
    DROP POLICY IF EXISTS "Users can delete own phrases" ON public.phrases;

    -- Políticas de Usuarios
    CREATE POLICY "Users can view own profile" ON public.users
      FOR SELECT TO authenticated USING (auth.uid() = id);

    CREATE POLICY "Users can update own profile" ON public.users
      FOR UPDATE TO authenticated USING (auth.uid() = id);

    -- Permitir insert si es el mismo usuario o service_role (backup)
    CREATE POLICY "Users can insert own profile" ON public.users
      FOR INSERT TO authenticated WITH CHECK (auth.uid() = id OR auth.role() = 'service_role');
      
    -- Políticas de Frases
    CREATE POLICY "Users can view own phrases" ON public.phrases
      FOR SELECT TO authenticated USING (auth.uid() = user_id);

    CREATE POLICY "Users can insert own phrases" ON public.phrases
      FOR INSERT TO authenticated WITH CHECK (auth.uid() = user_id);

    CREATE POLICY "Users can update own phrases" ON public.phrases
      FOR UPDATE TO authenticated USING (auth.uid() = user_id)
      WITH CHECK (auth.uid() = user_id);

    CREATE POLICY "Users can delete own phrases" ON public.phrases
      FOR DELETE TO authenticated USING (auth.uid() = user_id);

    -- 4. Trigger de Sincronización (Auth -> Public)
    -- Importante: search_path = public para evitar problemas de seguridad
    CREATE OR REPLACE FUNCTION public.handle_new_user()
    RETURNS TRIGGER
    SECURITY DEFINER SET search_path = public
    AS $$
    BEGIN
      INSERT INTO public.users (id, email, user_name)
      VALUES (NEW.id, NEW.email, COALESCE(NEW.raw_user_meta_data->>'user_name', ''));
      RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;

    DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
    CREATE TRIGGER on_auth_user_created
      AFTER INSERT ON auth.users
      FOR EACH ROW
      EXECUTE FUNCTION public.handle_new_user();

    -- 5. Restricción de Unicidad (Evitar duplicados)
    DROP INDEX IF EXISTS uniq_phrase_per_user;
    CREATE UNIQUE INDEX IF NOT EXISTS uniq_phrase_per_user 
    ON public.phrases(user_id, phrase);
    """
    
    try:
        supabase = get_supabase_client()
        
        # Ejecutar SQL para crear tablas
        result = supabase.rpc('exec_sql', {'sql': create_tables_sql}).execute()
        
        print("✅ Tablas 'users' y 'phrases' creadas en Supabase")
        return True
        
    except Exception as e:
        print(f"⚠️  Las tablas ya existen o error: {e}")
        return True  # Asumimos que las tablas ya existen

if __name__ == "__main__":
    print("🔄 Probando conexión con Supabase...")
    print(f"🔍 SUPABASE_URL: {SUPABASE_URL}")
    print(f"🔍 SUPABASE_KEY: {SUPABASE_KEY[:10] + '...' if SUPABASE_KEY else 'No encontrada'}")
    
    if test_supabase_connection():
        print("✅ Configuración de Supabase completada")
    else:
        print("❌ Verifica las variables de entorno SUPABASE_URL y SUPABASE_KEY")
        print("💡 Asegúrate de que el archivo .env esté configurado correctamente") 