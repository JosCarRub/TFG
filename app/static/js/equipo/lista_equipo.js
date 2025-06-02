document.addEventListener('DOMContentLoaded', function() {
    // Inicializar funcionalidades
    initializeAnimations();
    initializeCardInteractions();
    initializeDeleteConfirmation();
    initializeTooltips();
    initializeSearch();
    initializeStatistics();
});

// ======= Animaciones y Efectos Visuales =======
function initializeAnimations() {
    // Intersection Observer para animaciones al hacer scroll
    if ('IntersectionObserver' in window) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-in');
                    // Animar contador de estadísticas
                    if (entry.target.classList.contains('stat-card')) {
                        animateStatNumber(entry.target);
                    }
                }
            });
        }, {
            threshold: 0.1,
            rootMargin: '50px'
        });

        // Observar elementos
        document.querySelectorAll('.equipo-card, .stat-card, .empty-state').forEach(el => {
            observer.observe(el);
        });
    }
    
    // Efectos hover mejorados
    addAdvancedHoverEffects();
}

function addAdvancedHoverEffects() {
    // Efecto parallax sutil en las cards
    document.querySelectorAll('.equipo-card').forEach(card => {
        card.addEventListener('mousemove', function(e) {
            const rect = this.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            
            const rotateX = (y - centerY) / 20;
            const rotateY = (centerX - x) / 20;
            
            this.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-4px)`;
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg) translateY(0px)';
        });
    });
    
    // Efecto de ondas en los botones
    document.querySelectorAll('.btn').forEach(button => {
        button.addEventListener('click', function(e) {
            createRippleEffect(e, this);
        });
    });
}

function createRippleEffect(event, element) {
    const button = element;
    const circle = document.createElement('span');
    const diameter = Math.max(button.clientWidth, button.clientHeight);
    const radius = diameter / 2;
    
    const rect = button.getBoundingClientRect();
    circle.style.width = circle.style.height = `${diameter}px`;
    circle.style.left = `${event.clientX - rect.left - radius}px`;
    circle.style.top = `${event.clientY - rect.top - radius}px`;
    circle.classList.add('ripple');
    
    // Agregar estilos del ripple
    circle.style.cssText += `
        position: absolute;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.6);
        transform: scale(0);
        animation: ripple 600ms linear;
        pointer-events: none;
    `;
    
    // Agregar keyframes si no existen
    if (!document.querySelector('#ripple-styles')) {
        const style = document.createElement('style');
        style.id = 'ripple-styles';
        style.textContent = `
            @keyframes ripple {
                to {
                    transform: scale(4);
                    opacity: 0;
                }
            }
        `;
        document.head.appendChild(style);
    }
    
    const ripple = button.getElementsByClassName('ripple')[0];
    if (ripple) {
        ripple.remove();
    }
    
    button.style.position = 'relative';
    button.style.overflow = 'hidden';
    button.appendChild(circle);
    
    setTimeout(() => {
        circle.remove();
    }, 600);
}

function animateStatNumber(statCard) {
    const numberElement = statCard.querySelector('.stat-number');
    if (!numberElement) return;
    
    const targetValue = parseInt(numberElement.textContent) || 0;
    if (targetValue === 0) return;
    
    let currentValue = 0;
    const increment = targetValue / 30; // Duración de la animación
    const timer = setInterval(() => {
        currentValue += increment;
        if (currentValue >= targetValue) {
            currentValue = targetValue;
            clearInterval(timer);
        }
        numberElement.textContent = Math.floor(currentValue);
    }, 50);
}

// ======= Interacciones de las Cards =======
function initializeCardInteractions() {
    // Click en las cards para expandir información
    document.querySelectorAll('.equipo-card').forEach(card => {
        // Prevenir que el click en acciones active el card
        const actions = card.querySelectorAll('.equipo-actions button, .equipo-actions a');
        actions.forEach(action => {
            action.addEventListener('click', function(e) {
                e.stopPropagation();
            });
        });
        
        // Doble click para ir a detalles
        card.addEventListener('dblclick', function() {
            const viewButton = this.querySelector('.btn-view');
            if (viewButton) {
                viewButton.click();
            }
        });
        
        // Keyboard navigation
        card.setAttribute('tabindex', '0');
        card.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                const viewButton = this.querySelector('.btn-view');
                if (viewButton) {
                    viewButton.click();
                }
            }
        });
    });
    
    // Lazy loading de imágenes
    initializeLazyLoading();
}

function initializeLazyLoading() {
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    if (img.dataset.src) {
                        img.src = img.dataset.src;
                        img.removeAttribute('data-src');
                        imageObserver.unobserve(img);
                        
                        // Efecto de fade in
                        img.style.opacity = '0';
                        img.onload = () => {
                            img.style.transition = 'opacity 0.3s ease';
                            img.style.opacity = '1';
                        };
                    }
                }
            });
        });
        
        document.querySelectorAll('img[data-src]').forEach(img => {
            imageObserver.observe(img);
        });
    }
}

// ======= Confirmación de Eliminación =======
function initializeDeleteConfirmation() {
    // Manejar el modal de confirmación
    const modal = document.getElementById('confirmDeleteModal');
    const confirmBtn = document.getElementById('confirmDeleteBtn');
    const teamNameSpan = document.getElementById('teamNameToDelete');
    
    let teamIdToDelete = null;
    
    // Función global para abrir el modal
    window.confirmDelete = function(teamName, teamId) {
        teamNameSpan.textContent = teamName;
        teamIdToDelete = teamId;
        
        // Mostrar el modal
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
    };
    
    // Confirmar eliminación
    if (confirmBtn) {
        confirmBtn.addEventListener('click', function() {
            if (teamIdToDelete) {
                deleteTeam(teamIdToDelete);
            }
        });
    }
}

function deleteTeam(teamId) {
    // Mostrar estado de loading
    const confirmBtn = document.getElementById('confirmDeleteBtn');
    const originalText = confirmBtn.innerHTML;
    confirmBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Eliminando...';
    confirmBtn.disabled = true;
    
    // Simulación de petición AJAX (adaptar según tu backend)
    fetch(`/equipos/${teamId}/delete/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCsrfToken(),
            'Content-Type': 'application/json',
        },
    })
    .then(response => {
        if (response.ok) {
            // Éxito: animar la eliminación de la card
            const card = document.querySelector(`[data-equipo-id="${teamId}"]`);
            if (card) {
                card.style.transition = 'all 0.3s ease';
                card.style.transform = 'scale(0)';
                card.style.opacity = '0';
                
                setTimeout(() => {
                    card.remove();
                    updateStatistics();
                    checkEmptyState();
                }, 300);
            }
            
            // Cerrar modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('confirmDeleteModal'));
            modal.hide();
            
            showNotification('Equipo eliminado correctamente', 'success');
        } else {
            throw new Error('Error al eliminar el equipo');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Error al eliminar el equipo', 'error');
    })
    .finally(() => {
        // Restaurar botón
        confirmBtn.innerHTML = originalText;
        confirmBtn.disabled = false;
    });
}

function getCsrfToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
           document.querySelector('meta[name=csrf-token]')?.getAttribute('content');
}

// ======= Notificaciones =======
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <i class="fas fa-${getNotificationIcon(type)} me-2"></i>
        ${message}
        <button class="notification-close" onclick="this.parentElement.remove()">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${getNotificationColor(type)};
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        z-index: 1050;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-weight: 500;
        max-width: 400px;
        animation: slideInRight 0.3s ease;
    `;
    
    // Agregar estilos de animación
    if (!document.querySelector('#notification-styles')) {
        const style = document.createElement('style');
        style.id = 'notification-styles';
        style.textContent = `
            @keyframes slideInRight {
                from {
                    transform: translateX(100%);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }
            .notification-close {
                background: none;
                border: none;
                color: white;
                cursor: pointer;
                padding: 0.25rem;
                margin-left: auto;
                opacity: 0.7;
                transition: opacity 0.2s ease;
            }
            .notification-close:hover {
                opacity: 1;
            }
        `;
        document.head.appendChild(style);
    }
    
    document.body.appendChild(notification);
    
    // Auto-remove después de 5 segundos
    setTimeout(() => {
        if (notification.parentNode) {
            notification.style.animation = 'slideInRight 0.3s ease reverse';
            setTimeout(() => notification.remove(), 300);
        }
    }, 5000);
}

function getNotificationIcon(type) {
    const icons = {
        success: 'check-circle',
        error: 'exclamation-triangle',
        warning: 'exclamation-circle',
        info: 'info-circle'
    };
    return icons[type] || 'info-circle';
}

function getNotificationColor(type) {
    const colors = {
        success: '#10b981',
        error: '#ef4444',
        warning: '#f59e0b',
        info: '#3b82f6'
    };
    return colors[type] || '#3b82f6';
}

// ======= Tooltips =======
function initializeTooltips() {
    // Inicializar tooltips de Bootstrap si está disponible
    if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
    
    // Tooltips personalizados para elementos específicos
    addCustomTooltips();
}

function addCustomTooltips() {
    // Agregar tooltips a los badges de capitán
    document.querySelectorAll('.equipo-badge').forEach(badge => {
        badge.setAttribute('title', 'Eres el capitán de este equipo');
    });
    
    // Agregar tooltips a los indicadores de actividad
    document.querySelectorAll('.activity-indicator.active').forEach(indicator => {
        indicator.setAttribute('title', 'Equipo activo');
    });
    
    // Agregar tooltips a los botones de menú
    document.querySelectorAll('.btn-menu').forEach(btn => {
        btn.setAttribute('title', 'Opciones del equipo');
    });
}

// ======= Búsqueda y Filtrado =======
function initializeSearch() {
    // Preparar para futuras funcionalidades de búsqueda
    const searchInput = document.querySelector('.search-input');
    if (searchInput) {
        searchInput.addEventListener('input', debounce(function() {
            filterTeams(this.value);
        }, 300));
    }
}

function filterTeams(searchTerm) {
    const cards = document.querySelectorAll('.equipo-card');
    const term = searchTerm.toLowerCase();
    
    cards.forEach(card => {
        const teamName = card.querySelector('.equipo-name').textContent.toLowerCase();
        const teamDesc = card.querySelector('.equipo-description').textContent.toLowerCase();
        const captain = card.querySelector('.stat-value').textContent.toLowerCase();
        
        const matches = teamName.includes(term) || 
                       teamDesc.includes(term) || 
                       captain.includes(term);
        
        if (matches) {
            card.style.display = 'block';
            card.style.animation = 'fadeInUp 0.3s ease';
        } else {
            card.style.display = 'none';
        }
    });
    
    updateStatistics();
}

// ======= Estadísticas =======
function initializeStatistics() {
    updateStatistics();
}

function updateStatistics() {
    const visibleCards = document.querySelectorAll('.equipo-card:not([style*="display: none"])');
    const totalTeams = visibleCards.length;
    
    // Actualizar contador de equipos
    const teamCountElement = document.querySelector('.stat-card .stat-number');
    if (teamCountElement) {
        teamCountElement.textContent = totalTeams;
    }
    
    // Calcular otras estadísticas si es necesario
    // Por ejemplo: equipos donde es capitán, partidos jugados, etc.
}

function checkEmptyState() {
    const cards = document.querySelectorAll('.equipo-card');
    const emptyState = document.querySelector('.empty-state');
    const equiposSection = document.querySelector('.equipos-section');
    
    if (cards.length === 0) {
        if (equiposSection) equiposSection.style.display = 'none';
        if (emptyState) emptyState.style.display = 'flex';
    } else {
        if (equiposSection) equiposSection.style.display = 'block';
        if (emptyState) emptyState.style.display = 'none';
    }
}

// ======= Utilidades =======
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// ======= Manejo de Errores =======
window.addEventListener('error', function(e) {
    console.error('Error en lista de equipos:', e.error);
    // Opcional: mostrar notificación de error al usuario
});

// ======= Funciones de Debug =======
function debugTeamsList() {
    console.log('=== Debug Lista de Equipos ===');
    console.log('Equipos encontrados:', document.querySelectorAll('.equipo-card').length);
    console.log('Estadísticas visibles:', document.querySelectorAll('.stat-card').length);
    console.log('Estado vacío visible:', document.querySelector('.empty-state')?.style.display !== 'none');
    
    // Información de cada equipo
    document.querySelectorAll('.equipo-card').forEach((card, index) => {
        const teamName = card.querySelector('.equipo-name')?.textContent;
        const teamId = card.getAttribute('data-equipo-id');
        console.log(`Equipo ${index + 1}:`, { name: teamName, id: teamId });
    });
}

// ======= Atajos de Teclado =======
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + N para crear nuevo equipo
    if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
        e.preventDefault();
        const createButton = document.querySelector('.btn-create, .btn-create-first');
        if (createButton) {
            createButton.click();
        }
    }
    
    // Escape para cerrar modales
    if (e.key === 'Escape') {
        const openModal = document.querySelector('.modal.show');
        if (openModal) {
            const modalInstance = bootstrap.Modal.getInstance(openModal);
            if (modalInstance) {
                modalInstance.hide();
            }
        }
    }
    
    // Flecha derecha/izquierda para navegación entre equipos
    if (e.key === 'ArrowRight' || e.key === 'ArrowLeft') {
        navigateTeams(e.key === 'ArrowRight');
    }
});

function navigateTeams(forward = true) {
    const cards = document.querySelectorAll('.equipo-card');
    const focusedCard = document.querySelector('.equipo-card:focus');
    
    if (cards.length === 0) return;
    
    let currentIndex = -1;
    if (focusedCard) {
        currentIndex = Array.from(cards).indexOf(focusedCard);
    }
    
    let nextIndex;
    if (forward) {
        nextIndex = currentIndex + 1 >= cards.length ? 0 : currentIndex + 1;
    } else {
        nextIndex = currentIndex - 1 < 0 ? cards.length - 1 : currentIndex - 1;
    }
    
    cards[nextIndex].focus();
    cards[nextIndex].scrollIntoView({ behavior: 'smooth', block: 'center' });
}

// ======= Gestión de Favoritos (Futuro) =======
function toggleFavorite(teamId) {
    const card = document.querySelector(`[data-equipo-id="${teamId}"]`);
    if (!card) return;
    
    const favoriteBtn = card.querySelector('.favorite-btn');
    if (!favoriteBtn) return;
    
    const isFavorite = favoriteBtn.classList.contains('active');
    
    // Simulación de petición al servidor
    fetch(`/equipos/${teamId}/favorite/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCsrfToken(),
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ favorite: !isFavorite })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            favoriteBtn.classList.toggle('active');
            const icon = favoriteBtn.querySelector('i');
            if (favoriteBtn.classList.contains('active')) {
                icon.className = 'fas fa-heart';
                showNotification('Equipo añadido a favoritos', 'success');
            } else {
                icon.className = 'far fa-heart';
                showNotification('Equipo removido de favoritos', 'info');
            }
        }
    })
    .catch(error => {
        console.error('Error al actualizar favorito:', error);
        showNotification('Error al actualizar favorito', 'error');
    });
}

