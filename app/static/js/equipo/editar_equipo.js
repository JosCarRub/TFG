document.addEventListener('DOMContentLoaded', function() {
    // Inicializar funcionalidades
    initializeFormValidation();
    initializeFileUpload();
    initializePreview();
    initializeFormSubmission();
    initializeAnimations();
    initializeChangeTracking();
});

// ======= Seguimiento de Cambios =======
let originalValues = {};
let hasChanges = false;

function initializeChangeTracking() {
    const form = document.querySelector('.equipo-form');
    const inputs = form.querySelectorAll('input, textarea, select');
    
    // Guardar valores originales
    inputs.forEach(input => {
        if (input.type !== 'file') {
            originalValues[input.name] = input.value;
        }
    });
    
    // Escuchar cambios
    inputs.forEach(input => {
        input.addEventListener('input', function() {
            trackChanges();
            updatePreview();
        });
        
        if (input.type === 'color') {
            input.addEventListener('change', function() {
                trackChanges();
                updatePreview();
                updateColorPreview(this);
            });
        }
    });
    
    // Advertir antes de salir si hay cambios
    window.addEventListener('beforeunload', function(e) {
        if (hasChanges) {
            e.preventDefault();
            e.returnValue = '¿Estás seguro de que quieres salir? Los cambios no guardados se perderán.';
            return e.returnValue;
        }
    });
}

function trackChanges() {
    const form = document.querySelector('.equipo-form');
    const inputs = form.querySelectorAll('input, textarea, select');
    hasChanges = false;
    
    inputs.forEach(input => {
        if (input.type === 'file') {
            if (input.files.length > 0) {
                hasChanges = true;
                markFieldAsChanged(input);
            }
        } else if (originalValues[input.name] !== input.value) {
            hasChanges = true;
            markFieldAsChanged(input);
        } else {
            unmarkFieldAsChanged(input);
        }
    });
    
    // Actualizar botón de guardar
    updateSaveButton();
}

function markFieldAsChanged(field) {
    const fieldContainer = field.closest('.form-field');
    if (fieldContainer && !fieldContainer.classList.contains('field-changed')) {
        fieldContainer.classList.add('field-changed');
        
        // Agregar indicador visual
        if (!fieldContainer.querySelector('.change-indicator')) {
            const indicator = document.createElement('div');
            indicator.className = 'change-indicator';
            indicator.title = 'Campo modificado';
            fieldContainer.appendChild(indicator);
        }
    }
}

function unmarkFieldAsChanged(field) {
    const fieldContainer = field.closest('.form-field');
    if (fieldContainer) {
        fieldContainer.classList.remove('field-changed');
        const indicator = fieldContainer.querySelector('.change-indicator');
        if (indicator) {
            indicator.remove();
        }
    }
}

function updateSaveButton() {
    const saveBtn = document.querySelector('.btn-submit');
    const btnText = saveBtn.querySelector('.btn-text');
    
    if (hasChanges) {
        saveBtn.classList.remove('btn-disabled');
        btnText.textContent = 'Guardar Cambios';
        saveBtn.disabled = false;
    } else {
        saveBtn.classList.add('btn-disabled');
        btnText.textContent = 'Sin Cambios';
        saveBtn.disabled = true;
    }
}

// ======= Validación del Formulario =======
function initializeFormValidation() {
    const form = document.querySelector('.equipo-form');
    const inputs = form.querySelectorAll('input, textarea, select');
    
    inputs.forEach(input => {
        input.addEventListener('input', function() {
            validateField(this);
        });
        
        input.addEventListener('blur', function() {
            validateField(this);
        });
    });
}

function validateField(field) {
    const isRequired = field.hasAttribute('required');
    const value = field.value.trim();
    
    // Remover clases de validación previas
    field.classList.remove('is-valid', 'is-invalid');
    
    // Validación básica de campos requeridos
    if (isRequired && !value) {
        field.classList.add('is-invalid');
        showFieldError(field, 'Este campo es obligatorio.');
        return false;
    }
    
    // Validaciones específicas por tipo de campo
    if (field.name === 'nombre' && value) {
        if (value.length < 3) {
            field.classList.add('is-invalid');
            showFieldError(field, 'El nombre debe tener al menos 3 caracteres.');
            return false;
        }
        if (value.length > 50) {
            field.classList.add('is-invalid');
            showFieldError(field, 'El nombre no puede exceder 50 caracteres.');
            return false;
        }
    }
    
    if (field.name === 'descripcion' && value && value.length > 500) {
        field.classList.add('is-invalid');
        showFieldError(field, 'La descripción no puede exceder 500 caracteres.');
        return false;
    }
    
    // Si llegamos aquí, el campo es válido
    if (value || !isRequired) {
        field.classList.add('is-valid');
        clearFieldError(field);
        return true;
    }
    
    return true;
}

