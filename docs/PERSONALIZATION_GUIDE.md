# 👋 Guía de Personalización - EmotionalEcho

## 🎯 ¿Qué es la Personalización?

La nueva funcionalidad de **personalización** permite que la aplicación salude al usuario por su nombre, creando una experiencia más cálida y personal. En lugar de un simple "¿Cómo te sientes?", ahora verás "Hola, Juli ¿Cómo te sientes?".

## ✨ Funcionalidades Implementadas

### 1. **Modal de Bienvenida**
- Aparece automáticamente en la primera visita
- Solicita amablemente el nombre del usuario
- Diseño elegante y no intrusivo

### 2. **Saludo Personalizado**
- Cambia dinámicamente el texto de la pregunta
- Mantiene el contexto emocional
- Compatible con ambos idiomas

### 3. **Persistencia del Nombre**
- Almacenamiento local (localStorage)
- Sincronización con backend (cookies)
- Duración de 30 días

### 4. **Cambio de Nombre**
- Botón en la navegación para cambiar nombre
- Actualización en tiempo real
- Sin necesidad de recargar la página

## 🚀 Cómo Funciona

### **Primera Visita:**
1. El usuario abre la aplicación
2. Aparece el modal de bienvenida
3. Ingresa su nombre
4. El saludo cambia a "Hola, [nombre] ¿Cómo te sientes?"
5. El nombre se guarda para futuras visitas

### **Visitas Posteriores:**
1. El usuario abre la aplicación
2. El saludo aparece personalizado automáticamente
3. Puede cambiar su nombre desde la navegación

### **Cambio de Nombre:**
1. Hacer clic en el nombre en la navegación
2. Aparece un prompt para ingresar nuevo nombre
3. El saludo se actualiza inmediatamente

## 📱 Interfaz de Usuario

### **Modal de Bienvenida:**
```
┌─────────────────────────────────┐
│  ¡Bienvenido a Entrelíneas!    │
│                                 │
│  Transforma tus emociones       │
│  en poesía                      │
│                                 │
│  Para hacer tu experiencia      │
│  más personal, ¿podrías         │
│  decirme tu nombre?             │
│                                 │
│  ┌─────────────────────────────┐ │
│  │      Tu nombre             │ │
│  └─────────────────────────────┘ │
│                                 │
│  [¡Comenzar!]                   │
└─────────────────────────────────┘
```

### **Saludo Personalizado:**
```
Antes: ¿Cómo te sientes?
Después: Hola, Juli ¿Cómo te sientes?
```

### **Navegación:**
```
[Inicio] [Mi Colección] [Favoritos] [Estadísticas] [Juli]
```

## 🔧 Implementación Técnica

### **Frontend (JavaScript):**
```javascript
// Almacenamiento local
localStorage.setItem('userName', userName);

// Actualización dinámica
emotionLabel.textContent = `Hola, ${userName} ¿Cómo te sientes?`;

// Sincronización con backend
fetch('/api/user/name', {
    method: 'POST',
    body: JSON.stringify({ user_name: userName })
});
```

### **Backend (Python/Flask):**
```python
@app.route('/api/user/name', methods=['GET', 'POST'])
def user_name_api():
    if request.method == 'POST':
        user_name = data.get('user_name', '').strip()
        response.set_cookie('user_name', user_name, max_age=30*24*60*60)
```

### **Plantillas (HTML):**
```html
<label for="emotion" class="form-label" id="emotionLabel">
    {% if user_name %}
        Hola, {{ user_name }} ¿Cómo te sientes?
    {% else %}
        ¿Cómo te sientes?
    {% endif %}
</label>
```

## 🌍 Compatibilidad Multilingüe

### **Funciona con Ambos Idiomas:**
- **Español:** "Hola, Juli ¿Cómo te sientes?"
- **Inglés:** "Hello, John How do you feel?"

### **Detección Automática:**
- El sistema detecta el idioma del input
- Mantiene la personalización en ambos idiomas
- No interfiere con la funcionalidad multilingüe existente

## 📊 Almacenamiento de Datos

### **LocalStorage:**
- Nombre del usuario
- Persistencia entre sesiones
- Acceso inmediato

### **Cookies (Backend):**
- Sincronización con servidor
- Duración: 30 días
- Compatible con múltiples dispositivos

### **Seguridad:**
- Solo almacena el nombre
- No información personal sensible
- Fácil de eliminar

## 🎨 Experiencia de Usuario

### **Beneficios:**
1. **Más Personal:** El usuario se siente reconocido
2. **Más Cálido:** Crea una conexión emocional
3. **Más Intuitivo:** Interfaz más amigable
4. **Más Memorable:** Mejora la retención de usuarios

### **Casos de Uso:**
- **Primera vez:** Modal de bienvenida
- **Uso regular:** Saludo personalizado
- **Cambio de nombre:** Actualización fácil
- **Múltiples usuarios:** Cada uno con su nombre

## 🔧 Scripts de Prueba

### **Probar Personalización:**
```bash
python test_personalization.py
```

### **Probar Manualmente:**
1. Abrir http://localhost:5000
2. Ver modal de bienvenida
3. Ingresar nombre
4. Verificar saludo personalizado
5. Cambiar nombre desde navegación

## 🐛 Troubleshooting

### **Problema: Modal no aparece**
- **Solución:** Limpiar localStorage del navegador
- **Comando:** `localStorage.clear()`

### **Problema: Nombre no se guarda**
- **Solución:** Verificar conexión con backend
- **Verificar:** Consola del navegador para errores

### **Problema: Saludo no se actualiza**
- **Solución:** Recargar la página
- **Verificar:** Que el elemento `emotionLabel` existe

### **Problema: Cookies no funcionan**
- **Solución:** Verificar configuración del navegador
- **Alternativa:** Usar solo localStorage

## 🎯 Próximas Mejoras

### **Funcionalidades Futuras:**
1. **Preferencias de idioma:** Guardar idioma preferido
2. **Temas personalizados:** Colores según preferencia
3. **Estadísticas personales:** Frases por usuario
4. **Perfil completo:** Más información personalizable

### **Mejoras Técnicas:**
1. **Base de datos:** Almacenar nombres en Supabase
2. **Autenticación:** Sistema de usuarios completo
3. **Sincronización:** Entre dispositivos
4. **Backup:** Respaldo de preferencias

## 📈 Métricas de Éxito

### **Indicadores a Medir:**
- Tasa de completación del modal de bienvenida
- Frecuencia de cambio de nombres
- Tiempo de permanencia en la aplicación
- Satisfacción del usuario

### **Herramientas de Análisis:**
- Google Analytics
- Hotjar (heatmaps)
- Encuestas de satisfacción
- Métricas de retención

## 🎉 Conclusión

La funcionalidad de personalización **transforma** la experiencia del usuario de:

**Antes:** "¿Cómo te sientes?" (genérico)
**Después:** "Hola, Juli ¿Cómo te sientes?" (personal)

### **Beneficios Clave:**
1. ✅ **Experiencia más cálida**
2. ✅ **Mayor engagement**
3. ✅ **Mejor retención**
4. ✅ **Interfaz más humana**
5. ✅ **Fácil implementación**

---

**🌟 ¡La personalización hace que cada usuario se sienta especial!**
