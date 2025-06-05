// Configuración
const AI_ENDPOINT = 'http://localhost:8001/query-database-agent';

// Estado de la aplicación
let isListening = false;
let isProcessing = false;
let isSpeaking = false;
let recognition = null;
let speechSynthesis = window.speechSynthesis;
let currentUtterance = null;

// Variables WebGL
let gl, program, backgroundGL, backgroundProgram;
let faceCanvas, backgroundCanvas;
let mouseX = 0, mouseY = 0;
let startTime = Date.now();
let speakingLevel = 0;
let energyLevel = 0;

// Elementos DOM
const voiceInput = document.getElementById('voiceInput');
const voiceBtn = document.getElementById('voiceBtn');
const sendBtn = document.getElementById('sendBtn');
const muteBtn = document.getElementById('muteBtn');
const volumeRange = document.getElementById('volumeRange');
const aiStatus = document.getElementById('aiStatus');
const aiMouth = document.getElementById('aiMouth');
const faceContainer = document.querySelector('.ai-face-container');
const voiceStatusDot = document.getElementById('voiceStatusDot');
const voiceStatusText = document.getElementById('voiceStatusText');

// Inicializar aplicación
document.addEventListener('DOMContentLoaded', function() {
    initializeWebGL();
    initializeSpeechRecognition();
    initializeEventListeners();
    initializeTextToSpeech();
    updateStatus('ready', 'Listo para escuchar');
});

// Inicializar WebGL para la cara
function initializeWebGL() {
    faceCanvas = document.getElementById('faceCanvas');
    backgroundCanvas = document.getElementById('backgroundCanvas');
    
    // Configurar canvas de fondo
    backgroundCanvas.width = window.innerWidth;
    backgroundCanvas.height = window.innerHeight;
    
    // Configurar canvas de cara
    faceCanvas.width = 400;
    faceCanvas.height = 400;
    
    // Inicializar contextos WebGL
    initializeFaceGL();
    initializeBackgroundGL();
    
    // Event listeners para mouse
    document.addEventListener('mousemove', (e) => {
        mouseX = e.clientX / window.innerWidth;
        mouseY = 1.0 - (e.clientY / window.innerHeight);
    });
    
    // Iniciar renderizado
    render();
}

// Inicializar WebGL para la cara
function initializeFaceGL() {
    gl = faceCanvas.getContext('webgl');
    if (!gl) {
        console.error('WebGL no disponible');
        return;
    }
    
    const vertexShader = createShader(gl, gl.VERTEX_SHADER, document.getElementById('faceVertexShader').textContent);
    const fragmentShader = createShader(gl, gl.FRAGMENT_SHADER, document.getElementById('faceFragmentShader').textContent);
    
    program = createProgram(gl, vertexShader, fragmentShader);
    
    // Buffer de vértices
    const buffer = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, buffer);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, 1, -1, -1, 1, -1, 1, 1]), gl.STATIC_DRAW);
    
    const vPosition = gl.getAttribLocation(program, 'vPosition');
    gl.vertexAttribPointer(vPosition, 2, gl.FLOAT, false, 0, 0);
    gl.enableVertexAttribArray(vPosition);
    
    gl.useProgram(program);
    gl.viewport(0, 0, faceCanvas.width, faceCanvas.height);
    
    // Uniforms
    gl.uniform2fv(gl.getUniformLocation(program, 'resolution'), [faceCanvas.width, faceCanvas.height]);
}

