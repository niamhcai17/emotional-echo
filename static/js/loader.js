/**
 * Loader Controller - Controla la pantalla de carga con animación de lápiz
 * Optimizado para IA generativa con timing adaptativo
 */

class LoaderController {
    constructor() {
        this.loader = null;
        this.messageIndex = 0;
        this.startTime = null;
        this.isLongRequest = false;
        
        // Mensajes adaptativos basados en el tiempo
        this.initialMessages = [
            "Conectando con la IA...",
            "Preparando la generación...",
            "Analizando tu emoción..."
        ];
        
        this.longRequestMessages = [
            "La IA está procesando tu solicitud...",
            "Generando la frase perfecta...",
            "Esto puede tomar unos segundos más...",
            "Casi listo..."
        ];
        
        this.messageInterval = null;
        this.init();
    }

    init() {
        this.createLoader();
        this.bindEvents();
    }

    createLoader() {
        // Crear el HTML del loader
        const loaderHTML = `
            <div id="loader-overlay" class="loader-overlay">
                <div class="loader-content">
                    <p class="loader-subtitle">Transformando tus emociones en poesía</p>
                    
                    <div class="pencil-container">
                        <div class="pencil"></div>
                        <div class="writing-line"></div>
                    </div>
                    
                    <div class="loading-dots">
                        <div class="dot"></div>
                        <div class="dot"></div>
                        <div class="dot"></div>
                    </div>
                    
                    <p class="status-message" id="status-message">${this.initialMessages[0]}</p>
                    <p class="time-info" id="time-info" style="font-size: 0.9rem; opacity: 0.7; margin-top: 0.5rem;"></p>
                </div>
            </div>
        `;

        // Insertar en el DOM
        document.body.insertAdjacentHTML('beforeend', loaderHTML);
        this.loader = document.getElementById('loader-overlay');
        this.statusMessage = document.getElementById('status-message');
        this.timeInfo = document.getElementById('time-info');
    }

    bindEvents() {
        // Escuchar eventos de generación de frases
        document.addEventListener('DOMContentLoaded', () => {
            const generateForm = document.getElementById('generateForm');
            if (generateForm) {
                generateForm.addEventListener('submit', (e) => {
                    this.show();
                });
            }
        });
    }

    show() {
        if (!this.loader) return;
        
        // Registrar tiempo de inicio
        this.startTime = Date.now();
        this.isLongRequest = false;
        
        // Mostrar loader
        this.loader.classList.add('show');
        this.loader.classList.remove('hide');
        
        // Iniciar con mensajes iniciales
        this.startMessageRotation();
        
        // Iniciar timer para mensajes adaptativos
        this.startAdaptiveTimer();
        
        // Scroll al top para mejor experiencia
        window.scrollTo({ top: 0, behavior: 'smooth' });
        
        console.log('🖊️ Loader activado - Iniciando generación con IA...');
    }

    hide() {
        if (!this.loader) return;
        
        // Calcular tiempo total
        const totalTime = Date.now() - this.startTime;
        
        // Parar timers
        this.stopMessageRotation();
        this.stopAdaptiveTimer();
        
        // Mostrar mensaje final basado en el tiempo
        this.showFinalMessage(totalTime);
        
        // Ocultar después de un delay
        setTimeout(() => {
            this.loader.classList.add('hide');
            setTimeout(() => {
                this.loader.classList.remove('show', 'hide');
            }, 300);
        }, 1000);
        
        console.log(`✨ Loader desactivado - Generación completada en ${totalTime}ms`);
    }

    startMessageRotation() {
        this.messageIndex = 0;
        this.messageInterval = setInterval(() => {
            this.messageIndex++;
            const messages = this.isLongRequest ? this.longRequestMessages : this.initialMessages;
            
            if (this.messageIndex >= messages.length) {
                this.messageIndex = 0;
            }
            
            this.statusMessage.textContent = messages[this.messageIndex];
        }, 2000);
    }

    stopMessageRotation() {
        if (this.messageInterval) {
            clearInterval(this.messageInterval);
            this.messageInterval = null;
        }
    }

    startAdaptiveTimer() {
        // Después de 3 segundos, cambiar a mensajes de "procesamiento largo"
        setTimeout(() => {
            this.isLongRequest = true;
            this.messageIndex = 0;
            this.statusMessage.textContent = this.longRequestMessages[0];
        }, 3000);
        
        // Actualizar tiempo cada segundo
        this.timeInterval = setInterval(() => {
            const elapsed = Math.floor((Date.now() - this.startTime) / 1000);
            this.timeInfo.textContent = `${elapsed}s`;
        }, 1000);
    }

    stopAdaptiveTimer() {
        if (this.timeInterval) {
            clearInterval(this.timeInterval);
            this.timeInterval = null;
        }
    }

    showFinalMessage(totalTime) {
        let finalMessage = "¡Listo!";
        
        if (totalTime > 10000) {
            finalMessage = "¡Listo! (La conexión fue lenta, pero valió la pena)";
        } else if (totalTime > 5000) {
            finalMessage = "¡Listo! (La IA tomó su tiempo para crear algo especial)";
        }
        
        this.statusMessage.textContent = finalMessage;
        this.timeInfo.textContent = `Tiempo total: ${Math.floor(totalTime / 1000)}s`;
    }

    showError(message = 'Error en la generación') {
        if (!this.loader) return;
        
        this.stopMessageRotation();
        this.stopAdaptiveTimer();
        
        this.statusMessage.textContent = message;
        this.statusMessage.style.color = '#dc3545';
        
        setTimeout(() => {
            this.hide();
        }, 3000);
    }

    showCustomMessage(message, duration = 2000) {
        if (!this.loader) return;
        
        this.stopMessageRotation();
        this.statusMessage.textContent = message;
        
        setTimeout(() => {
            this.startMessageRotation();
        }, duration);
    }
}

// Instancia global
const loaderController = new LoaderController();

// Funciones globales para compatibilidad
function showLoader() {
    loaderController.show();
}

function hideLoader() {
    loaderController.hide();
}

function showLoaderError(message) {
    loaderController.showError(message);
}

function showLoaderMessage(message, duration) {
    loaderController.showCustomMessage(message, duration);
}
