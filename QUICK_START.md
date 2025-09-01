# 🚀 Inicio Rápido - Entrelíneas

## ⚡ Ejecutar en 5 minutos

### 1. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 2. Configurar variables de entorno
Copia `env.example` a `.env` y llena tus credenciales:
```bash
cp env.example .env
# Edita .env con tus credenciales
```

### 3. Ejecutar la aplicación
```bash
python main.py
```

### 4. Abrir en el navegador
```
http://localhost:5000
```

## 🔑 Variables de Entorno Requeridas

```bash
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_KEY=tu-service-role-key
SUPABASE_ANON_KEY=tu-anon-key
OPENAI_API_KEY=tu-openai-key
SESSION_SECRET=tu-secret-key
```

## 📋 Configuración de Supabase

1. **Habilita Google Auth** en Authentication → Providers
2. **Ejecuta el script SQL** del README.md en el SQL Editor
3. **Configura Google OAuth** en Google Cloud Console

## 🆘 Problemas Comunes

- **Import Error**: Verifica que las carpetas `services/` y `config/` existan
- **Connection Error**: Revisa `SUPABASE_URL` y `SUPABASE_KEY`
- **Auth Error**: Confirma que Google Auth esté habilitado en Supabase

## 📖 Documentación Completa

Ver `README.md` para instrucciones detalladas.
