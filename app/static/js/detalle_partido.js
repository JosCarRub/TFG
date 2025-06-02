/**
 * Gestión Avanzada de Asignación de Equipos
 * Soporte para Drag & Drop, Lista Desplegable y Asignación Automática
 */

class AdvancedTeamAssignmentManager {
    constructor() {
        this.currentMode = 'drag';
        this.draggedElement = null;
        this.dragPreview = null;
        this.touchFeedback = null;
        this.isDragging = false;
        this.hasChanges = false;
        this.originalPositions = new Map();
        this.playersData = new Map();
        
        this.init();
    }

    init() {
        this.createDragPreview();
        this.createTouchFeedback();
        this.setupModeToggle();
        this.setupDragAndDrop();
        this.setupDropdownMode();
        this.setupAutoMode();
        this.setupSaveButton();
        this.storeOriginalData();
        this.setupKeyboardSupport();
        this.updateCounters();
    }

    // ===== INITIALIZATION =====
    createDragPreview() {
        this.dragPreview = document.getElementById('dragPreview');
        if (!this.dragPreview) {
            this.dragPreview = document.createElement('div');
            this.dragPreview.id = 'dragPreview';
            this.dragPreview.className = 'drag-preview';
            document.body.appendChild(this.dragPreview);
        }
    }

    createTouchFeedback() {
        this.touchFeedback = document.getElementById('touchFeedback');
        if (!this.touchFeedback) {
            this.touchFeedback = document.createElement('div');
            this.touchFeedback.id = 'touchFeedback';
            this.touchFeedback.className = 'touch-feedback';
            document.body.appendChild(this.touchFeedback);
        }
    }

    storeOriginalData() {
        // Almacenar datos originales y posiciones
        const players = document.querySelectorAll('[data-jugador-id]');
        players.forEach(player => {
            const jugadorId = player.dataset.jugadorId;
            const playerData = this.extractPlayerData(player);
            this.playersData.set(jugadorId, playerData);
            
            // Determinar equipo actual
            const container = player.closest('.players-drop-zone, .bench-players');
            let currentTeam = 'bench';
            if (container) {
                if (container.id === 'local-players') currentTeam = 'local';
                else if (container.id === 'visitante-players') currentTeam = 'visitante';
            }
            
            this.originalPositions.set(jugadorId, {
                team: currentTeam,
                element: player.cloneNode(true)
            });
        });
    }

    extractPlayerData(playerElement) {
        const img = playerElement.querySelector('img');
        const nameEl = playerElement.querySelector('.player-name');
        const positionEl = playerElement.querySelector('.player-position');
        const creatorBadge = playerElement.querySelector('.creator-badge, .creator-crown');
        
        return {
            id: playerElement.dataset.jugadorId,
            name: nameEl?.textContent.trim() || '',
            position: positionEl?.textContent.trim() || '',
            avatar: img?.src || '',
            isCreator: !!creatorBadge
        };
    }

