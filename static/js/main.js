// Auth utility functions
class AuthManager {
    constructor(supabaseClient) {
        this.supabase = supabaseClient;
        this.isCheckingAuth = false;
        this.authCheckPromise = null;
        this.retryCount = 0;
        this.maxRetries = 3;
    }

    async checkSession() {
        if (this.isCheckingAuth && this.authCheckPromise) {
            return this.authCheckPromise; // Return existing promise if check is in progress
        }
        
        this.isCheckingAuth = true;
        
        this.authCheckPromise = this._performSessionCheck();
        
        try {
            const result = await this.authCheckPromise;
            this.retryCount = 0; // Reset retry count on success
            return result;
        } finally {
            this.isCheckingAuth = false;
            this.authCheckPromise = null;
        }
    }

    async _performSessionCheck() {
        try {
            const { data: { session }, error } = await this.supabase.auth.getSession();
            
            if (error) {
                console.error('Error obteniendo sesión:', error);
                
                // Retry logic for network errors
                if (this.retryCount < this.maxRetries && this._isRetryableError(error)) {
                    this.retryCount++;
                    console.log(`Reintentando verificación de sesión (${this.retryCount}/${this.maxRetries})...`);
                    await this._delay(1000 * this.retryCount); // Exponential backoff
                    return this._performSessionCheck();
                }
                
                return { session: null, error };
            }
            
            return { session, error: null };
        } catch (error) {
            console.error('Error verificando autenticación:', error);
            
            // Retry logic for network errors
            if (this.retryCount < this.maxRetries && this._isRetryableError(error)) {
                this.retryCount++;
                console.log(`Reintentando verificación de sesión (${this.retryCount}/${this.maxRetries})...`);
                await this._delay(1000 * this.retryCount); // Exponential backoff
                return this._performSessionCheck();
            }
            
            return { session: null, error };
        }
    }

    _isRetryableError(error) {
        // Check if error is retryable (network issues, timeouts, etc.)
        const retryableMessages = ['network', 'timeout', 'fetch', 'connection'];
        const errorMessage = error.message?.toLowerCase() || '';
        return retryableMessages.some(msg => errorMessage.includes(msg));
    }

    _delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    async isAuthenticated() {
        const { session } = await this.checkSession();
        return !!session;
    }

    async getCurrentUser() {
        const { session } = await this.checkSession();
        return session ? session.user : null;
    }

    async redirectIfNotAuthenticated(redirectTo = '/landing') {
        try {
            const { session, error } = await this.checkSession();
            
            if (error) {
                console.warn('Error verificando autenticación, permitiendo acceso:', error);
                return false; // Don't redirect on error, allow user to see the page
            }
            
            if (!session && window.location.pathname !== redirectTo) {
                console.log('Usuario no autenticado, redirigiendo a:', redirectTo);
                this._showLoadingState('Verificando autenticación...');
                window.location.href = redirectTo;
                return false;
            }
            return !!session;
        } catch (error) {
            console.error('Error en redirectIfNotAuthenticated:', error);
            return false; // Don't redirect on error
        }
    }

    async redirectIfAuthenticated(redirectTo = '/') {
        try {
            const { session, error } = await this.checkSession();
            
            if (error) {
                console.warn('Error verificando autenticación, permitiendo acceso:', error);
                return false; // Don't redirect on error, allow user to see the page
            }
            
            if (session && window.location.pathname !== redirectTo) {
                console.log('Usuario ya autenticado, redirigiendo a:', redirectTo);
                this._showLoadingState('Redirigiendo...');
                window.location.href = redirectTo;
                return true;
            }
            return !!session;
        } catch (error) {
            console.error('Error en redirectIfAuthenticated:', error);
            return false; // Don't redirect on error
        }
    }

