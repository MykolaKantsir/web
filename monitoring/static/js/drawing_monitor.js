/**
 * Drawing Monitor Display System
 * Real-time manufacturing drawing display with WebSocket support
 *
 * Features:
 * - Preloads all drawings on page load for instant switching
 * - Polls cursor status every 10 seconds
 * - Connects to WebSocket when cursor becomes active
 * - Displays drawing in full screen (from preloaded cache)
 * - Returns to logo screen when inactive
 */

(function() {
    'use strict';

    // Configuration
    const POLL_INTERVAL = 10000; // Check cursor status every 10 seconds
    const WS_RECONNECT_DELAY = 1000;

    // State
    let ws = null;
    let cursorCheckInterval = null;
    let currentOperationId = null;
    let drawingsCache = {}; // {operation_id: {name, drawing_base64}}

    // DOM Elements
    const logoScreen = document.getElementById('logo-screen');
    const drawingScreen = document.getElementById('drawing-screen');
    const drawingImage = document.getElementById('drawing-image');
    const operationName = document.getElementById('operation-name');
    const noDrawingMsg = document.getElementById('no-drawing');

    /**
     * Preload all drawings on page load for instant switching
     * Fetches ~12MB once, avoids sending 400KB per cursor change
     */
    async function preloadDrawings() {
        try {
            console.log('Preloading drawings...');
            const response = await fetch('/monitoring/api/drawing/all/');
            const data = await response.json();
            drawingsCache = data.drawings || {};
            console.log(`Preloaded ${Object.keys(drawingsCache).length} drawings`);
        } catch (error) {
            console.error('Failed to preload drawings:', error);
            // Continue anyway - WebSocket can still work without cache
        }
    }

    /**
     * Check if cursor is active (polling)
     * Polls the server every 10 seconds to check cursor status
     */
    async function checkCursorStatus() {
        try {
            const response = await fetch('/monitoring/api/drawing/cursor-status/');
            const data = await response.json();

            if (data.is_active && !ws) {
                // Cursor became active - connect WebSocket
                connectWebSocket();
            } else if (!data.is_active && ws) {
                // Cursor became inactive - disconnect and show logo
                disconnectWebSocket();
                showLogo();
            }
        } catch (error) {
            console.error('Failed to check cursor status:', error);
        }
    }

    /**
     * Connect to WebSocket for real-time drawing updates
     * WebSocket provides <500ms latency for cursor changes
     */
    function connectWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/drawing/`;

        ws = new WebSocket(wsUrl);

        ws.onopen = () => {
            console.log('WebSocket connected');
        };

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);

            if (data.type === 'drawing') {
                showDrawing(data);
            }
        };

        ws.onerror = (error) => {
            console.error('WebSocket error:', error);
        };

        ws.onclose = () => {
            console.log('WebSocket closed');
            ws = null;
        };
    }

    /**
     * Disconnect WebSocket connection
     */
    function disconnectWebSocket() {
        if (ws) {
            ws.close();
            ws = null;
        }
    }

    /**
     * Show logo screen (idle state)
     */
    function showLogo() {
        drawingScreen.classList.remove('active');
        logoScreen.style.display = 'flex';
        currentOperationId = null;
    }

    /**
     * Show drawing screen with operation details
     * Looks up drawing from preloaded cache for instant display
     * @param {Object} data - Drawing data from WebSocket (operation_id, operation_name)
     */
    function showDrawing(data) {
        const opId = String(data.operation_id);
        const cached = drawingsCache[opId];

        // Use cached name if available, fallback to WebSocket data
        const displayName = cached?.name || data.operation_name || 'Operation';
        operationName.textContent = displayName;

        // Get drawing from cache
        const drawingBase64 = cached?.drawing_base64;

        if (drawingBase64) {
            drawingImage.src = drawingBase64;
            drawingImage.style.display = 'block';
            noDrawingMsg.style.display = 'none';
        } else {
            drawingImage.style.display = 'none';
            noDrawingMsg.style.display = 'block';
            console.warn(`No cached drawing for operation ${opId}`);
        }

        logoScreen.style.display = 'none';
        drawingScreen.classList.add('active');

        currentOperationId = data.operation_id;
    }

    /**
     * Initialize the drawing monitor
     */
    async function init() {
        // Preload all drawings first
        await preloadDrawings();

        // Start cursor status polling
        cursorCheckInterval = setInterval(checkCursorStatus, POLL_INTERVAL);
        checkCursorStatus(); // Initial check
    }

    // Start when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();