// Inicializar WebGL para el fondo
function initializeBackgroundGL() {
    backgroundGL = backgroundCanvas.getContext('webgl');
    if (!backgroundGL) return;
    
    const bgVertexShader = `
        attribute vec4 vPosition;
        void main() {
            gl_Position = vPosition;
        }
    `;
    
    const bgFragmentShader = `
        #ifdef GL_ES
        precision mediump float;
        #endif
        uniform float time;
        uniform vec2 resolution;
        
        void main() {
            vec2 uv = gl_FragCoord.xy / resolution.xy;
            vec3 color = vec3(0.05, 0.1, 0.2);
            
            // Partículas flotantes
            for(int i = 0; i < 3; i++) {
                float fi = float(i);
                vec2 p = uv + vec2(sin(time * 0.5 + fi), cos(time * 0.3 + fi)) * 0.1;
                float d = length(p - 0.5);
                color += vec3(0.02, 0.05, 0.1) / (d * 10.0);
            }
            
            gl_FragColor = vec4(color, 1.0);
        }
    `;
    
    const vertexShader = createShader(backgroundGL, backgroundGL.VERTEX_SHADER, bgVertexShader);
    const fragmentShader = createShader(backgroundGL, backgroundGL.FRAGMENT_SHADER, bgFragmentShader);
    
    backgroundProgram = createProgram(backgroundGL, vertexShader, fragmentShader);
    
    const buffer = backgroundGL.createBuffer();
    backgroundGL.bindBuffer(backgroundGL.ARRAY_BUFFER, buffer);
    backgroundGL.bufferData(backgroundGL.ARRAY_BUFFER, new Float32Array([-1, 1, -1, -1, 1, -1, 1, 1]), backgroundGL.STATIC_DRAW);
    
    const vPosition = backgroundGL.getAttribLocation(backgroundProgram, 'vPosition');
    backgroundGL.vertexAttribPointer(vPosition, 2, backgroundGL.FLOAT, false, 0, 0);
    backgroundGL.enableVertexAttribArray(vPosition);
    
    backgroundGL.useProgram(backgroundProgram);
    backgroundGL.viewport(0, 0, backgroundCanvas.width, backgroundCanvas.height);
    
    backgroundGL.uniform2fv(backgroundGL.getUniformLocation(backgroundProgram, 'resolution'), [backgroundCanvas.width, backgroundCanvas.height]);
}

// Crear shader
function createShader(gl, type, source) {
    const shader = gl.createShader(type);
    gl.shaderSource(shader, source);
    gl.compileShader(shader);
    
    if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
        console.error('Error compilando shader:', gl.getShaderInfoLog(shader));
        gl.deleteShader(shader);
        return null;
    }
    
    return shader;
}

// Crear programa WebGL
function createProgram(gl, vertexShader, fragmentShader) {
    const program = gl.createProgram();
    gl.attachShader(program, vertexShader);
    gl.attachShader(program, fragmentShader);
    gl.linkProgram(program);
    
    if (!gl.getProgramParameter(program, gl.LINK_STATUS)) {
        console.error('Error enlazando programa:', gl.getProgramInfoLog(program));
        gl.deleteProgram(program);
        return null;
    }
    
    return program;
}

// Bucle de renderizado
function render() {
    const time = (Date.now() - startTime) / 1000;
    
    // Renderizar fondo
    if (backgroundGL && backgroundProgram) {
        backgroundGL.useProgram(backgroundProgram);
        backgroundGL.uniform1f(backgroundGL.getUniformLocation(backgroundProgram, 'time'), time);
        backgroundGL.drawArrays(backgroundGL.TRIANGLE_FAN, 0, 4);
    }
    
    // Renderizar cara
    if (gl && program) {
        gl.useProgram(program);
        gl.uniform1f(gl.getUniformLocation(program, 'time'), time);
        gl.uniform2fv(gl.getUniformLocation(program, 'mouse'), [mouseX, mouseY]);
        gl.uniform1f(gl.getUniformLocation(program, 'speaking'), speakingLevel);
        gl.uniform1f(gl.getUniformLocation(program, 'energy'), energyLevel);
        
        // Animar niveles
        if (isSpeaking) {
            speakingLevel = Math.min(speakingLevel + 0.1, 1.0);
            energyLevel = 0.5 + Math.sin(time * 10) * 0.3;
        } else {
            speakingLevel = Math.max(speakingLevel - 0.05, 0.0);
            energyLevel = Math.max(energyLevel - 0.02, 0.0);
        }
        
        gl.drawArrays(gl.TRIANGLE_FAN, 0, 4);
    }
    
    requestAnimationFrame(render);
}