function showFieldError(field, message) {
    const fieldContainer = field.closest('.form-field');
    clearFieldError(field);
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'field-errors';
    errorDiv.innerHTML = `<small class="error-text">${message}</small>`;
    
    fieldContainer.appendChild(errorDiv);
}

function clearFieldError(field) {
    const fieldContainer = field.closest('.form-field');
    const existingError = fieldContainer.querySelector('.field-errors');
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
        this.style.borderColor = '#d97706';
        this.style.backgroundColor = 'rgba(217, 119, 6, 0.15)';
    });
    
    preview.addEventListener('dragleave', function(e) {
        e.preventDefault();
        this.style.borderColor = '#f59e0b';
        this.style.backgroundColor = 'rgba(245, 158, 11, 0.08)';
    });
    
    preview.addEventListener('drop', function(e) {
        e.preventDefault();
        this.style.borderColor = '#f59e0b';
        this.style.backgroundColor = 'rgba(245, 158, 11, 0.08)';
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            fileInput.files = files;
            fileInput.dispatchEvent(new Event('change'));
        }
    });
}

function showImagePreview(src) {
    const preview = document.getElementById('escudo-preview');
    preview.innerHTML = `
        <img src="${src}" alt="Preview del escudo">
        <div class="current-badge">Nuevo</div>
    `;
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
        z-index: 10;
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
    
    // Inicializar previews de color
    const colorInputs = document.querySelectorAll('input[type="color"]');
    colorInputs.forEach(input => {
        updateColorPreview(input);
    });
}

function updatePreview(escudoSrc = null) {
    const nombreInput = document.querySelector('input[name="nombre"]');
    const descripcionInput = document.querySelector('textarea[name="descripcion"]');
    const colorPrimarioInput = document.querySelector('input[name="color_primario"]');
    const colorSecundarioInput = document.querySelector('input[name="color_secundario"]');
    
    const newPreview = document.getElementById('new-preview');
    const previewName = newPreview.querySelector('.preview-name');
    const previewDescription = newPreview.querySelector('.preview-description');
    const previewShield = newPreview.querySelector('.preview-shield');
    const primaryColorSample = newPreview.querySelector('.primary-color');
    const secondaryColorSample = newPreview.querySelector('.secondary-color');
    
    // Actualizar nombre
    if (nombreInput && previewName) {
        const nombre = nombreInput.value.trim() || previewName.textContent;
        previewName.textContent = nombre;
    }
    
    // Actualizar descripción
    if (descripcionInput && previewDescription) {
        const descripcion = descripcionInput.value.trim() || previewDescription.textContent;
        previewDescription.textContent = descripcion;
    }
    
    // Actualizar escudo
    if (previewShield && escudoSrc) {
        previewShield.innerHTML = `<img src="${escudoSrc}" alt="Escudo nuevo">`;
    }
    
    // Actualizar colores
    if (colorPrimarioInput && primaryColorSample) {
        const colorPrimario = colorPrimarioInput.value;
        primaryColorSample.style.backgroundColor = colorPrimario;
        
        // Actualizar también el escudo si no hay imagen nueva
        if (previewShield && !previewShield.querySelector('img')) {
            const colorSecundario = colorSecundarioInput?.value || '#a855f7';
            previewShield.style.background = `linear-gradient(135deg, ${colorPrimario}, ${colorSecundario})`;
        }
    }
    
    if (colorSecundarioInput && secondaryColorSample) {
        const colorSecundario = colorSecundarioInput.value;
        secondaryColorSample.style.backgroundColor = colorSecundario;
    }
    
    // Agregar efecto de actualización
    newPreview.style.transform = 'scale(1.02)';
    newPreview.style.borderColor = '#f59e0b';
    setTimeout(() => {
        newPreview.style.transform = 'scale(1)';
        newPreview.style.borderColor = '#f59e0b';
    }, 300);
}

function updateColorPreview(colorInput) {
    const fieldName = colorInput.getAttribute('data-field') || colorInput.name;
    const colorPreview = document.querySelector(`.color-preview[data-field="${fieldName}"]`);
    
    if (colorPreview) {
        const swatch = colorPreview.querySelector('.color-swatch');
        const value = colorPreview.querySelector('.color-value');
        
        if (swatch) swatch.style.backgroundColor = colorInput.value;
        if (value) value.textContent = colorInput.value.toUpperCase();
    }
}