// ======= Exportación de Datos =======
function exportTeamsData() {
    const teams = [];
    
    document.querySelectorAll('.equipo-card').forEach(card => {
        const teamData = {
            id: card.getAttribute('data-equipo-id'),
            name: card.querySelector('.equipo-name')?.textContent,
            description: card.querySelector('.equipo-description')?.textContent,
            captain: card.querySelector('.stat-value')?.textContent,
            players: card.querySelectorAll('.stat-item')[1]?.querySelector('.stat-value')?.textContent,
            created: card.querySelectorAll('.stat-item')[2]?.querySelector('.stat-value')?.textContent
        };
        teams.push(teamData);
    });
    
    // Crear y descargar archivo CSV
    const csv = convertToCSV(teams);
    downloadCSV(csv, 'mis_equipos.csv');
}

function convertToCSV(data) {
    if (!data.length) return '';
    
    const headers = Object.keys(data[0]);
    const csvContent = [
        headers.join(','),
        ...data.map(row => headers.map(header => `"${row[header] || ''}"`).join(','))
    ].join('\n');
    
    return csvContent;
}

function downloadCSV(csvContent, filename) {
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    
    if (link.download !== undefined) {
        const url = URL.createObjectURL(blob);
        link.setAttribute('href', url);
        link.setAttribute('download', filename);
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
}

// ======= Compartir Equipo =======
function shareTeam(teamId, teamName) {
    if (navigator.share) {
        // API nativa de compartir (móviles)
        navigator.share({
            title: `Equipo ${teamName}`,
            text: `Únete a mi equipo "${teamName}" en De Rabona`,
            url: `${window.location.origin}/equipos/${teamId}/`
        }).catch(err => console.log('Error al compartir:', err));
    } else {
        // Fallback: copiar al portapapeles
        const url = `${window.location.origin}/equipos/${teamId}/`;
        copyToClipboard(url);
        showNotification('Enlace copiado al portapapeles', 'success');
    }
}

function copyToClipboard(text) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text);
    } else {
        // Fallback para navegadores antiguos
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        try {
            document.execCommand('copy');
        } catch (err) {
            console.error('Error al copiar:', err);
        }
        document.body.removeChild(textArea);
    }
}