// Inicializar reconocimiento de voz
function initializeSpeechRecognition() {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        recognition = new SpeechRecognition();
        
        recognition.lang = 'es-ES';
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.maxAlternatives = 1;
        
        recognition.onstart = () => {
            console.log('🎤 Reconocimiento iniciado');
            isListening = true;
            updateFaceState('listening');
            updateStatus('listening', 'Escuchando...');
            voiceBtn.classList.add('recording');
        };
        
        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            console.log('🎤 Texto reconocido:', transcript);
            voiceInput.value = transcript;
            sendMessage(transcript);
        };
        
        recognition.onerror = (event) => {
            console.error('❌ Error en reconocimiento:', event.error);
            updateStatus('error', 'Error en reconocimiento');
            stopListening();
        };
        
        recognition.onend = () => {
            console.log('🎤 Reconocimiento terminado');
            stopListening();
        };
    } else {
        console.log('❌ Reconocimiento de voz no disponible');
        voiceBtn.style.display = 'none';
    }
}

// Inicializar text-to-speech
function initializeTextToSpeech() {
    if ('speechSynthesis' in window) {
        console.log('🔊 Text-to-Speech disponible');
        
        // Cargar voces
        speechSynthesis.addEventListener('voiceschanged', () => {
            console.log('🔊 Voces cargadas:', speechSynthesis.getVoices().length);
        });
    } else {
        console.log('❌ Text-to-Speech no disponible');
    }
}

// Inicializar event listeners
function initializeEventListeners() {
    // Botón de voz
    voiceBtn.addEventListener('click', toggleListening);
    
    // Botón de enviar
    sendBtn.addEventListener('click', () => {
        const message = voiceInput.value.trim();
        if (message) {
            sendMessage(message);
        }
    });
    
    // Input de texto (Enter)
    voiceInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            const message = voiceInput.value.trim();
            if (message) {
                sendMessage(message);
            }
        }
    });
    
    // Botón de silenciar
    muteBtn.addEventListener('click', toggleMute);
    
    // Control de volumen
    volumeRange.addEventListener('input', (e) => {
        const volume = e.target.value / 100;
        if (currentUtterance) {
            currentUtterance.volume = volume;
        }
    });
    
    // Redimensionar canvas
    window.addEventListener('resize', () => {
        backgroundCanvas.width = window.innerWidth;
        backgroundCanvas.height = window.innerHeight;
        if (backgroundGL) {
            backgroundGL.viewport(0, 0, backgroundCanvas.width, backgroundCanvas.height);
            backgroundGL.uniform2fv(backgroundGL.getUniformLocation(backgroundProgram, 'resolution'), 
                [backgroundCanvas.width, backgroundCanvas.height]);
        }
    });
}

// Toggle del micrófono
function toggleListening() {
    if (!recognition) {
        console.log('❌ Reconocimiento no disponible');
        return;
    }
    
    if (isListening) {
        stopListening();
    } else {
        startListening();
    }
}

// Iniciar escucha
function startListening() {
    if (isProcessing || isSpeaking) {
        return;
    }
    
    try {
        recognition.start();
    } catch (error) {
        console.error('Error iniciando reconocimiento:', error);
        updateStatus('error', 'Error iniciando micrófono');
    }
}

// Detener escucha
function stopListening() {
    isListening = false;
    voiceBtn.classList.remove('recording');
    updateFaceState('idle');
    updateStatus('ready', 'Listo para escuchar');
    
    if (recognition) {
        try {
            recognition.stop();
        } catch (error) {
            console.log('Error deteniendo reconocimiento:', error);
        }
    }
}