// ======= Envío del Formulario =======
function initializeFormSubmission() {
    const form = document.querySelector('.equipo-form');
    const submitBtn = document.querySelector('.btn-submit');
    
    if (!form || !submitBtn) return;
    
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Solo proceder si hay cambios
        if (!hasChanges) {
            showFormMessage('No hay cambios para guardar.', 'info');
            return;
        }
        
        // Validar todos los campos antes del envío
        if (validateForm()) {
            showLoadingState(submitBtn);
            
            // Remover el listener de beforeunload ya que estamos guardando
            hasChanges = false;
            
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
        
        showFormMessage('Por favor corrige los errores antes de continuar.', 'error');
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

function showFormMessage(message, type) {
    // Remover mensaje anterior si existe
    const existingMessage = document.querySelector('.form-message-alert');
    if (existingMessage) {
        existingMessage.remove();
    }
    
    const alertClass = {
        'success': 'alert-success',
        'error': 'alert-danger',
        'warning': 'alert-warning',
        'info': 'alert-info'
    }[type] || 'alert-info';
    
    const iconClass = {
        'success': 'check-circle',
        'error': 'exclamation-triangle',
        'warning': 'exclamation-circle',
        'info': 'info-circle'
    }[type] || 'info-circle';
    
    const messageAlert = document.createElement('div');
    messageAlert.className = `alert ${alertClass} form-message-alert`;
    messageAlert.innerHTML = `
        <i class="fas fa-${iconClass} me-2"></i>
        ${message}
    `;
    
    const form = document.querySelector('.equipo-form');
    form.insertBefore(messageAlert, form.firstChild);
    
    // Scroll al mensaje
    messageAlert.scrollIntoView({ 
        behavior: 'smooth', 
        block: 'center' 
    });
    
    // Remover después de 5 segundos
    setTimeout(() => {
        if (messageAlert.parentNode) {
            messageAlert.remove();
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
        document.querySelectorAll('.form-section, .comparison-section, .form-actions').forEach(el => {
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
            this.style.transform = 'translateY(-2px)';
        });
        
        section.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
    
    // Efectos para los campos de color
    document.querySelectorAll('input[type="color"]').forEach(colorInput => {
        colorInput.addEventListener('focus', function() {
            this.style.transform = 'scale(1.02)';
        });
        
        colorInput.addEventListener('blur', function() {
            this.style.transform = 'scale(1)';
        });
    });
    
    // Efecto de comparación entre cards
    const comparisonItems = document.querySelectorAll('.comparison-item');
    comparisonItems.forEach(item => {
        item.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.02)';
            
            // Destacar el otro item también
            comparisonItems.forEach(otherItem => {
                if (otherItem !== this) {
                    otherItem.style.opacity = '0.7';
                }
            });
        });
        
        item.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1)';
            
            // Restaurar opacidad
            comparisonItems.forEach(otherItem => {
                otherItem.style.opacity = '1';
            });
        });
    });
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

// ======= Funciones de Comparación =======
function highlightChanges() {
    const currentPreview = document.getElementById('current-preview');
    const newPreview = document.getElementById('new-preview');
    
    if (hasChanges) {
        newPreview.style.animation = 'pulse 2s infinite';
        newPreview.style.borderColor = '#f59e0b';
    } else {
        newPreview.style.animation = 'none';
        newPreview.style.borderColor = '#64748b';
    }
}

// ======= Auto-save (opcional) =======
function initializeAutoSave() {
    let autoSaveTimeout;
    const form = document.querySelector('.equipo-form');
    
    form.addEventListener('input', debounce(function() {
        if (hasChanges) {
            clearTimeout(autoSaveTimeout);
            autoSaveTimeout = setTimeout(() => {
                showAutoSaveIndicator();
            }, 30000); // Auto-save después de 30 segundos de inactividad
        }
    }, 1000));
}

