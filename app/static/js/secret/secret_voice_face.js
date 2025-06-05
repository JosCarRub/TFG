// ==========================================
// CARA FUTURÍSTICA WEBGL - HUMANOIDE
// ==========================================

// Variables globales
let scene, camera, renderer, clock;
let faceGroup, eyeLeft, eyeRight, mouth;
let faceCanvas;
let mouseX = 0, mouseY = 0;
let faceState = 'idle'; // idle, listening, processing, speaking
let energyLevel = 0;
let speakingIntensity = 0;

// Configuración de la cara
const faceConfig = {
    canvas: null,
    width: 400,
    height: 400,
    cameraDistance: 5,
    colors: {
        idle: 0x00d4b1,
        listening: 0xffd700,
        processing: 0xff9500,
        speaking: 0x00bfff,
        error: 0xff6b6b
    },
    face: {
        radius: 1.5,
        detail: 32
    },
    eyes: {
        radius: 0.2,
        distance: 0.4,
        height: 0.3
    },
    mouth: {
        width: 0.6,
        height: 0.2,
        depth: 0.1
    }
};

// Shaders personalizados para efectos
const faceVertexShader = `
    uniform float time;
    uniform float energy;
    varying vec2 vUv;
    varying vec3 vNormal;
    varying vec3 vPosition;
    
    void main() {
        vUv = uv;
        vNormal = normalize(normalMatrix * normal);
        
        vec3 pos = position;
        
        // Efecto de ondas basado en energía
        float wave = sin(pos.x * 10.0 + time * 5.0) * sin(pos.y * 10.0 + time * 3.0);
        pos += normal * wave * energy * 0.1;
        
        vPosition = pos;
        gl_Position = projectionMatrix * modelViewMatrix * vec4(pos, 1.0);
    }
`;

const faceFragmentShader = `
    uniform float time;
    uniform float energy;
    uniform vec3 baseColor;
    uniform vec2 mouse;
    varying vec2 vUv;
    varying vec3 vNormal;
    varying vec3 vPosition;
    
    void main() {
        vec3 color = baseColor;
        
        // Gradiente base
        float gradient = dot(vNormal, vec3(0.0, 0.0, 1.0));
        color *= 0.7 + gradient * 0.3;
        
        // Patrones de circuitos
        float circuit1 = step(0.98, sin(vUv.x * 50.0 + time)) * step(0.98, sin(vUv.y * 30.0));
        float circuit2 = step(0.95, sin(vUv.x * 30.0 - time)) * step(0.95, sin(vUv.y * 50.0));
        
        color += vec3(circuit1 + circuit2) * energy * 0.5;
        
        // Efecto de mouse
        float mouseDistance = distance(vUv, mouse);
        float mouseEffect = 1.0 - smoothstep(0.0, 0.3, mouseDistance);
        color += vec3(0.2, 0.4, 0.8) * mouseEffect * 0.3;
        
        // Pulso de energía
        float pulse = sin(time * 8.0) * 0.5 + 0.5;
        color += baseColor * energy * pulse * 0.2;
        
        gl_FragColor = vec4(color, 1.0);
    }
`;

// Inicializar la cara futurística
function initializeFuturisticFace() {
    console.log('🎭 Inicializando cara futurística WebGL...');
    
    faceCanvas = document.getElementById('faceCanvas');
    if (!faceCanvas) {
        console.error('❌ Canvas no encontrado');
        return;
    }
    
    setupThreeJS();
    createFaceGeometry();
    setupLighting();
    setupEventListeners();
    
    animate();
    
    console.log('✅ Cara futurística inicializada');
}

// Configurar Three.js
function setupThreeJS() {
    const container = document.querySelector('.ai-face-container');
    const size = Math.min(container.clientWidth, container.clientHeight);
    
    faceConfig.width = size;
    faceConfig.height = size;
    
    // Escena
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x0a0a0a);
    
    // Cámara
    camera = new THREE.PerspectiveCamera(
        50,
        faceConfig.width / faceConfig.height,
        0.1,
        1000
    );
    camera.position.z = faceConfig.cameraDistance;
    
    // Renderer
    renderer = new THREE.WebGLRenderer({
        canvas: faceCanvas,
        antialias: true,
        alpha: true
    });
    renderer.setSize(faceConfig.width, faceConfig.height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    
    // Clock para animaciones
    clock = new THREE.Clock();
}

// Crear geometría de la cara
function createFaceGeometry() {
    // Grupo principal de la cara
    faceGroup = new THREE.Group();
    
    // Crear cara base
    createFaceBase();
    
    // Crear ojos
    createEyes();
    
    // Crear boca
    createMouth();
    
    scene.add(faceGroup);
}

