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
            generateBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Creando...';
            generateBtn.classList.add('loading');
            
            // Show loading modal
            loadingModal.show();
        });
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
