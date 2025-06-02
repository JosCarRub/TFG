document.addEventListener('DOMContentLoaded', function() {
    // Inicializar funcionalidades
    initializeFormValidation();
    initializeFileUpload();
    initializePreview();
    initializeFormSubmission();
    initializeAnimations();
});

// ======= Validación del Formulario =======
function initializeFormValidation() {
    const form = document.querySelector('.equipo-form');
    const inputs = form.querySelectorAll('input, textarea, select');
    
    inputs.forEach(input => {
        // Validación en tiempo real
        input.addEventListener('input', function() {
            validateField(this);
            updatePreview();
        });
        
        input.addEventListener('blur', function() {
            validateField(this);
        });
        
        // Para campos de color, también escuchar el evento change
        if (input.type === 'color') {
            input.addEventListener('change', function() {
                validateField(this);
                updatePreview();
            });
        }
    });
}

function validateField(field) {
    const fieldContainer = field.closest('.form-field');
    const isRequired = field.hasAttribute('required');
    const value = field.value.trim();
    
    // Remover clases de validación previas
    field.classList.remove('is-valid', 'is-invalid');
    
    // Validación básica de campos requeridos
    if (isRequired && !value) {
        field.classList.add('is-invalid');
        showFieldError(fieldContainer, 'Este campo es obligatorio.');
        return false;
    }
    
    // Validaciones específicas por tipo de campo
    if (field.name === 'nombre' && value) {
        if (value.length < 3) {
            field.classList.add('is-invalid');
            showFieldError(fieldContainer, 'El nombre debe tener al menos 3 caracteres.');
            return false;
        }
        if (value.length > 50) {
            field.classList.add('is-invalid');
            showFieldError(fieldContainer, 'El nombre no puede exceder 50 caracteres.');
            return false;
        }
    }
    
    if (field.name === 'descripcion' && value && value.length > 500) {
        field.classList.add('is-invalid');
        showFieldError(fieldContainer, 'La descripción no puede exceder 500 caracteres.');
        return false;
    }
    
    // Si llegamos aquí, el campo es válido
    if (value || !isRequired) {
        field.classList.add('is-valid');
        clearFieldError(fieldContainer);
        return true;
    }
    
    return true;
}

function showFieldError(container, message) {
    clearFieldError(container);
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'field-errors';
    errorDiv.innerHTML = `<small class="error-text">${message}</small>`;
    
    container.appendChild(errorDiv);
}

function clearFieldError(container) {
    const existingError = container.querySelector('.field-errors');
    if (existingError) {
        existingError.remove();
    }
}

// ======= Upload de Archivo =======
function initializeFileUpload() {
    const fileInput = document.querySelector('input[type="file"]');
    const preview = document.getElementById('escudo-preview');
    
    if (!fileInput || !preview) return;
    
    fileInput.addEventListener('change', function(e) {
        const file = e.target.files[0];
        
        if (file) {
            // Validar tipo de archivo
            if (!file.type.startsWith('image/')) {
                showUploadError('Por favor selecciona un archivo de imagen válido.');
                return;
            }
            
            // Validar tamaño (máximo 5MB)
            if (file.size > 5 * 1024 * 1024) {
                showUploadError('El archivo es demasiado grande. Máximo 5MB.');
                return;
            }
            
            // Mostrar preview
            const reader = new FileReader();
            reader.onload = function(e) {
                showImagePreview(e.target.result);
                updatePreview(e.target.result);
            };
            reader.readAsDataURL(file);
        }
    });
    
    // Efectos de drag and drop
    preview.addEventListener('dragover', function(e) {
        e.preventDefault();
        this.style.borderColor = '#a855f7';
        this.style.backgroundColor = 'rgba(168, 85, 247, 0.2)';
    });
    
    preview.addEventListener('dragleave', function(e) {
        e.preventDefault();
        this.style.borderColor = '#8b5cf6';
        this.style.backgroundColor = 'rgba(139, 92, 246, 0.1)';
    });
    
    preview.addEventListener('drop', function(e) {
        e.preventDefault();
        this.style.borderColor = '#8b5cf6';
        this.style.backgroundColor = 'rgba(139, 92, 246, 0.1)';
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            fileInput.files = files;
            fileInput.dispatchEvent(new Event('change'));
        }
    });
}

function showImagePreview(src) {
    const preview = document.getElementById('escudo-preview');
    preview.innerHTML = `<img src="${src}" alt="Preview del escudo">`;
    preview.classList.add('has-image');
}