// Enviar mensaje al AI
async function sendMessage(message) {
    if (isProcessing || !message.trim()) return;
    
    isProcessing = true;
    updateFaceState('processing');
    updateStatus('processing', 'Procesando...');
    sendBtn.disabled = true;
    voiceInput.value = '';
    
    try {
        const response = await fetch(AI_ENDPOINT, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                question: message
            })
        });
        
        if (!response.ok) {
            throw new Error(`Error HTTP: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        if (data.answer) {
            await speakResponse(data.answer);
        } else {
            throw new Error('Respuesta vacía del servidor');
        }
        
    } catch (error) {
        console.error('Error comunicándose con IA:', error);
        updateStatus('error', `Error: ${error.message}`);
        await speakResponse(`Lo siento, ha ocurrido un error: ${error.message}`);
    } finally {
        isProcessing = false;
        sendBtn.disabled = false;
        updateFaceState('idle');
        updateStatus('ready', 'Listo para escuchar');
    }
}

// Hablar respuesta
async function speakResponse(text) {
    return new Promise((resolve) => {
        if (!speechSynthesis) {
            console.log('❌ Speech synthesis no disponible');
            resolve();
            return;
        }
        
        // Detener cualquier speech anterior
        speechSynthesis.cancel();
        
        // Limpiar texto
        const cleanText = text
            .replace(/<[^>]*>/g, '')
            .replace(/\*\*(.*?)\*\*/g, '$1')
            .replace(/\*(.*?)\*/g, '$1')
            .replace(/•/g, '')
            .trim();
        
        if (!cleanText) {
            resolve();
            return;
        }
        
        // Crear utterance
        currentUtterance = new SpeechSynthesisUtterance(cleanText);
        
        // Configurar voz en español
        const voices = speechSynthesis.getVoices();
        const spanishVoice = voices.find(voice => 
            voice.lang.includes('es') || 
            voice.name.toLowerCase().includes('spanish')
        );
        
        if (spanishVoice) {
            currentUtterance.voice = spanishVoice;
        }
        
        currentUtterance.lang = 'es-ES';
        currentUtterance.rate = 0.9;
        currentUtterance.pitch = 1.0;
        currentUtterance.volume = volumeRange.value / 100;
        
        // Event listeners
        currentUtterance.onstart = () => {
            console.log('🔊 Hablando...');
            isSpeaking = true;
            updateFaceState('speaking');
            updateStatus('speaking', 'Hablando...');
            aiMouth.classList.add('speaking');
        };
        
        currentUtterance.onend = () => {
            console.log('🔊 Speech terminado');
            isSpeaking = false;
            updateFaceState('idle');
            updateStatus('ready', 'Listo para escuchar');
            aiMouth.classList.remove('speaking');
            resolve();
        };
        
        currentUtterance.onerror = (event) => {
            console.error('❌ Error en speech:', event.error);
            isSpeaking = false;
            updateFaceState('idle');
            updateStatus('error', 'Error en síntesis de voz');
            aiMouth.classList.remove('speaking');
            resolve();
        };
        
        // Hablar
        speechSynthesis.speak(currentUtterance);
    });
}

// Actualizar estado de la cara
function updateFaceState(state) {
    faceContainer.className = 'ai-face-container';
    if (state !== 'idle') {
        faceContainer.classList.add(state);
    }
}

// Actualizar estado general
function updateStatus(status, text) {
    aiStatus.textContent = text;
    voiceStatusText.textContent = text;
    
    // Actualizar indicador visual
    voiceStatusDot.className = 'status-dot';
    switch (status) {
        case 'ready':
            voiceStatusDot.style.background = '#00d4b1';
            break;
        case 'listening':
            voiceStatusDot.style.background = '#ffd700';
            break;
        case 'processing':
            voiceStatusDot.style.background = '#ff9500';
            break;
        case 'speaking':
            voiceStatusDot.style.background = '#00bfff';
            break;
        case 'error':
            voiceStatusDot.style.background = '#ff6b6b';
            break;
    }
}

// Toggle mute
function toggleMute() {
    const icon = muteBtn.querySelector('i');
    if (speechSynthesis.paused || volumeRange.value == 0) {
        speechSynthesis.resume();
        volumeRange.value = 80;
        icon.className = 'fas fa-volume-up';
    } else {
        speechSynthesis.pause();
        volumeRange.value = 0;
        icon.className = 'fas fa-volume-mute';
    }
}