    // ===== MODE TOGGLE SYSTEM =====
    setupModeToggle() {
        const modeButtons = document.querySelectorAll('.mode-btn');
        modeButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const mode = btn.dataset.mode;
                this.switchMode(mode);
            });
        });
    }

    switchMode(newMode) {
        if (this.currentMode === newMode) return;
        
        // Update button states
        document.querySelectorAll('.mode-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.mode === newMode);
        });
        
        // Update info cards
        document.querySelectorAll('[data-info]').forEach(info => {
            info.classList.toggle('active', info.dataset.info === newMode);
        });
        
        // Update assignment modes
        document.querySelectorAll('[data-assignment]').forEach(mode => {
            mode.classList.toggle('active', mode.dataset.assignment === newMode);
        });
        
        this.currentMode = newMode;
        
        // Sync data between modes
        this.syncModeData();
        
        // Mode-specific setup
        switch (newMode) {
            case 'drag':
                this.setupDragMode();
                break;
            case 'dropdown':
                this.setupDropdownMode();
                break;
            case 'auto':
                this.setupAutoMode();
                break;
        }
    }

    syncModeData() {
        // Sincronizar datos entre los diferentes modos
        if (this.currentMode === 'dropdown') {
            this.updateDropdownSelections();
            this.updateDropdownSummary();
        } else if (this.currentMode === 'drag') {
            this.updateDragPositions();
        }
    }

    updateDragPositions() {
        // Actualizar posiciones en drag mode desde dropdown
        // Esto se llamará cuando se cambie a modo drag
    }

    // ===== DRAG & DROP MODE =====
    setupDragAndDrop() {
        // Desktop drag events
        document.addEventListener('dragstart', this.handleDragStart.bind(this));
        document.addEventListener('dragend', this.handleDragEnd.bind(this));
        document.addEventListener('dragover', this.handleDragOver.bind(this));
        document.addEventListener('drop', this.handleDrop.bind(this));

        // Touch events for mobile
        document.addEventListener('touchstart', this.handleTouchStart.bind(this), { passive: false });
        document.addEventListener('touchmove', this.handleTouchMove.bind(this), { passive: false });
        document.addEventListener('touchend', this.handleTouchEnd.bind(this), { passive: false });

        // Drop zone events
        const dropZones = ['local-players', 'visitante-players', 'bench-players'];
        dropZones.forEach(zoneId => {
            const zone = document.getElementById(zoneId);
            if (zone) {
                zone.addEventListener('dragenter', this.handleDragEnter.bind(this));
                zone.addEventListener('dragleave', this.handleDragLeave.bind(this));
            }
        });
    }

    setupDragMode() {
        // Asegurar que todos los jugadores sean draggables
        document.querySelectorAll('[data-jugador-id]').forEach(player => {
            player.draggable = true;
            player.tabIndex = 0;
        });
    }

    // Drag event handlers
    handleDragStart(e) {
        if (!this.isDraggableElement(e.target) || this.currentMode !== 'drag') return;

        this.draggedElement = e.target.closest('[data-jugador-id]');
        if (!this.draggedElement) return;
        
        this.isDragging = true;
        
        this.draggedElement.classList.add('dragging');
        e.dataTransfer.effectAllowed = 'move';
        e.dataTransfer.setData('text/html', this.draggedElement.outerHTML);
        
        // Crear imagen transparente para ocultar el ghost nativo
        const emptyCanvas = document.createElement('canvas');
        emptyCanvas.width = 1;
        emptyCanvas.height = 1;
        const ctx = emptyCanvas.getContext('2d');
        ctx.globalAlpha = 0.01;
        e.dataTransfer.setDragImage(emptyCanvas, 0, 0);
        
        // Mostrar nuestro preview personalizado
        setTimeout(() => {
            this.updateDragPreview(this.draggedElement, e.clientX, e.clientY);
            this.showDragPreview();
        }, 0);
        
        this.addDragVisualFeedback();
    }

    handleDragEnd(e) {
        if (!this.isDragging) return;

        if (e.target.classList) {
            e.target.classList.remove('dragging');
        }
        this.endDrag();
    }

    handleDragOver(e) {
        if (!this.isDragging) return;
        e.preventDefault();
        e.dataTransfer.dropEffect = 'move';
        
        // Actualizar posición del preview
        this.updateDragPreview(this.draggedElement, e.clientX, e.clientY);
    }

    handleDragEnter(e) {
        const dropZone = e.currentTarget;
        if (this.canDropInZone(dropZone)) {
            dropZone.classList.add('drag-over');
        }
    }

    handleDragLeave(e) {
        const dropZone = e.currentTarget;
        if (!dropZone.contains(e.relatedTarget)) {
            dropZone.classList.remove('drag-over');
        }
    }

    handleDrop(e) {
        e.preventDefault();
        const dropZone = e.target.closest('.players-drop-zone, .bench-players');
        
        if (dropZone && this.draggedElement && this.canDropInZone(dropZone)) {
            this.movePlayerToZone(this.draggedElement, dropZone);
            this.showDropAnimation(e.clientX, e.clientY);
        }
        
        // Limpiar todos los estados visuales
        document.querySelectorAll('.drag-over').forEach(zone => {
            zone.classList.remove('drag-over');
        });
        
        // Forzar el fin del drag
        this.endDrag();
    }

    // Touch event handlers
    handleTouchStart(e) {
        if (!this.isDraggableElement(e.target) || this.currentMode !== 'drag') return;
        
        e.preventDefault();
        this.draggedElement = e.target.closest('[data-jugador-id]');
        if (!this.draggedElement) return;
        
        this.isDragging = true;
        
        const touch = e.touches[0];
        this.draggedElement.classList.add('dragging');
        this.updateDragPreview(this.draggedElement, touch.clientX, touch.clientY);
        this.showDragPreview();
        this.addDragVisualFeedback();
        this.showTouchFeedback(touch.clientX, touch.clientY);
        
        if (navigator.vibrate) navigator.vibrate(50);
    }

    handleTouchMove(e) {
        if (!this.isDragging || !this.draggedElement) return;
        
        e.preventDefault();
        const touch = e.touches[0];
        
        this.updateDragPreview(this.draggedElement, touch.clientX, touch.clientY);
        this.updateTouchFeedback(touch.clientX, touch.clientY);
        
        const elementBelow = document.elementFromPoint(touch.clientX, touch.clientY);
        const dropZone = elementBelow?.closest('.players-drop-zone, .bench-players');
        
        document.querySelectorAll('.drag-over').forEach(zone => {
            zone.classList.remove('drag-over');
        });
        
        if (dropZone && this.canDropInZone(dropZone)) {
            dropZone.classList.add('drag-over');
        }
    }

    handleTouchEnd(e) {
        if (!this.isDragging || !this.draggedElement) return;
        
        e.preventDefault();
        const touch = e.changedTouches[0];
        
        const elementBelow = document.elementFromPoint(touch.clientX, touch.clientY);
        const dropZone = elementBelow?.closest('.players-drop-zone, .bench-players');
        
        if (dropZone && this.canDropInZone(dropZone)) {
            this.movePlayerToZone(this.draggedElement, dropZone);
            this.showDropAnimation(touch.clientX, touch.clientY);
            if (navigator.vibrate) navigator.vibrate([50, 50, 50]);
        } else {
            if (navigator.vibrate) navigator.vibrate(200);
        }
        
        // Limpiar estados visuales
        document.querySelectorAll('.drag-over').forEach(zone => {
            zone.classList.remove('drag-over');
        });
        
        this.endDrag();
    }

    // ===== DROPDOWN MODE =====
    setupDropdownMode() {
        const selects = document.querySelectorAll('.team-select');
        selects.forEach(select => {
            select.addEventListener('change', this.handleTeamSelectionChange.bind(this));
        });
        
        this.updateDropdownSelections();
        this.updateDropdownSummary();
    }

    updateDropdownSelections() {
        // Sincronizar dropdowns con el estado actual
        const selects = document.querySelectorAll('.team-select');
        selects.forEach(select => {
            const jugadorId = select.dataset.jugador;
            const currentTeam = this.getCurrentPlayerTeam(jugadorId);
            select.value = currentTeam;
        });
    }

    handleTeamSelectionChange(e) {
        const select = e.target;
        const jugadorId = select.dataset.jugador;
        const newTeam = select.value;
        
        this.assignPlayerToTeam(jugadorId, newTeam);
        this.updateDropdownSummary();
        this.markChanges();
    }

    updateDropdownSummary() {
        const teams = {
            local: [],
            visitante: [],
            bench: []
        };
        
        // Recopilar asignaciones actuales
        document.querySelectorAll('.team-select').forEach(select => {
            const jugadorId = select.dataset.jugador;
            const team = select.value;
            const playerData = this.playersData.get(jugadorId);
            
            if (playerData) {
                teams[team].push(playerData);
            }
        });
        
        // Actualizar contadores
        const localCountEl = document.getElementById('localCountDropdown');
        const visitanteCountEl = document.getElementById('visitanteCountDropdown');
        const benchCountEl = document.getElementById('benchCountDropdown');
        
        if (localCountEl) localCountEl.textContent = teams.local.length;
        if (visitanteCountEl) visitanteCountEl.textContent = teams.visitante.length;
        if (benchCountEl) benchCountEl.textContent = teams.bench.length;
        
        // Actualizar previews
        this.updatePlayersPreview('localPlayersPreview', teams.local);
        this.updatePlayersPreview('visitantePlayersPreview', teams.visitante);
        this.updatePlayersPreview('benchPlayersPreview', teams.bench);
        
        // Animar contadores
        this.animateCounterUpdate('localCountDropdown');
        this.animateCounterUpdate('visitanteCountDropdown');
        this.animateCounterUpdate('benchCountDropdown');
    }

    updatePlayersPreview(containerId, players) {
        const container = document.getElementById(containerId);
        if (!container) return;
        
        container.innerHTML = '';
        
        players.forEach((player, index) => {
            const previewElement = document.createElement('div');
            previewElement.className = 'preview-player';
            previewElement.style.animationDelay = `${index * 0.1}s`;
            previewElement.innerHTML = `
                <img src="${player.avatar}" alt="${player.name}">
                <span>${player.name}</span>
            `;
            container.appendChild(previewElement);
        });
    }

    // ===== AUTO ASSIGNMENT MODE =====
    setupAutoMode() {
        const autoAssignBtn = document.getElementById('autoAssignBtn');
        if (autoAssignBtn) {
            autoAssignBtn.addEventListener('click', this.handleAutoAssignment.bind(this));
        }
    }

    handleAutoAssignment() {
        const selectedMode = document.querySelector('input[name="autoMode"]:checked')?.value;
        if (!selectedMode) return;
        
        const btn = document.getElementById('autoAssignBtn');
        const originalText = btn.innerHTML;
        
        // Show loading state
        btn.classList.add('loading');
        btn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Asignando...';
        btn.disabled = true;
        
        // Simulate processing time
        setTimeout(() => {
            const assignment = this.generateAutoAssignment(selectedMode);
            this.applyAutoAssignment(assignment);
            this.showAutoResult(assignment);
            
            // Reset button
            btn.classList.remove('loading');
            btn.innerHTML = originalText;
            btn.disabled = false;
            
            this.markChanges();
        }, 1500);
    }

    generateAutoAssignment(mode) {
        const players = Array.from(this.playersData.values());
        const maxPerTeam = this.getMaxPlayersPerTeam();
        
        let assignment = {
            local: [],
            visitante: [],
            bench: []
        };
        
        switch (mode) {
            case 'random':
                assignment = this.randomAssignment(players, maxPerTeam);
                break;
            case 'balanced':
                assignment = this.balancedAssignment(players, maxPerTeam);
                break;
            case 'position':
                assignment = this.positionBasedAssignment(players, maxPerTeam);
                break;
        }
        
        return assignment;
    }

    randomAssignment(players, maxPerTeam) {
        const shuffled = [...players].sort(() => Math.random() - 0.5);
        const assignment = { local: [], visitante: [], bench: [] };
        
        shuffled.forEach((player, index) => {
            if (index < maxPerTeam) {
                assignment.local.push(player);
            } else if (index < maxPerTeam * 2) {
                assignment.visitante.push(player);
            } else {
                assignment.bench.push(player);
            }
        });
        
        return assignment;
    }

    balancedAssignment(players, maxPerTeam) {
        // Asignación más equilibrada considerando experiencia/posición
        const sorted = [...players].sort((a, b) => {
            // Priorizar creador y posiciones específicas
            if (a.isCreator && !b.isCreator) return -1;
            if (!a.isCreator && b.isCreator) return 1;
            return Math.random() - 0.5;
        });
        
        const assignment = { local: [], visitante: [], bench: [] };
        
        // Alternar entre equipos para equilibrio
        sorted.forEach((player, index) => {
            if (assignment.local.length < maxPerTeam && assignment.visitante.length < maxPerTeam) {
                if (index % 2 === 0) {
                    assignment.local.push(player);
                } else {
                    assignment.visitante.push(player);
                }
            } else if (assignment.local.length < maxPerTeam) {
                assignment.local.push(player);
            } else if (assignment.visitante.length < maxPerTeam) {
                assignment.visitante.push(player);
            } else {
                assignment.bench.push(player);
            }
        });
        
        return assignment;
    }

    positionBasedAssignment(players, maxPerTeam) {
        // Asignación basada en posiciones
        const positions = {
            'DEF': [],
            'MED': [],
            'DEL': [],
            'POR': [],
            'OTHER': []
        };
        
        // Categorizar jugadores por posición
        players.forEach(player => {
            const pos = player.position.toUpperCase();
            if (positions[pos]) {
                positions[pos].push(player);
            } else {
                positions.OTHER.push(player);
            }
        });
        
        const assignment = { local: [], visitante: [], bench: [] };
        
        // Distribuir por posiciones
        Object.values(positions).forEach(posPlayers => {
            posPlayers.forEach((player, index) => {
                if (assignment.local.length < maxPerTeam && assignment.visitante.length < maxPerTeam) {
                    if (index % 2 === 0) {
                        assignment.local.push(player);
                    } else {
                        assignment.visitante.push(player);
                    }
                } else if (assignment.local.length < maxPerTeam) {
                    assignment.local.push(player);
                } else if (assignment.visitante.length < maxPerTeam) {
                    assignment.visitante.push(player);
                } else {
                    assignment.bench.push(player);
                }
            });
        });
        
        return assignment;
    }

    applyAutoAssignment(assignment) {
        // Aplicar asignación a todos los modos
        
        // Actualizar dropdowns
        document.querySelectorAll('.team-select').forEach(select => {
            const jugadorId = select.dataset.jugador;
            const playerTeam = this.findPlayerTeamInAssignment(jugadorId, assignment);
            select.value = playerTeam;
        });
        
        // Actualizar drag mode si está activo
        if (this.currentMode === 'drag') {
            this.updateDragPositionsFromAssignment(assignment);
        }
        
        // Actualizar dropdown summary
        this.updateDropdownSummary();
    }

    findPlayerTeamInAssignment(playerId, assignment) {
        for (const [team, players] of Object.entries(assignment)) {
            if (players.some(p => p.id === playerId)) {
                return team;
            }
        }
        return 'bench';
    }

    updateDragPositionsFromAssignment(assignment) {
        // Mover jugadores en el modo drag según la asignación
        Object.entries(assignment).forEach(([team, players]) => {
            const zoneId = team === 'bench' ? 'bench-players' : `${team}-players`;
            const zone = document.getElementById(zoneId);
            if (!zone) return;
            
            players.forEach(playerData => {
                const playerElement = document.querySelector(`[data-jugador-id="${playerData.id}"]`);
                if (playerElement && !zone.contains(playerElement)) {
                    this.movePlayerToZone(playerElement, zone, false);
                }
            });
        });
    }

    showAutoResult(assignment) {
        const resultContainer = document.getElementById('autoResult');
        if (!resultContainer) return;
        
        // Mostrar resultado
        resultContainer.style.display = 'block';
        
        // Poblar equipos
        this.populateAutoResultTeam('autoLocalPlayers', assignment.local);
        this.populateAutoResultTeam('autoVisitantePlayers', assignment.visitante);
        this.populateAutoResultTeam('autoBenchPlayers', assignment.bench);
    }

    populateAutoResultTeam(containerId, players) {
        const container = document.getElementById(containerId);
        if (!container) return;
        
        container.innerHTML = '';
        
        players.forEach((player, index) => {
            const playerElement = document.createElement('div');
            playerElement.className = 'result-player';
            playerElement.style.animationDelay = `${index * 0.1}s`;
            playerElement.innerHTML = `
                <img src="${player.avatar}" alt="${player.name}">
                <div class="result-player-info">
                    <div class="result-player-name">${player.name}</div>
                    <div class="result-player-position">${player.position}</div>
                </div>
                ${player.isCreator ? '<i class="fas fa-crown" style="color: #ffd700;"></i>' : ''}
            `;
            container.appendChild(playerElement);
        });
    }

    // ===== UTILITY METHODS =====
    isDraggableElement(element) {
        return element.closest('[data-jugador-id]') !== null;
    }

    canDropInZone(dropZone) {
        if (!dropZone || !this.draggedElement) return false;
        
        const currentZone = this.draggedElement.closest('.players-drop-zone, .bench-players');
        if (currentZone === dropZone) return false;
        
        if (dropZone.id === 'local-players' || dropZone.id === 'visitante-players') {
            const maxPlayers = this.getMaxPlayersPerTeam();
            const currentPlayers = dropZone.querySelectorAll('[data-jugador-id]').length;
            return currentPlayers < maxPlayers;
        }
        
        return true;
    }

    getMaxPlayersPerTeam() {
        const fieldElement = document.querySelector('.football-field');
        const tipoPartido = fieldElement?.dataset.tipoPartido;
        
        switch (tipoPartido) {
            case '5v5': return 5;
            case '7v7': return 7;
            case '11v11': return 11;
            default: return 11;
        }
    }

    getCurrentPlayerTeam(playerId) {
        const playerElement = document.querySelector(`[data-jugador-id="${playerId}"]`);
        if (!playerElement) return 'bench';
        
        const container = playerElement.closest('.players-drop-zone, .bench-players');
        if (!container) return 'bench';
        
        if (container.id === 'local-players') return 'local';
        if (container.id === 'visitante-players') return 'visitante';
        return 'bench';
    }

    assignPlayerToTeam(playerId, team) {
        // Para modo dropdown, solo actualizamos la selección
        // La sincronización se hace al cambiar de modo
        this.markChanges();
    }

    movePlayerToZone(player, targetZone, animate = true) {
        const playerElement = player.closest ? player.closest('[data-jugador-id]') : player;
        if (!playerElement || !targetZone) return;
        
        const jugadorId = playerElement.dataset.jugadorId;
        const playerData = this.playersData.get(jugadorId);
        
        if (!playerData) return;
        
        // Crear nuevo elemento según la zona
        const newPlayer = this.createPlayerElementForZone(playerData, targetZone);
        
        // Añadir a la zona
        targetZone.appendChild(newPlayer);
        
        // Remover elemento original
        playerElement.remove();
        
        // Animación de entrada
        if (animate) {
            this.animatePlayerEntry(newPlayer);
        }
        
        // Actualizar estado
        this.markChanges();
        this.updateCounters();
        
        // Sincronizar con dropdown mode
        if (this.currentMode === 'drag') {
            this.syncDropdownFromDrag();
        }
    }

    createPlayerElementForZone(playerData, targetZone) {
        let element;
        
        if (targetZone.id === 'bench-players') {
            element = this.createBenchPlayerElement(playerData);
        } else {
            const teamClass = targetZone.id === 'local-players' ? 'local-player' : 'visitante-player';
            element = this.createFieldPlayerElement(playerData, teamClass);
        }
        
        element.dataset.jugadorId = playerData.id;
        element.draggable = true;
        element.tabIndex = 0;
        
        return element;
    }

    createFieldPlayerElement(playerData, teamClass) {
        const element = document.createElement('div');
        element.className = `field-player ${teamClass}`;
        
        // Asegurar que el nombre se muestre siempre
        const displayName = playerData.name || 'Jugador';
        const shortName = displayName.length > 10 ? 
            displayName.substring(0, 8) + '...' : 
            displayName;
            
        // Asegurar posición
        const displayPosition = playerData.position ? 
            (playerData.position.length > 3 ? 
                playerData.position.substring(0, 3).toUpperCase() : 
                playerData.position.toUpperCase()) : 'JUG';
        
        element.innerHTML = `
            <div class="player-avatar">
                <img src="${playerData.avatar || '/static/images/avatar_default.png'}" 
                     alt="${displayName}" 
                     onerror="this.src='/static/images/avatar_default.png'">
            </div>
            <div class="player-name" title="${displayName}">${shortName}</div>
            <div class="player-position">${displayPosition}</div>
            ${playerData.isCreator ? '<div class="creator-badge"><i class="fas fa-crown"></i></div>' : ''}
        `;
        
        return element;
    }

    createBenchPlayerElement(playerData) {
        const element = document.createElement('div');
        element.className = 'bench-player';
        
        // Asegurar que el nombre se muestre siempre
        const displayName = playerData.name || 'Jugador';
        const displayPosition = playerData.position || 'Jugador';
        
        element.innerHTML = `
            <div class="player-avatar">
                <img src="${playerData.avatar || '/static/images/avatar_default.png'}" 
                     alt="${displayName}" 
                     onerror="this.src='/static/images/avatar_default.png'">
            </div>
            <div class="player-info">
                <div class="player-name" title="${displayName}">${displayName}</div>
                <div class="player-position">${displayPosition}</div>
            </div>
            ${playerData.isCreator ? '<div class="creator-badge"><i class="fas fa-crown"></i></div>' : ''}
        `;
        return element;
    }

    syncDropdownFromDrag() {
        // Sincronizar dropdowns con el estado actual del drag mode
        document.querySelectorAll('.team-select').forEach(select => {
            const jugadorId = select.dataset.jugador;
            const currentTeam = this.getCurrentPlayerTeam(jugadorId);
            select.value = currentTeam;
        });
        
        this.updateDropdownSummary();
    }

    updateCounters() {
        const localCount = document.querySelectorAll('#local-players [data-jugador-id]').length;
        const visitanteCount = document.querySelectorAll('#visitante-players [data-jugador-id]').length;
        const benchCount = document.querySelectorAll('#bench-players [data-jugador-id]').length;
        
        // Actualizar contadores en drag mode
        const localCounter = document.querySelector('.local-counter');
        const visitanteCounter = document.querySelector('.visitante-counter');
        const benchCounter = document.querySelector('.bench-counter');
        
        if (localCounter) {
            localCounter.textContent = localCount;
            this.animateCounterUpdate(localCounter);
        }
        if (visitanteCounter) {
            visitanteCounter.textContent = visitanteCount;
            this.animateCounterUpdate(visitanteCounter);
        }
        if (benchCounter) {
            benchCounter.textContent = benchCount;
            this.animateCounterUpdate(benchCounter);
        }
    }

    animateCounterUpdate(counter) {
        if (typeof counter === 'string') {
            counter = document.getElementById(counter);
        }
        if (!counter) return;
        
        counter.classList.add('updated');
        setTimeout(() => {
            counter.classList.remove('updated');
        }, 300);
    }

    // ===== VISUAL FEEDBACK =====
    updateDragPreview(element, x, y) {
        if (!this.dragPreview || !element) return;
        
        // Clonar el elemento y prepararlo para el preview
        const clone = element.cloneNode(true);
        clone.classList.remove('dragging');
        clone.classList.add('drag-preview-element');
        
        this.dragPreview.innerHTML = '';
        this.dragPreview.appendChild(clone);
        
        this.dragPreview.style.left = `${x - 30}px`;
        this.dragPreview.style.top = `${y - 40}px`;
        this.dragPreview.style.zIndex = '10000';
    }

    showDragPreview() {
        if (this.dragPreview) {
            this.dragPreview.style.display = 'block';
            this.dragPreview.style.opacity = '0.9';
            this.dragPreview.style.pointerEvents = 'none';
        }
    }

    hideDragPreview() {
        if (this.dragPreview) {
            this.dragPreview.style.display = 'none';
            this.dragPreview.style.opacity = '0';
            this.dragPreview.style.left = '-1000px';
            this.dragPreview.style.top = '-1000px';
            this.dragPreview.innerHTML = '';
        }
    }

    showTouchFeedback(x, y) {
        if (!this.touchFeedback) return;
        
        this.touchFeedback.style.left = `${x - 50}px`;
        this.touchFeedback.style.top = `${y - 50}px`;
        this.touchFeedback.classList.add('active');
    }

    updateTouchFeedback(x, y) {
        if (!this.touchFeedback) return;
        
        this.touchFeedback.style.left = `${x - 50}px`;
        this.touchFeedback.style.top = `${y - 50}px`;
    }

    hideTouchFeedback() {
        if (this.touchFeedback) {
            this.touchFeedback.classList.remove('active');
        }
    }

    addDragVisualFeedback() {
        document.body.classList.add('dragging-active');
        
        const dropZones = document.querySelectorAll('.players-drop-zone, .bench-players');
        dropZones.forEach(zone => {
            if (this.canDropInZone(zone)) {
                zone.classList.add('valid-drop-zone');
            }
        });
    }

    removeDragVisualFeedback() {
        document.body.classList.remove('dragging-active');
        document.querySelectorAll('.valid-drop-zone, .drag-over').forEach(zone => {
            zone.classList.remove('valid-drop-zone', 'drag-over');
        });
    }

    showDropAnimation(x, y) {
        const animation = document.createElement('div');
        animation.className = 'drop-animation';
        animation.style.cssText = `
            position: fixed;
            left: ${x - 25}px;
            top: ${y - 25}px;
            width: 50px;
            height: 50px;
            border-radius: 50%;
            background: radial-gradient(circle, var(--match-primary) 0%, transparent 70%);
            pointer-events: none;
            z-index: 9999;
            animation: dropPulse 0.6s ease-out forwards;
        `;
        
        document.body.appendChild(animation);
        setTimeout(() => animation.remove(), 600);
    }

    animatePlayerEntry(player) {
        player.style.opacity = '0';
        player.style.transform = 'scale(0.8)';
        
        requestAnimationFrame(() => {
            player.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
            player.style.opacity = '1';
            player.style.transform = 'scale(1)';
        });
    }

    endDrag() {
        // Limpiar elemento arrastrado
        if (this.draggedElement) {
            this.draggedElement.classList.remove('dragging');
        }
        
        // Resetear estados
        this.draggedElement = null;
        this.isDragging = false;
        
        // Ocultar previews y feedback
        this.hideDragPreview();
        this.hideTouchFeedback();
        this.removeDragVisualFeedback();
        
        // Limpiar todas las clases de drag
        document.querySelectorAll('.dragging, .drag-over, .valid-drop-zone').forEach(el => {
            el.classList.remove('dragging', 'drag-over', 'valid-drop-zone');
        });
        
        // Limpiar body classes
        document.body.classList.remove('dragging-active');
    }

    // ===== SAVE FUNCTIONALITY =====
    setupSaveButton() {
        this.saveButton = document.getElementById('saveTeamsBtn');
        if (this.saveButton) {
            this.saveButton.addEventListener('click', this.saveTeamAssignments.bind(this));
        }
    }

    markChanges() {
        this.hasChanges = true;
        this.updateSaveButton();
    }

    updateSaveButton() {
        if (!this.saveButton) return;
        
        if (this.hasChanges) {
            this.saveButton.disabled = false;
            this.saveButton.classList.add('has-changes');
        } else {
            this.saveButton.disabled = true;
            this.saveButton.classList.remove('has-changes');
        }
    }

    saveTeamAssignments() {
        if (!this.hasChanges) return;
        
        // Recopilar datos según el modo actual
        let localPlayers, visitantePlayers;
        
        if (this.currentMode === 'dropdown') {
            localPlayers = this.getPlayersFromDropdown('local');
            visitantePlayers = this.getPlayersFromDropdown('visitante');
        } else {
            localPlayers = this.getPlayersFromDrag('local-players');
            visitantePlayers = this.getPlayersFromDrag('visitante-players');
        }
        
        // Actualizar campos hidden
        const localInput = document.getElementById('localPlayersInput');
        const visitanteInput = document.getElementById('visitantePlayersInput');
        
        if (localInput) localInput.value = localPlayers.join(',');
        if (visitanteInput) visitanteInput.value = visitantePlayers.join(',');
        
        // Mostrar indicador de guardado
        this.showSaveIndicator();
        
        // Enviar formulario
        const form = document.getElementById('teamAssignmentForm');
        if (form) {
            form.submit();
        }
    }

    getPlayersFromDropdown(team) {
        const players = [];
        document.querySelectorAll('.team-select').forEach(select => {
            if (select.value === team) {
                players.push(select.dataset.jugador);
            }
        });
        return players;
    }

    getPlayersFromDrag(zoneId) {
        const zone = document.getElementById(zoneId);
        if (!zone) return [];
        
        return Array.from(zone.querySelectorAll('[data-jugador-id]'))
            .map(player => player.dataset.jugadorId);
    }

    showSaveIndicator() {
        if (!this.saveButton) return;
        
        const originalText = this.saveButton.innerHTML;
        this.saveButton.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Guardando...';
        this.saveButton.disabled = true;
        this.saveButton.classList.add('loading');
        
        setTimeout(() => {
            this.saveButton.innerHTML = '<i class="fas fa-check me-2"></i>Guardado';
            this.saveButton.classList.remove('loading');
            this.saveButton.classList.add('save-success');
            
            setTimeout(() => {
                this.saveButton.innerHTML = originalText;
                this.saveButton.classList.remove('save-success');
                this.hasChanges = false;
                this.updateSaveButton();
            }, 1000);
        }, 1500);
    }

    // ===== KEYBOARD SUPPORT =====
    setupKeyboardSupport() {
        document.addEventListener('keydown', (e) => {
            const activeElement = document.activeElement;
            if (!activeElement || !activeElement.closest('[data-jugador-id]')) return;
            
            switch (e.key) {
                case 'Enter':
                case ' ':
                    e.preventDefault();
                    this.handleKeyboardPlayerAction(activeElement);
                    break;
                case 'ArrowLeft':
                    e.preventDefault();
                    this.movePlayerWithKeyboard(activeElement, 'local');
                    break;
                case 'ArrowRight':
                    e.preventDefault();
                    this.movePlayerWithKeyboard(activeElement, 'visitante');
                    break;
                case 'ArrowDown':
                    e.preventDefault();
                    this.movePlayerWithKeyboard(activeElement, 'bench');
                    break;
            }
        });
    }

    handleKeyboardPlayerAction(element) {
        // Highlight player for keyboard users
        element.classList.toggle('keyboard-selected');
    }

    movePlayerWithKeyboard(element, targetTeam) {
        if (this.currentMode !== 'drag') return;
        
        const player = element.closest('[data-jugador-id]');
        if (!player) return;
        
        const zoneId = targetTeam === 'bench' ? 'bench-players' : `${targetTeam}-players`;
        const targetZone = document.getElementById(zoneId);
        
        if (targetZone && this.canDropInZone(targetZone)) {
            this.movePlayerToZone(player, targetZone);
            
            // Mover foco al nuevo elemento
            setTimeout(() => {
                const newPlayer = targetZone.querySelector(`[data-jugador-id="${player.dataset.jugadorId}"]`);
                if (newPlayer) {
                    newPlayer.focus();
                }
            }, 100);
        }
    }

    // ===== RESET FUNCTIONALITY =====
    resetToOriginal() {
        // Restablecer posiciones originales
        this.originalPositions.forEach((data, jugadorId) => {
            const currentPlayer = document.querySelector(`[data-jugador-id="${jugadorId}"]`);
            if (currentPlayer) {
                currentPlayer.remove();
            }
            
            const originalTeam = data.team;
            const zoneId = originalTeam === 'bench' ? 'bench-players' : `${originalTeam}-players`;
            const targetZone = document.getElementById(zoneId);
            
            if (targetZone) {
                const playerData = this.playersData.get(jugadorId);
                if (playerData) {
                    const restoredPlayer = this.createPlayerElementForZone(playerData, targetZone);
                    targetZone.appendChild(restoredPlayer);
                }
            }
        });
        
        // Resetear dropdowns
        this.updateDropdownSelections();
        this.updateDropdownSummary();
        
        // Resetear auto mode
        const autoResult = document.getElementById('autoResult');
        if (autoResult) {
            autoResult.style.display = 'none';
        }
        
        this.hasChanges = false;
        this.updateSaveButton();
        this.updateCounters();
    }
}