function showUploadError(message) {
    const preview = document.getElementById('escudo-preview');
    const errorDiv = document.createElement('div');
    errorDiv.className = 'upload-error';
    errorDiv.style.cssText = `
        position: absolute;
        top: 100%;
        left: 0;
        right: 0;
        background: rgba(239, 68, 68, 0.1);
        border: 1px solid rgba(239, 68, 68, 0.3);
        color: #fca5a5;
        padding: 0.5rem;
        border-radius: 8px;
        font-size: 0.85rem;
        margin-top: 0.5rem;
    `;
    errorDiv.textContent = message;
    
    // Remover error anterior si existe
    const existingError = preview.parentNode.querySelector('.upload-error');
    if (existingError) {
        existingError.remove();
    }
    
    preview.parentNode.appendChild(errorDiv);
    
    // Remover error después de 5 segundos
    setTimeout(() => {
        if (errorDiv.parentNode) {
            errorDiv.remove();
        }
    }, 5000);
}

// ======= Vista Previa del Equipo =======
function initializePreview() {
    // Actualizar preview inicial
    updatePreview();
}

function updatePreview(escudoSrc = null) {
    const nombreInput = document.querySelector('input[name="nombre"]');
    const descripcionInput = document.querySelector('textarea[name="descripcion"]');
    const colorPrimarioInput = document.querySelector('input[name="color_primario"]');
    const colorSecundarioInput = document.querySelector('input[name="color_secundario"]');
    
    const previewName = document.querySelector('.preview-name');
    const previewDescription = document.querySelector('.preview-description');
    const previewShield = document.querySelector('.preview-shield');
    const primaryColorSample = document.querySelector('.primary-color');
    const secondaryColorSample = document.querySelector('.secondary-color');
    
    // Actualizar nombre
    if (nombreInput && previewName) {
        const nombre = nombreInput.value.trim() || 'Nombre del Equipo';
        previewName.textContent = nombre;
    }
    
    // Actualizar descripción
    if (descripcionInput && previewDescription) {
        const descripcion = descripcionInput.value.trim() || 'Descripción del equipo';
        previewDescription.textContent = descripcion;
    }
    
    // Actualizar escudo
    if (previewShield) {
        if (escudoSrc) {
            previewShield.innerHTML = `<img src="${escudoSrc}" alt="Escudo del equipo">`;
        } else {
            previewShield.innerHTML = '<i class="fas fa-shield-alt"></i>';
        }
    }
    
    // Actualizar colores
    if (colorPrimarioInput && primaryColorSample) {
        const colorPrimario = colorPrimarioInput.value || '#8b5cf6';
        primaryColorSample.style.backgroundColor = colorPrimario;
        
        // Actualizar también el escudo si no hay imagen
        if (previewShield && !previewShield.querySelector('img')) {
            previewShield.style.background = `linear-gradient(135deg, ${colorPrimario}, ${colorSecundarioInput?.value || '#a855f7'})`;
        }
    }
    
    if (colorSecundarioInput && secondaryColorSample) {
        const colorSecundario = colorSecundarioInput.value || '#a855f7';
        secondaryColorSample.style.backgroundColor = colorSecundario;
    }
    
    // Agregar efecto de actualización
    const previewCard = document.querySelector('.team-preview-card');
    if (previewCard) {
        previewCard.style.transform = 'scale(1.02)';
        setTimeout(() => {
            previewCard.style.transform = 'scale(1)';
        }, 200);
    }
}

// ======= Envío del Formulario =======
function initializeFormSubmission() {
    const form = document.querySelector('.equipo-form');
    const submitBtn = document.querySelector('.btn-submit');
    
    if (!form || !submitBtn) return;
    
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Validar todos los campos antes del envío
        if (validateForm()) {
            showLoadingState(submitBtn);
            
            // Simular delay para mostrar loading (remover en producción)
            setTimeout(() => {
                form.submit();
            }, 1000);
        }
    });
}

function validateForm() {
    const form = document.querySelector('.equipo-form');
    const inputs = form.querySelectorAll('input[required], textarea[required], select[required]');
    let isValid = true;
    
    inputs.forEach(input => {
        if (!validateField(input)) {
            isValid = false;
        }
    });
    
    if (!isValid) {
        // Scroll al primer error
        const firstError = form.querySelector('.is-invalid');
        if (firstError) {
            firstError.scrollIntoView({ 
                behavior: 'smooth', 
                block: 'center' 
            });
            firstError.focus();
        }
        
        showFormError('Por favor corrige los errores antes de continuar.');
    }
    
    return isValid;
}

function showLoadingState(button) {
    button.classList.add('loading');
    button.disabled = true;
}

function hideLoadingState(button) {
    button.classList.remove('loading');
    button.disabled = false;
}