function showAutoSaveIndicator() {
    const indicator = document.createElement('div');
    indicator.className = 'auto-save-indicator';
    indicator.innerHTML = '<i class="fas fa-cloud-upload-alt me-2"></i>Guardado automático disponible';
    indicator.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: rgba(16, 185, 129, 0.9);
        color: white;
        padding: 0.75rem 1rem;
        border-radius: 8px;
        font-size: 0.875rem;
        z-index: 1000;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        cursor: pointer;
        transition: all 0.3s ease;
    `;
    
    indicator.addEventListener('click', function() {
        const form = document.querySelector('.equipo-form');
        form.submit();
    });
    
    document.body.appendChild(indicator);
    
    // Remover después de 5 segundos
    setTimeout(() => {
        if (indicator.parentNode) {
            indicator.style.opacity = '0';
            setTimeout(() => indicator.remove(), 300);
        }
    }, 5000);
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
        
        // Aplicar altura inicial
        textarea.style.height = 'auto';
        textarea.style.height = textarea.scrollHeight + 'px';
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
    
    // Prevenir envío accidental del formulario
    document.addEventListener('keydown', function(e) {
        if (e.ctrlKey && e.key === 'Enter') {
            e.preventDefault();
            const submitBtn = document.querySelector('.btn-submit');
            if (submitBtn && !submitBtn.disabled) {
                submitBtn.click();
            }
        }
    });
    
    // Restaurar scroll position si viene de una validación
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('error')) {
        setTimeout(() => {
            const firstError = document.querySelector('.is-invalid');
            if (firstError) {
                firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        }, 500);
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
        transition: color 0.3s ease;
    `;
    
    const updateCounter = () => {
        const current = element.value.length;
        counter.textContent = `${current}/${maxLength}`;
        
        if (current > maxLength) {
            counter.style.color = '#ef4444';
            counter.style.fontWeight = '600';
        } else if (current > maxLength * 0.9) {
            counter.style.color = '#f59e0b';
            counter.style.fontWeight = '500';
        } else {
            counter.style.color = '#94a3b8';
            counter.style.fontWeight = '400';
        }
    };
    
    element.addEventListener('input', updateCounter);
    element.parentNode.appendChild(counter);
    updateCounter();
}

// ======= Funciones de Confirmación =======
function confirmNavigation() {
    if (hasChanges) {
        return confirm('¿Estás seguro de que quieres salir? Los cambios no guardados se perderán.');
    }
    return true;
}

// Aplicar confirmación a los enlaces de navegación
document.querySelectorAll('a[href]').forEach(link => {
    // Excepto los que son part del formulario
    if (!link.closest('.form-actions')) {
        link.addEventListener('click', function(e) {
            if (!confirmNavigation()) {
                e.preventDefault();
            }
        });
    }
});

// ======= Función de Reset =======
function resetForm() {
    if (confirm('¿Estás seguro de que quieres descartar todos los cambios?')) {
        const form = document.querySelector('.equipo-form');
        
        // Restaurar valores originales
        Object.keys(originalValues).forEach(fieldName => {
            const field = form.querySelector(`[name="${fieldName}"]`);
            if (field && field.type !== 'file') {
                field.value = originalValues[fieldName];
                field.classList.remove('is-valid', 'is-invalid');
                unmarkFieldAsChanged(field);
                clearFieldError(field);
            }
        });
        
        // Limpiar archivo si se había seleccionado uno nuevo
        const fileInput = form.querySelector('input[type="file"]');
        if (fileInput) {
            fileInput.value = '';
            // Restaurar preview original si existe
            const preview = document.getElementById('escudo-preview');
            // Aquí deberías restaurar la imagen original del equipo
        }
        
        hasChanges = false;
        updateSaveButton();
        updatePreview();
        
        showFormMessage('Cambios descartados correctamente.', 'info');
    }
}

// ======= Función de Debug =======
function debugEditForm() {
    console.log('=== Debug Editar Equipo ===');
    console.log('Valores originales:', originalValues);
    console.log('Tiene cambios:', hasChanges);
    
    const form = document.querySelector('.equipo-form');
    const formData = new FormData(form);
    
    console.log('Datos actuales del formulario:');
    for (let [key, value] of formData.entries()) {
        const original = originalValues[key];
        const changed = original !== value;
        console.log(`${key}:`, {
            original: original,
            current: value,
            changed: changed
        });
    }
    
    console.log('Estado de validación:');
    const inputs = form.querySelectorAll('input, textarea, select');
    inputs.forEach(input => {
        console.log(`${input.name}:`, {
            value: input.value,
            valid: input.classList.contains('is-valid'),
            invalid: input.classList.contains('is-invalid'),
            changed: input.closest('.form-field')?.classList.contains('field-changed')
        });
    });
}

// Hacer disponibles globalmente para debugging
window.debugEditForm = debugEditForm;
window.resetForm = resetForm;
window.trackChanges = trackChanges;