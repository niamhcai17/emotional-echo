# 🎨 Personalización del Loader - Entrelíneas

## 🖊️ Descripción de la Animación

El loader incluye una animación divertida de un **lápiz escribiendo** que simula el proceso creativo de generar frases poéticas. La animación incluye:

- ✏️ **Lápiz animado** que se mueve simulando escritura (punta hacia abajo)
- ✨ **Línea de escritura** que se extiende con efecto dorado
- 💫 **Puntos de carga** que pulsan rítmicamente
- 🔄 **Mensajes rotativos** que cambian automáticamente
- 🎭 **Transiciones suaves** de entrada y salida
- 🧹 **Diseño limpio** sin título, solo el mensaje principal

## 🎯 Archivos del Loader

### **CSS**: `static/css/loader.css`
- Contiene todos los estilos y animaciones
- Responsive design para móviles y desktop
- Variables CSS para fácil personalización

### **JavaScript**: `static/js/loader.js`
- Controla la lógica del loader
- Maneja eventos y transiciones
- API para mostrar/ocultar el loader

## 🎨 Personalización de Colores

### Cambiar colores principales en `loader.css`:

```css
/* Color de fondo del overlay */
.loader-overlay {
    background: rgba(0, 0, 0, 0.95); /* Cambiar a tu color preferido */
}

/* Color del lápiz */
.pencil {
    background: linear-gradient(45deg, #8B4513, #D2691E, #CD853F); /* Colores del lápiz */
}

/* Color de la línea de escritura */
.writing-line {
    background: linear-gradient(90deg, #FFD700, #FFA500); /* Línea dorada */
}

/* Color de los puntos de carga */
.loading-dots .dot {
    background: #FFD700; /* Puntos dorados */
}
```

### Ejemplos de esquemas de colores:

```css
/* Tema Azul */
.loader-overlay { background: rgba(25, 118, 210, 0.95); }
.pencil { background: linear-gradient(45deg, #1976d2, #42a5f5, #90caf9); }
.writing-line { background: linear-gradient(90deg, #64b5f6, #2196f3); }

/* Tema Verde */
.loader-overlay { background: rgba(76, 175, 80, 0.95); }
.pencil { background: linear-gradient(45deg, #4caf50, #81c784, #a5d6a7); }
.writing-line { background: linear-gradient(90deg, #66bb6a, #4caf50); }

/* Tema Púrpura */
.loader-overlay { background: rgba(156, 39, 176, 0.95); }
.pencil { background: linear-gradient(45deg, #9c27b0, #ba68c8, #ce93d8); }
.writing-line { background: linear-gradient(90deg, #ab47bc, #9c27b0); }
```

## ✏️ Personalización del Lápiz

### Cambiar el tamaño del lápiz:

```css
.pencil {
    width: 8px;        /* Ancho del lápiz */
    height: 60px;      /* Alto del lápiz */
}

/* Para móviles */
@media (max-width: 768px) {
    .pencil {
        width: 6px;    /* Lápiz más delgado en móviles */
        height: 50px;  /* Lápiz más corto en móviles */
    }
}
```

### Cambiar la forma del lápiz:

```css
.pencil::before {
    /* Punta del lápiz */
    border-bottom: 8px solid #8B4513; /* Color de la punta */
}

.pencil::after {
    /* Base del lápiz */
    width: 12px;  /* Ancho de la base */
    height: 2px;  /* Alto de la base */
}
```

## 🔄 Personalización de Animaciones

### Cambiar velocidad de las animaciones:

```css
/* Velocidad del lápiz escribiendo */
.pencil {
    animation: pencilWrite 2s ease-in-out infinite; /* 2 segundos por ciclo */
}

/* Velocidad de la línea de escritura */
.writing-line {
    animation: writeLine 2s ease-in-out infinite; /* 2 segundos por ciclo */
}

/* Velocidad de los puntos */
.loading-dots .dot {
    animation: dotPulse 1.4s ease-in-out infinite both; /* 1.4 segundos por ciclo */
}
```

### Crear nuevas animaciones:

