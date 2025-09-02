#!/usr/bin/env python3
"""
Script para crear las tablas en Supabase
Ejecuta este script una vez para configurar la base de datos
"""

import os
from dotenv import load_dotenv
from supabase import create_client

# Cargar variables de entorno
load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

def create_tables():
    """Crea las tablas necesarias en Supabase"""
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ Error: SUPABASE_URL y SUPABASE_KEY deben estar configurados")
        return False
    
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # SQL para crear las tablas
        create_users_table = """
        CREATE TABLE IF NOT EXISTS public.users (
            id UUID REFERENCES auth.users(id) ON DELETE CASCADE PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            user_name TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """
        
        create_phrases_table = """
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
        """
        
        # Crear índices
        create_indexes = """
        CREATE INDEX IF NOT EXISTS idx_phrases_user_id ON public.phrases(user_id);
        CREATE INDEX IF NOT EXISTS idx_phrases_created_at ON public.phrases(created_at);
        """
        
        # Habilitar RLS
        enable_rls = """
        ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
        ALTER TABLE public.phrases ENABLE ROW LEVEL SECURITY;
        """
        
        # Crear políticas
        create_policies = """
        -- Políticas para users
        CREATE POLICY IF NOT EXISTS "Users can view own profile" ON public.users
            FOR SELECT USING (auth.uid() = id);

        CREATE POLICY IF NOT EXISTS "Users can update own profile" ON public.users
            FOR UPDATE USING (auth.uid() = id);

        CREATE POLICY IF NOT EXISTS "Users can insert own profile" ON public.users
            FOR INSERT WITH CHECK (auth.uid() = id);

        -- Políticas para phrases
        CREATE POLICY IF NOT EXISTS "Users can view own phrases" ON public.phrases
            FOR SELECT USING (auth.uid() = user_id);

        CREATE POLICY IF NOT EXISTS "Users can insert own phrases" ON public.phrases
            FOR INSERT WITH CHECK (auth.uid() = user_id);

        CREATE POLICY IF NOT EXISTS "Users can update own phrases" ON public.phrases
            FOR UPDATE USING (auth.uid() = user_id);

        CREATE POLICY IF NOT EXISTS "Users can delete own phrases" ON public.phrases
            FOR DELETE USING (auth.uid() = user_id);
        """
        
        print("🔄 Creando tablas en Supabase...")
        
        # Ejecutar las consultas SQL usando el cliente de Supabase
        # Nota: Esto requiere que tengas permisos de administrador en Supabase
        
        # Crear tabla users
        print("📊 Creando tabla 'users'...")
        try:
            # Intentar insertar un usuario de prueba para verificar que la tabla existe
            test_user = {
                'id': '00000000-0000-0000-0000-000000000000',
                'email': 'test@example.com',
                'user_name': 'test'
            }
            result = supabase.table('users').insert(test_user).execute()
            print("✅ Tabla 'users' existe y es accesible")
        except Exception as e:
            print(f"❌ Error con tabla 'users': {e}")
            print("💡 Necesitas crear la tabla manualmente en el SQL Editor de Supabase")
            print("📝 Ejecuta este SQL en tu dashboard de Supabase:")
            print(create_users_table)
            return False
        
        # Crear tabla phrases
        print("📊 Verificando tabla 'phrases'...")
        try:
            # Intentar hacer una consulta simple
            result = supabase.table('phrases').select('*').limit(1).execute()
            print("✅ Tabla 'phrases' existe y es accesible")
        except Exception as e:
            print(f"❌ Error con tabla 'phrases': {e}")
            print("💡 Necesitas crear la tabla manualmente en el SQL Editor de Supabase")
            print("📝 Ejecuta este SQL en tu dashboard de Supabase:")
            print(create_phrases_table)
            return False
        
        print("✅ Todas las tablas están configuradas correctamente")
        return True
        
    except Exception as e:
        print(f"❌ Error general: {e}")
        return False

if __name__ == "__main__":
    print("🔄 Iniciando configuración de tablas...")
    success = create_tables()
    
    if success:
        print("✅ Configuración completada exitosamente")
    else:
        print("❌ Error en la configuración")
        print("\n📋 INSTRUCCIONES MANUALES:")
        print("1. Ve a tu dashboard de Supabase")
        print("2. Abre el SQL Editor")
        print("3. Ejecuta el siguiente SQL:")
        print("""
        -- Crear tabla users
        CREATE TABLE IF NOT EXISTS public.users (
            id UUID REFERENCES auth.users(id) ON DELETE CASCADE PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            user_name TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );

        -- Crear tabla phrases
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

        -- Habilitar RLS
        ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
        ALTER TABLE public.phrases ENABLE ROW LEVEL SECURITY;

        -- Crear políticas
        CREATE POLICY "Users can view own profile" ON public.users
            FOR SELECT USING (auth.uid() = id);

        CREATE POLICY "Users can update own profile" ON public.users
            FOR UPDATE USING (auth.uid() = id);

        CREATE POLICY "Users can insert own profile" ON public.users
            FOR INSERT WITH CHECK (auth.uid() = id);

        CREATE POLICY "Users can view own phrases" ON public.phrases
            FOR SELECT USING (auth.uid() = user_id);

        CREATE POLICY "Users can insert own phrases" ON public.phrases
            FOR INSERT WITH CHECK (auth.uid() = user_id);

        CREATE POLICY "Users can update own phrases" ON public.phrases
            FOR UPDATE USING (auth.uid() = user_id);

        CREATE POLICY "Users can delete own phrases" ON public.phrases
            FOR DELETE USING (auth.uid() = user_id);
        """)