    _showLoadingState(message = 'Cargando...') {
        // Create or update loading indicator
        let loadingIndicator = document.getElementById('auth-loading');
        if (!loadingIndicator) {
            loadingIndicator = document.createElement('div');
            loadingIndicator.id = 'auth-loading';
            loadingIndicator.className = 'position-fixed top-0 start-0 w-100 h-100 d-flex align-items-center justify-content-center';
            loadingIndicator.style.cssText = 'background: rgba(255,255,255,0.9); z-index: 9999;';
            loadingIndicator.innerHTML = `
                <div class="text-center">
                    <div class="spinner-border text-primary mb-3" role="status">
                        <span class="visually-hidden">Cargando...</span>
                    </div>
                    <p class="text-muted">${message}</p>
                </div>
            `;
            document.body.appendChild(loadingIndicator);
        } else {
            loadingIndicator.querySelector('p').textContent = message;
        }
    }

    _hideLoadingState() {
        const loadingIndicator = document.getElementById('auth-loading');
        if (loadingIndicator) {
            loadingIndicator.remove();
        }
    }

    updateUserInterface(user) {
        const navUserName = document.getElementById('navUserName');
        if (navUserName && user && user.user_metadata && user.user_metadata.username) {
            navUserName.textContent = user.user_metadata.username;
        } else if (navUserName) {
            navUserName.textContent = 'Mi Perfil';
        }
    }

    setupAuthStateListener() {
        this.supabase.auth.onAuthStateChange((event, session) => {
            console.log('Auth state changed:', event, session ? 'Session exists' : 'No session');
            
            // Hide loading state when auth state changes
            this._hideLoadingState();
            
            if (event === 'SIGNED_OUT' || !session) {
                this.updateUserInterface(null);
                if (window.location.pathname !== '/landing') {
                    this._showLoadingState('Cerrando sesión...');
                    window.location.href = '/landing';
                }
            } else if (event === 'SIGNED_IN' && session) {
                this.updateUserInterface(session.user);
                this._hideLoadingState();
            } else if (event === 'TOKEN_REFRESHED' && session) {
                // Update UI when token is refreshed
                this.updateUserInterface(session.user);
            }
        });
    }
}

// Global auth manager instance (will be initialized when Supabase is available)
let authManager = null;

// Initialize auth manager when Supabase is available
function initializeAuthManager(supabaseClient) {
    if (!authManager && supabaseClient) {
        authManager = new AuthManager(supabaseClient);
        authManager.setupAuthStateListener();
        
        // Add global error handler for auth errors
        window.addEventListener('unhandledrejection', (event) => {
            if (event.reason && event.reason.message && 
                event.reason.message.includes('auth')) {
                console.error('Unhandled auth error:', event.reason);
                authManager._hideLoadingState();
            }
        });
    }
    return authManager;
}

// Utility function to check if user is authenticated (can be used anywhere)
async function isUserAuthenticated() {
    if (authManager) {
        return await authManager.isAuthenticated();
    }
    return false;
}

// Utility function to get current user (can be used anywhere)
async function getCurrentUser() {
    if (authManager) {
        return await authManager.getCurrentUser();
    }
    return null;
}

/*
 * USAGE EXAMPLES:
 * 
 * // Check if user is authenticated
 * const isAuth = await isUserAuthenticated();
 * 
 * // Get current user data
 * const user = await getCurrentUser();
 * if (user) {
 *     console.log('User:', user.email);
 * }
 * 
 * // Check session manually
 * if (authManager) {
 *     const { session, error } = await authManager.checkSession();
 *     if (session) {
 *         console.log('Active session:', session);
 *     }
 * }
 * 
 * // The auth manager automatically handles:
 * - Session checking on page load
 * - Redirecting unauthenticated users to /landing
 * - Redirecting authenticated users away from /landing
 * - Updating UI when auth state changes
 * - Retry logic for network errors
 * - Loading states during auth operations
 */