```css
/* Ejemplo: Lápiz que rebota */
@keyframes pencilBounce {
    0%, 100% { transform: translate(-50%, -50%) translateY(0); }
    50% { transform: translate(-50%, -50%) translateY(-10px); }
}

.pencil {
    animation: pencilBounce 1s ease-in-out infinite;
}

/* Ejemplo: Línea que se dibuja de derecha a izquierda */
@keyframes writeLineReverse {
    0% { width: 150px; transform: translateX(-50%) scaleX(1); }
    100% { width: 0; transform: translateX(-50%) scaleX(-1); }
}
```

## 💬 Personalización de Mensajes

### Cambiar mensajes en `loader.js`:

```javascript
this.messages = [
    "Pensando en las palabras perfectas...",
    "Dando forma a tus emociones...",
    "Creando magia poética...",
    "Casi listo...",
    "¡Tu frase está lista!"
];
```

### Agregar mensajes personalizados:

```javascript
// Mostrar mensaje personalizado
window.showLoaderMessage("Procesando tu solicitud...", 3000);

// Mostrar error
window.showLoaderError("Error de conexión");

// Mostrar progreso
window.showLoaderProgress(2, 5); // Paso 2 de 5
```

## 📱 Personalización Responsive

### Ajustes para diferentes tamaños de pantalla:

```css
/* Tablets */
@media (max-width: 1024px) {
    .loader-title { font-size: 2.2rem; }
    .pencil-container { width: 180px; height: 110px; }
}

/* Móviles pequeños */
@media (max-width: 480px) {
    .loader-title { font-size: 1.8rem; }
    .loader-subtitle { font-size: 0.9rem; }
    .pencil-container { width: 120px; height: 80px; }
    .pencil { width: 5px; height: 40px; }
}
```

## 🎭 Temas Personalizados

### Crear un tema completo:

```css
/* Tema "Noche Estrellada" */
.loader-overlay {
    background: linear-gradient(135deg, #0c1445 0%, #1a1a2e 100%);
}

.loader-title {
    color: #e8f4fd;
    text-shadow: 0 0 20px rgba(232, 244, 253, 0.5);
}

.pencil {
    background: linear-gradient(45deg, #ffd700, #ffed4e, #fff200);
    box-shadow: 0 0 15px rgba(255, 215, 0, 0.6);
}

.writing-line {
    background: linear-gradient(90deg, #ffd700, #ffed4e);
    box-shadow: 0 0 10px rgba(255, 215, 0, 0.8);
}

.loading-dots .dot {
    background: #ffd700;
    box-shadow: 0 0 10px rgba(255, 215, 0, 0.6);
}
```

## 🔧 Integración Avanzada

### Controlar el loader desde tu código:

```javascript
// Mostrar loader con progreso personalizado
function generatePhraseWithProgress() {
    showLoader();
    
    // Simular pasos de generación
    setTimeout(() => showLoaderMessage("Analizando emoción...", 1000), 0);
    setTimeout(() => showLoaderMessage("Generando palabras...", 1000), 1000);
    setTimeout(() => showLoaderMessage("Aplicando estilo...", 1000), 2000);
    setTimeout(() => showLoaderMessage("Finalizando...", 1000), 3000);
    setTimeout(() => hideLoader(), 4000);
}

// Ocultar loader automáticamente en errores
function handleError(error) {
    showLoaderError(error.message);
    // El loader se ocultará automáticamente después de 3 segundos
}
```

### Eventos personalizados:

```javascript
// Escuchar cuando el loader se muestra/oculta
document.addEventListener('loaderShown', () => {
    console.log('Loader activado');
});

document.addEventListener('loaderHidden', () => {
    console.log('Loader desactivado');
});
```

## 🎨 Consejos de Diseño

1. **Contraste**: Asegúrate de que el texto sea legible sobre el fondo
2. **Consistencia**: Mantén los colores coherentes con tu marca
3. **Accesibilidad**: Considera usuarios con problemas de visión
4. **Performance**: Las animaciones CSS son más eficientes que JavaScript
5. **Testing**: Prueba en diferentes dispositivos y navegadores

## 🚀 Próximos Pasos

1. **Prueba el demo**: Abre `demo_loader.html` en tu navegador
2. **Personaliza colores**: Modifica las variables CSS en `loader.css`
3. **Ajusta animaciones**: Cambia velocidades y efectos
4. **Integra en tu app**: El loader ya está conectado a tu formulario
5. **Testea**: Verifica que funcione en diferentes escenarios

¡Tu loader personalizado está listo para dar vida a la experiencia de generación de frases! ✨