// ======= Gestión de Temas (Dark/Light) =======
function initializeThemeToggle() {
    const themeToggle = document.querySelector('.theme-toggle');
    if (!themeToggle) return;
    
    // Leer preferencia guardada
    const savedTheme = localStorage.getItem('theme') || 'dark';
    document.body.setAttribute('data-theme', savedTheme);
    
    themeToggle.addEventListener('click', function() {
        const currentTheme = document.body.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        
        document.body.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        
        // Animar el cambio
        document.body.style.transition = 'all 0.3s ease';
        setTimeout(() => {
            document.body.style.transition = '';
        }, 300);
    });
}

// ======= Monitoreo de Performance =======
function initializePerformanceMonitoring() {
    // Medir tiempo de carga de las cards
    const startTime = performance.now();
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const endTime = performance.now();
                console.log(`Card cargada en ${endTime - startTime}ms`);
            }
        });
    });
    
    document.querySelectorAll('.equipo-card').forEach(card => {
        observer.observe(card);
    });
    
    // Medir el tiempo total de renderizado
    window.addEventListener('load', function() {
        const loadTime = performance.now();
        console.log(`Página cargada completamente en ${loadTime}ms`);
    });
}

// ======= Auto-refresh (opcional) =======
function initializeAutoRefresh(intervalMinutes = 5) {
    // Opcional: auto-refresh cada X minutos para datos actualizados
    if (typeof intervalMinutes !== 'number' || intervalMinutes < 1) return;
    
    setInterval(() => {
        // Solo hacer refresh si la página está visible
        if (!document.hidden) {
            refreshTeamData();
        }
    }, intervalMinutes * 60 * 1000);
}