// Character counter for emotion input
document.addEventListener('DOMContentLoaded', function() {
    const emotionInput = document.getElementById('emotion');
    const charCount = document.getElementById('charCount');
    const generateBtn = document.getElementById('generateBtn');
    const emotionForm = document.getElementById('emotionForm');
    const loadingModal = new bootstrap.Modal(document.getElementById('loadingModal'));
    const deleteModal = new bootstrap.Modal(document.getElementById('deleteModal'));
    let deleteForm = null;

    // Character counter
    if (emotionInput && charCount) {
        function updateCharCount() {
            const count = emotionInput.value.length;
            charCount.textContent = count;
            
            if (count > 450) {
                charCount.style.color = '#dc3545';
            } else if (count > 350) {
                charCount.style.color = '#fd7e14';
            } else {
                charCount.style.color = '#6c757d';
            }
        }
        
        emotionInput.addEventListener('input', updateCharCount);
        updateCharCount(); // Initial count
    }

    // Form submission with loading state
    if (emotionForm && generateBtn) {
        emotionForm.addEventListener('submit', function(e) {
            if (emotionInput.value.trim() === '') {
                e.preventDefault();
                alert('Por favor, describe cómo te sientes.');
                return;
            }
            
            // Show loading state
            generateBtn.disabled = true;
            generateBtn.innerHTML = '<i class="fas fa-magic me-2"></i>Creando...';
            generateBtn.classList.add('loading');
            
            // Show loading modal
            loadingModal.show();
            
            // Add a small delay to ensure the modal shows before form submission
            setTimeout(() => {
                // The form will submit normally
            }, 100);
        });
    }

    // Hide loading modal if page is reloaded with a phrase (successful generation)
    if (document.querySelector('.phrase-result')) {
        // If there's a phrase result, hide the loading modal
        if (loadingModal) {
            loadingModal.hide();
        }
        
        // Reset button state
        if (generateBtn) {
            generateBtn.disabled = false;
            generateBtn.innerHTML = '<i class="fas fa-magic me-2"></i>Crear mi frase';
            generateBtn.classList.remove('loading');
        }
    }

    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.classList.remove('show');
            setTimeout(() => alert.remove(), 150);
        }, 5000);
    });

    // Delete confirmation
    window.deletePhrase = function(phraseId) {
        const deleteFormElement = document.getElementById('deleteForm');
        if (deleteFormElement) {
            deleteFormElement.action = `/delete/${phraseId}`;
            deleteModal.show();
        }
    };
});

// Copy to clipboard functionality
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(function() {
        showToast('Frase copiada al portapapeles', 'success');
    }, function(err) {
        console.error('Error al copiar: ', err);
        showToast('Error al copiar la frase', 'error');
    });
}

// Share functionality
function sharePhrase(text) {
    if (navigator.share) {
        navigator.share({
            title: 'Entrelíneas',
            text: text,
            url: window.location.origin
        }).then(() => {
            showToast('Frase compartida exitosamente', 'success');
        }).catch((error) => {
            console.log('Error sharing:', error);
            copyToClipboard(text);
        });
    } else {
        copyToClipboard(text);
    }
}

// Toggle favorite status
function toggleFavorite(phraseId) {
    const favoriteBtn = document.getElementById(`favoriteBtn${phraseId}`) || document.getElementById('favoriteBtn');
    
    fetch(`/favorite/${phraseId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            if (favoriteBtn) {
                if (data.is_favorite) {
                    favoriteBtn.classList.remove('btn-outline-secondary');
                    favoriteBtn.classList.add('btn-outline-danger');
                    favoriteBtn.innerHTML = '<i class="fas fa-heart"></i>';
                } else {
                    favoriteBtn.classList.remove('btn-outline-danger');
                    favoriteBtn.classList.add('btn-outline-secondary');
                    favoriteBtn.innerHTML = '<i class="far fa-heart"></i>';
                }
            }
            showToast(data.is_favorite ? 'Frase añadida a favoritos' : 'Frase removida de favoritos', 'success');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('Error al actualizar favoritos', 'error');
    });
}

// Show toast notification
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `alert alert-${type === 'error' ? 'danger' : 'success'} alert-dismissible fade show position-fixed`;
    toast.style.cssText = 'top: 100px; right: 20px; z-index: 1055; min-width: 300px;';
    toast.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 150);
    }, 3000);
}

// Smooth scrolling for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Add subtle animations on scroll
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, observerOptions);

// Observe elements for animation
document.querySelectorAll('.style-card, .phrase-collection-card').forEach(el => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(20px)';
    el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
    observer.observe(el);
});