// Crear base de la cara
function createFaceBase() {
    const geometry = new THREE.SphereGeometry(
        faceConfig.face.radius,
        faceConfig.face.detail,
        faceConfig.face.detail
    );
    
    // Aplanar ligeramente para forma más humana
    const positions = geometry.attributes.position.array;
    for (let i = 0; i < positions.length; i += 3) {
        positions[i + 2] *= 0.8; // Aplanar en Z
    }
    geometry.attributes.position.needsUpdate = true;
    geometry.computeVertexNormals();
    
    const material = new THREE.ShaderMaterial({
        uniforms: {
            time: { value: 0 },
            energy: { value: 0 },
            baseColor: { value: new THREE.Color(faceConfig.colors.idle) },
            mouse: { value: new THREE.Vector2(0.5, 0.5) }
        },
        vertexShader: faceVertexShader,
        fragmentShader: faceFragmentShader,
        transparent: true
    });
    
    const faceMesh = new THREE.Mesh(geometry, material);
    faceMesh.name = 'faceBase';
    faceGroup.add(faceMesh);
}

// Crear ojos
function createEyes() {
    // Geometría del ojo
    const eyeGeometry = new THREE.SphereGeometry(faceConfig.eyes.radius, 16, 16);
    
    // Material del ojo
    const eyeMaterial = new THREE.MeshPhongMaterial({
        color: 0x87ceeb,
        shininess: 100,
        transparent: true,
        opacity: 0.9
    });
    
    // Ojo izquierdo
    eyeLeft = new THREE.Mesh(eyeGeometry, eyeMaterial);
    eyeLeft.position.set(-faceConfig.eyes.distance, faceConfig.eyes.height, 1.2);
    eyeLeft.name = 'eyeLeft';
    
    // Ojo derecho
    eyeRight = new THREE.Mesh(eyeGeometry, eyeMaterial);
    eyeRight.position.set(faceConfig.eyes.distance, faceConfig.eyes.height, 1.2);
    eyeRight.name = 'eyeRight';
    
    // Pupilas
    const pupilGeometry = new THREE.SphereGeometry(faceConfig.eyes.radius * 0.5, 8, 8);
    const pupilMaterial = new THREE.MeshBasicMaterial({ color: 0x1a1a2e });
    
    const pupilLeft = new THREE.Mesh(pupilGeometry, pupilMaterial);
    pupilLeft.position.z = 0.1;
    eyeLeft.add(pupilLeft);
    
    const pupilRight = new THREE.Mesh(pupilGeometry, pupilMaterial);
    pupilRight.position.z = 0.1;
    eyeRight.add(pupilRight);
    
    faceGroup.add(eyeLeft);
    faceGroup.add(eyeRight);
}

// Crear boca
function createMouth() {
    const mouthGeometry = new THREE.RingGeometry(
        faceConfig.mouth.width * 0.3,
        faceConfig.mouth.width * 0.5,
        8,
        1,
        0,
        Math.PI
    );
    
    const mouthMaterial = new THREE.MeshPhongMaterial({
        color: 0xff6b6b,
        transparent: true,
        opacity: 0.8,
        side: THREE.DoubleSide
    });
    
    mouth = new THREE.Mesh(mouthGeometry, mouthMaterial);
    mouth.position.set(0, -faceConfig.mouth.height, 1);
    mouth.rotation.x = Math.PI;
    mouth.name = 'mouth';
    
    faceGroup.add(mouth);
}

// Configurar iluminación
function setupLighting() {
    // Luz ambiental
    const ambientLight = new THREE.AmbientLight(0x404040, 0.6);
    scene.add(ambientLight);
    
    // Luces direccionales
    const frontLight = new THREE.DirectionalLight(0xffffff, 0.8);
    frontLight.position.set(0, 0, 5);
    scene.add(frontLight);
    
    const backLight = new THREE.DirectionalLight(0x00d4b1, 0.3);
    backLight.position.set(0, 0, -5);
    scene.add(backLight);
    
    // Luces puntuales para efectos
    const leftLight = new THREE.PointLight(0x00bfff, 0.5, 10);
    leftLight.position.set(-3, 1, 2);
    scene.add(leftLight);
    
    const rightLight = new THREE.PointLight(0xff6b6b, 0.5, 10);
    rightLight.position.set(3, 1, 2);
    scene.add(rightLight);
}