function refreshTeamData() {
    fetch(window.location.href, {
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.text())
    .then(html => {
        // Actualizar solo la sección de equipos
        const parser = new DOMParser();
        const newDoc = parser.parseFromString(html, 'text/html');
        const newEquiposSection = newDoc.querySelector('.equipos-section');
        const currentEquiposSection = document.querySelector('.equipos-section');
        
        if (newEquiposSection && currentEquiposSection) {
            currentEquiposSection.innerHTML = newEquiposSection.innerHTML;
            // Reinicializar funcionalidades para los nuevos elementos
            initializeCardInteractions();
            showNotification('Datos actualizados', 'info');
        }
    })
    .catch(error => {
        console.error('Error al actualizar datos:', error);
    });
}

// ======= Funciones de Inicialización Avanzada =======
function initializeAdvancedFeatures() {
    // Estas funciones se pueden activar según las necesidades
    // initializeThemeToggle();
    // initializePerformanceMonitoring();
    // initializeAutoRefresh(5); // Auto-refresh cada 5 minutos
}

// ======= Event Listeners Globales =======
document.addEventListener('visibilitychange', function() {
    if (!document.hidden) {
        // La página volvió a ser visible, actualizar datos si es necesario
        updateStatistics();
    }
});

// ======= Funciones Públicas para uso global =======
window.teamsList = {
    deleteTeam,
    shareTeam,
    toggleFavorite,
    exportTeamsData,
    refreshTeamData,
    debugTeamsList
};

// Hacer disponible globalmente para debugging
window.debugTeamsList = debugTeamsList;

// ======= Inicialización Final =======
// Ejecutar funciones adicionales cuando el DOM esté completamente cargado
document.addEventListener('DOMContentLoaded', function() {
    // Pequeño delay para asegurar que Bootstrap esté inicializado
    setTimeout(() => {
        checkEmptyState();
        initializeAdvancedFeatures();
    }, 100);
});

// ======= Service Worker para caching (opcional) =======
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        navigator.serviceWorker.register('/sw.js')
            .then(function(registration) {
                console.log('SW registrado:', registration.scope);
            }, function(err) {
                console.log('SW falló:', err);
            });
    });
}