function showFormError(message) {
    // Remover error anterior si existe
    const existingError = document.querySelector('.form-error-alert');
    if (existingError) {
        existingError.remove();
    }
    
    const errorAlert = document.createElement('div');
    errorAlert.className = 'alert alert-danger form-error-alert';
    errorAlert.innerHTML = `
        <i class="fas fa-exclamation-triangle me-2"></i>
        ${message}
    `;
    
    const form = document.querySelector('.equipo-form');
    form.insertBefore(errorAlert, form.firstChild);
    
    // Scroll al error
    errorAlert.scrollIntoView({ 
        behavior: 'smooth', 
        block: 'center' 
    });
    
    // Remover después de 5 segundos
    setTimeout(() => {
        if (errorAlert.parentNode) {
            errorAlert.remove();
        }
    }, 5000);
}

// ======= Animaciones =======
function initializeAnimations() {
    // Intersection Observer para animaciones al hacer scroll
    if ('IntersectionObserver' in window) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.animationPlayState = 'running';
                }
            });
        }, {
            threshold: 0.1,
            rootMargin: '50px'
        });

        // Observar elementos con animaciones
        document.querySelectorAll('.form-section, .preview-section, .form-actions').forEach(el => {
            observer.observe(el);
        });
    }
    
    // Agregar efectos hover mejorados
    addAdvancedHoverEffects();
}

function addAdvancedHoverEffects() {
    // Efectos para las secciones del formulario
    document.querySelectorAll('.form-section').forEach(section => {
        section.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-4px) scale(1.01)';
        });
        
        section.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });
    
    // Efectos para los campos de color
    document.querySelectorAll('input[type="color"]').forEach(colorInput => {
        colorInput.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.1) rotate(5deg)';
        });
        
        colorInput.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1) rotate(0deg)';
        });
    });
    
    // Efecto parallax sutil para el header icon
    const headerIcon = document.querySelector('.header-icon');
    if (headerIcon) {
        document.addEventListener('mousemove', function(e) {
            const rect = headerIcon.getBoundingClientRect();
            const centerX = rect.left + rect.width / 2;
            const centerY = rect.top + rect.height / 2;
            
            const deltaX = (e.clientX - centerX) * 0.05;
            const deltaY = (e.clientY - centerY) * 0.05;
            
            headerIcon.style.transform = `translate(${deltaX}px, ${deltaY}px) scale(1.05)`;
        });
        
        document.addEventListener('mouseleave', function() {
            headerIcon.style.transform = 'translate(0px, 0px) scale(1)';
        });
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

// ======= Event Listeners Adicionales =======
document.addEventListener('DOMContentLoaded', function() {
    // Auto-resize para textarea
    const textareas = document.querySelectorAll('textarea');
    textareas.forEach(textarea => {
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = this.scrollHeight + 'px';
        });
    });
    
    // Contador de caracteres para campos con límite
    const nombreInput = document.querySelector('input[name="nombre"]');
    const descripcionTextarea = document.querySelector('textarea[name="descripcion"]');
    
    if (nombreInput) {
        addCharacterCounter(nombreInput, 50);
    }
    
    if (descripcionTextarea) {
        addCharacterCounter(descripcionTextarea, 500);
    }
});

function addCharacterCounter(element, maxLength) {
    const counter = document.createElement('div');
    counter.className = 'character-counter';
    counter.style.cssText = `
        text-align: right;
        font-size: 0.8rem;
        color: #94a3b8;
        margin-top: 0.25rem;
    `;
    
    const updateCounter = () => {
        const current = element.value.length;
        counter.textContent = `${current}/${maxLength}`;
        
        if (current > maxLength * 0.9) {
            counter.style.color = '#f59e0b';
        } else if (current > maxLength) {
            counter.style.color = '#ef4444';
        } else {
            counter.style.color = '#94a3b8';
        }
    };
    
    element.addEventListener('input', updateCounter);
    element.parentNode.appendChild(counter);
    updateCounter();
}

// ======= Función de Debug =======
function debugForm() {
    console.log('=== Debug Crear Equipo ===');
    const form = document.querySelector('.equipo-form');
    const formData = new FormData(form);
    
    console.log('Datos del formulario:');
    for (let [key, value] of formData.entries()) {
        console.log(`${key}:`, value);
    }
    
    console.log('Estado de validación:');
    const inputs = form.querySelectorAll('input, textarea, select');
    inputs.forEach(input => {
        console.log(`${input.name}:`, {
            value: input.value,
            valid: input.classList.contains('is-valid'),
            invalid: input.classList.contains('is-invalid')
        });
    });
}

// Hacer disponible globalmente para debugging
window.debugForm = debugForm;