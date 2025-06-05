// ==========================================
// LÓGICA DE VOZ CORREGIDA
// ==========================================

// Configuración de la API
const API_CONFIG = {
    endpoint: 'http://localhost:8001/query-database-agent',
    timeout: 15000,
    retries: 2,
    retryDelay: 1000
};

// Estado de la aplicación
let appState = {
    isListening: false,
    isProcessing: false,
    isSpeaking: false,
    isVoiceAvailable: false,
    isSpeechRecognitionAvailable: false,
    connectionStatus: 'unknown'
};

// Variables del sistema de voz
let recognition = null;
let speechSynthesis = window.speechSynthesis;
let currentUtterance = null;
let availableVoices = [];

// Elementos DOM
let voiceInput, voiceBtn, sendBtn, muteBtn, volumeRange;
let aiStatus, voiceStatusDot, voiceStatusText;

// Inicializar sistema de voz
function initializeVoiceSystem() {
    console.log('🎤 Inicializando sistema de voz...');
    
    // Obtener elementos DOM
    getDOMElements();
    
    // Inicializar reconocimiento de voz
    initializeSpeechRecognition();
    
    // Inicializar síntesis de voz
    initializeTextToSpeech();
    
    // Configurar event listeners
    setupEventListeners();
    
    // Verificar disponibilidad
    checkVoiceAvailability();
    
    console.log('✅ Sistema de voz inicializado');
}

// Obtener elementos DOM
function getDOMElements() {
    voiceInput = document.getElementById('voiceInput');
    voiceBtn = document.getElementById('voiceBtn');
    sendBtn = document.getElementById('sendBtn');
    muteBtn = document.getElementById('muteBtn');
    volumeRange = document.getElementById('volumeRange');
    aiStatus = document.getElementById('aiStatus');
    voiceStatusDot = document.getElementById('voiceStatusDot');
    voiceStatusText = document.getElementById('voiceStatusText');
    
    if (!voiceInput || !voiceBtn || !sendBtn) {
        console.error('❌ Elementos DOM no encontrados');
        return false;
    }
    
    return true;
}

// Inicializar reconocimiento de voz
function initializeSpeechRecognition() {
    try {
        // Verificar soporte
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        
        if (!SpeechRecognition) {
            console.log('❌ Speech Recognition no disponible');
            appState.isSpeechRecognitionAvailable = false;
            voiceBtn.style.display = 'none';
            return;
        }
        
        // Crear instancia
        recognition = new SpeechRecognition();
        
        // Configuración
        recognition.lang = 'es-ES';
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.maxAlternatives = 1;
        
        // Event listeners
        recognition.onstart = () => {
            console.log('🎤 Reconocimiento iniciado');
            appState.isListening = true;
            updateVoiceUI();
            setFaceState('listening');
            voiceBtn.classList.add('recording');
        };
        
        recognition.onresult = (event) => {
            const result = event.results[0];
            if (result.isFinal) {
                const transcript = result[0].transcript;
                console.log('🎤 Transcripción:', transcript);
                voiceInput.value = transcript;
                handleMessageSend(transcript);
            }
        };
        
        recognition.onerror = (event) => {
            console.error('❌ Error en reconocimiento:', event.error);
            
            // Manejar errores específicos
            let errorMessage = 'Error en reconocimiento de voz';
            switch (event.error) {
                case 'network':
                    errorMessage = 'Error de conexión';
                    break;
                case 'not-allowed':
                    errorMessage = 'Micrófono no permitido';
                    break;
                case 'no-speech':
                    errorMessage = 'No se detectó voz';
                    break;
                case 'audio-capture':
                    errorMessage = 'Error de captura de audio';
                    break;
            }
            
            updateStatus('error', errorMessage);
            stopListening();
        };
        
        recognition.onend = () => {
            console.log('🎤 Reconocimiento terminado');
            stopListening();
        };
        
        appState.isSpeechRecognitionAvailable = true;
        console.log('✅ Speech Recognition disponible');
        
    } catch (error) {
        console.error('❌ Error inicializando Speech Recognition:', error);
        appState.isSpeechRecognitionAvailable = false;
        voiceBtn.style.display = 'none';
    }
}

// Inicializar síntesis de voz
function initializeTextToSpeech() {
    try {
        if (!speechSynthesis) {
            console.log('❌ Speech Synthesis no disponible');
            appState.isVoiceAvailable = false;
            return;
        }
        
        // Cargar voces disponibles
        loadVoices();
        
        // Event listener para cambios de voces
        speechSynthesis.addEventListener('voiceschanged', loadVoices);
        
        appState.isVoiceAvailable = true;
        console.log('✅ Speech Synthesis disponible');
        
    } catch (error) {
        console.error('❌ Error inicializando Speech Synthesis:', error);
        appState.isVoiceAvailable = false;
    }
}

// Cargar voces disponibles
function loadVoices() {
    try {
        availableVoices = speechSynthesis.getVoices();
        console.log(`🔊 ${availableVoices.length} voces disponibles`);
        
        // Encontrar voz en español
        const spanishVoice = availableVoices.find(voice => 
            voice.lang.includes('es') || 
            voice.name.toLowerCase().includes('spanish')
        );
        
        if (spanishVoice) {
            console.log('✅ Voz en español encontrada:', spanishVoice.name);
        }
        
    } catch (error) {
        console.error('❌ Error cargando voces:', error);
    }
}

// Configurar event listeners
function setupEventListeners() {
    try {
        // Botón de voz
        if (voiceBtn) {
            voiceBtn.addEventListener('click', toggleListening);
        }
        
        // Botón de enviar
        if (sendBtn) {
            sendBtn.addEventListener('click', () => {
                const message = voiceInput?.value?.trim();
                if (message) {
                    handleMessageSend(message);
                }
            });
        }
        
        // Input de texto
        if (voiceInput) {
            voiceInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    const message = voiceInput.value.trim();
                    if (message) {
                        handleMessageSend(message);
                    }
                }
            });
        }
        
        // Botón de silenciar
        if (muteBtn) {
            muteBtn.addEventListener('click', toggleMute);
        }
        
        // Control de volumen
        if (volumeRange) {
            volumeRange.addEventListener('input', (e) => {
                const volume = e.target.value / 100;
                if (currentUtterance) {
                    currentUtterance.volume = volume;
                }
            });
        }
        
        console.log('✅ Event listeners configurados');
        
    } catch (error) { 
        console.log(error)
    }
}