// ===== CSS ANIMATIONS =====
const style = document.createElement('style');
style.textContent = `
    @keyframes dropPulse {
        0% {
            opacity: 1;
            transform: scale(0);
        }
        50% {
            opacity: 0.8;
            transform: scale(1);
        }
        100% {
            opacity: 0;
            transform: scale(1.5);
        }
    }
    
    .dragging-active .valid-drop-zone {
        animation: pulseGlow 1.5s ease-in-out infinite;
    }
    
    @keyframes pulseGlow {
        0%, 100% {
            box-shadow: 0 0 0 0 rgba(0, 212, 170, 0.4);
        }
        50% {
            box-shadow: 0 0 0 10px rgba(0, 212, 170, 0.1);
        }
    }
    
    .btn.has-changes {
        animation: buttonPulse 2s ease-in-out infinite;
    }
    
    @keyframes buttonPulse {
        0%, 100% {
            transform: scale(1);
        }
        50% {
            transform: scale(1.05);
        }
    }

    .keyboard-selected {
        outline: 2px solid var(--match-primary);
        outline-offset: 2px;
    }
`;
document.head.appendChild(style);

// ===== INITIALIZATION =====
document.addEventListener('DOMContentLoaded', function() {
    // Inicializar solo si estamos en la vista de creador
    if (document.querySelector('.team-management-section')) {
        window.advancedTeamManager = new AdvancedTeamAssignmentManager();
        
        // Añadir botón de reset
        const resetBtn = document.createElement('button');
        resetBtn.className = 'btn btn-outline btn-sm ms-2';
        resetBtn.innerHTML = '<i class="fas fa-undo me-2"></i>Restablecer';
        resetBtn.addEventListener('click', () => {
            if (confirm('¿Estás seguro de que quieres restablecer la asignación de equipos?')) {
                window.advancedTeamManager.resetToOriginal();
            }
        });
        
        const saveBtn = document.getElementById('saveTeamsBtn');
        if (saveBtn && saveBtn.parentNode) {
            saveBtn.parentNode.insertBefore(resetBtn, saveBtn.nextSibling);
        }
    }
    
    // Configurar otras funcionalidades
    setupPlayerActions();
    setupEntryAnimations();
});

function setupPlayerActions() {
    const joinBtn = document.getElementById('joinMatchBtn');
    const leaveBtn = document.getElementById('leaveMatchBtn');
    
    if (joinBtn) {
        joinBtn.addEventListener('click', function() {
            // Aquí iría la lógica para unirse al partido
            console.log('Unirse al partido');
        });
    }
    
    if (leaveBtn) {
        leaveBtn.addEventListener('click', function() {
            if (confirm('¿Estás seguro de que quieres abandonar este partido?')) {
                // Aquí iría la lógica para abandonar el partido
                console.log('Abandonar partido');
            }
        });
    }
}

function setupEntryAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.animationPlayState = 'running';
            }
        });
    }, observerOptions);
    
    document.querySelectorAll('.info-item, .player-card, .field-player, .bench-player').forEach(el => {
        observer.observe(el);
    });
}