// Configurar event listeners
function setupEventListeners() {
    // Seguimiento del mouse
    faceCanvas.addEventListener('mousemove', (event) => {
        const rect = faceCanvas.getBoundingClientRect();
        mouseX = ((event.clientX - rect.left) / rect.width) * 2 - 1;
        mouseY = -((event.clientY - rect.top) / rect.height) * 2 + 1;
        
        // Actualizar uniforme del shader
        const faceMesh = faceGroup.getObjectByName('faceBase');
        if (faceMesh) {
            faceMesh.material.uniforms.mouse.value.set(
                (mouseX + 1) * 0.5,
                (mouseY + 1) * 0.5
            );
        }
    });
    
    // Redimensionar
    window.addEventListener('resize', () => {
        const container = document.querySelector('.ai-face-container');
        const size = Math.min(container.clientWidth, container.clientHeight);
        
        faceConfig.width = size;
        faceConfig.height = size;
        
        camera.aspect = faceConfig.width / faceConfig.height;
        camera.updateProjectionMatrix();
        renderer.setSize(faceConfig.width, faceConfig.height);
    });
}

// Bucle de animación
function animate() {
    requestAnimationFrame(animate);
    
    const elapsedTime = clock.getElapsedTime();
    
    updateFaceAnimations(elapsedTime);
    updateEyeAnimations(elapsedTime);
    updateMouthAnimations(elapsedTime);
    
    renderer.render(scene, camera);
}

// Actualizar animaciones de la cara
function updateFaceAnimations(time) {
    if (!faceGroup) return;
    
    const faceMesh = faceGroup.getObjectByName('faceBase');
    if (!faceMesh) return;
    
    // Actualizar uniforms del shader
    faceMesh.material.uniforms.time.value = time;
    faceMesh.material.uniforms.energy.value = energyLevel;
    
    // Rotación sutil
    faceGroup.rotation.y = Math.sin(time * 0.5) * 0.1;
    faceGroup.rotation.x = Math.sin(time * 0.3) * 0.05;
    
    // Actualizar color según estado
    const targetColor = new THREE.Color(faceConfig.colors[faceState]);
    faceMesh.material.uniforms.baseColor.value.lerp(targetColor, 0.05);
}

// Actualizar animaciones de los ojos
function updateEyeAnimations(time) {
    if (!eyeLeft || !eyeRight) return;
    
    switch (faceState) {
        case 'listening':
            // Parpadeo más frecuente
            const blinkListening = Math.sin(time * 4) > 0.8 ? 0.1 : 1;
            eyeLeft.scale.y = blinkListening;
            eyeRight.scale.y = blinkListening;
            
            // Movimiento de seguimiento
            eyeLeft.rotation.y = mouseX * 0.2;
            eyeRight.rotation.y = mouseX * 0.2;
            break;
            
        case 'processing':
            // Pulsación
            const pulseProcessing = 0.8 + Math.sin(time * 6) * 0.2;
            eyeLeft.scale.setScalar(pulseProcessing);
            eyeRight.scale.setScalar(pulseProcessing);
            break;
            
        case 'speaking':
            // Brillo intenso
            eyeLeft.material.emissive.setHex(0x004488);
            eyeRight.material.emissive.setHex(0x004488);
            break;
            
        default:
            // Estado idle - parpadeo normal
            const blinkIdle = Math.sin(time * 0.5) > 0.95 ? 0.1 : 1;
            eyeLeft.scale.y = blinkIdle;
            eyeRight.scale.y = blinkIdle;
            
            // Reset emissive
            eyeLeft.material.emissive.setHex(0x000000);
            eyeRight.material.emissive.setHex(0x000000);
    }
}

// Actualizar animaciones de la boca
function updateMouthAnimations(time) {
    if (!mouth) return;
    
    switch (faceState) {
        case 'speaking':
            // Animación de habla
            const speakScale = 1 + speakingIntensity * 0.5;
            mouth.scale.set(speakScale, speakScale, 1);
            
            // Ondulación
            mouth.rotation.z = Math.sin(time * 10) * speakingIntensity * 0.1;
            break;
            
        default:
            // Escala normal
            mouth.scale.set(1, 1, 1);
            mouth.rotation.z = 0;
    }
}

// Funciones públicas para controlar la cara
function setFaceState(newState) {
    faceState = newState;
    console.log(`🎭 Estado de cara: ${newState}`);
    
    // Actualizar energía según estado
    switch (newState) {
        case 'listening':
            energyLevel = 0.6;
            break;
        case 'processing':
            energyLevel = 0.8;
            break;
        case 'speaking':
            energyLevel = 1.0;
            break;
        case 'error':
            energyLevel = 0.3;
            break;
        default:
            energyLevel = 0.2;
    }
}

function setSpeakingIntensity(intensity) {
    speakingIntensity = Math.max(0, Math.min(1, intensity));
}

function setFaceEnergy(energy) {
    energyLevel = Math.max(0, Math.min(1, energy));
}

// Limpiar recursos
function cleanupFaceAnimation() {
    if (renderer) {
        renderer.dispose();
    }
    if (scene) {
        scene.clear();
    }
}