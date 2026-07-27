/**
 * Current Jobs View  (cursor controller)
 *
 * Table (airport-style) board with auto-scroll + periodic reload.
 *
 * Cursor navigation (Android TV remote / keyboard). This screen is the LEFT of
 * a two-screen pair (Current-Jobs | Next-Jobs) and owns the remote:
 *   - ArrowUp / ArrowDown  : move the cursor between rows on the ACTIVE screen.
 *   - ArrowRight           : move the cursor onto the Next-Jobs screen (right).
 *   - ArrowLeft            : move the cursor back to the Current-Jobs screen.
 *
 * The selected operation pk is POSTed (300ms debounced) to the drawing cursor
 * API, which drives BOTH the Drawing-Monitor and the Next-Jobs highlight over
 * the existing WebSocket. When the cursor is on Current-Jobs we highlight the
 * row locally; when it moves to Next-Jobs we clear the local highlight (that
 * screen highlights itself via the socket).
 *
 * Cursor position is server-side, in-memory only (90s auto-timeout) - NOT in
 * the DB. On load we restore it from cursor-status so it survives the periodic
 * reload. Next-Jobs rows are fetched from the cursor next-rows API so the
 * controller knows what to navigate on the right-hand screen.
 */

(function() {
    'use strict';

    // --- Cursor / drawing API config ---
    const SET_CURSOR_URL = '/monitoring/api/drawing/set-cursor/';
    const CURSOR_STATUS_URL = '/monitoring/api/drawing/cursor-status/';
    const NEXT_ROWS_URL = '/monitoring/api/cursor/next-rows/';
    const DEBOUNCE_DELAY = 300;    // ms - only POST after the cursor settles on a row
    const CURSOR_IDLE_MS = 90000;  // mirror server timeout; then release local cursor
    const NEXT_ROWS_REFRESH_MS = 60000; // keep the next-jobs list fresh

    // Current view state: 'card' or 'table'
    let currentView = 'table';

    // DOM elements
    const cardView = document.getElementById('card-view');
    const tableView = document.getElementById('table-view');
    let boardBody = null;  // Will be set when table view is shown

    // Auto-scroll configuration
    const SCROLL_SPEED = 1; // pixels per frame (lower = slower, smoother)
    const PAUSE_DURATION = 3000; // milliseconds to pause at top/bottom
    const SCROLL_FPS = 60; // frames per second for smooth scrolling
    const RELOAD_INTERVAL = 12000; // milliseconds between reload checks

    // Auto-scroll state
    let autoScrollInterval = null;
    let autoScrollTimeout = null;
    let scrollDirection = 'down'; // 'down' or 'up'
    let isPaused = false;
    let reloadCheckInterval = null;
    let reloadPending = false; // Flag to indicate reload is waiting for top position
    let hasScrolledDown = false; // Track if we've scrolled down at least once since page load

    // Cursor state
    let currentRows = [];       // ordered operation pks (strings) on THIS screen
    let nextRows = [];          // ordered operation pks (strings) on the Next-Jobs screen
    let activeScreen = 'current'; // 'current' | 'next'
    let cursorIndex = -1;       // index into the active screen's list; -1 = no cursor
    let cursorActive = false;   // when true, auto-scroll is paused
    let pendingPk = null;
    let debounceTimer = null;
    let idleTimer = null;

    /**
     * Read the csrftoken cookie for POSTs.
     */
    function getCSRFToken() {
        const match = document.cookie.match(/(?:^|;\s*)csrftoken=([^;]+)/);
        return match ? decodeURIComponent(match[1]) : '';
    }

    /**
     * Stop auto-scroll
     */
    function stopAutoScroll() {
        if (autoScrollInterval) {
            clearInterval(autoScrollInterval);
            autoScrollInterval = null;
        }
        if (autoScrollTimeout) {
            clearTimeout(autoScrollTimeout);
            autoScrollTimeout = null;
        }
        isPaused = false;
    }

    /**
     * Start auto-scroll after a pause
     */
    function startAutoScrollAfterPause(delay) {
        isPaused = true;
        autoScrollTimeout = setTimeout(() => {
            isPaused = false;
            startAutoScroll();
        }, delay);
    }

    /**
     * Perform the scrolling animation
     */
    function performScroll() {
        // Freeze scrolling while the cursor is active so the highlighted row
        // stays put under the operator's control.
        if (cursorActive || isPaused || currentView !== 'table' || !boardBody) {
            return;
        }

        const currentScroll = boardBody.scrollTop;
        const maxScroll = boardBody.scrollHeight - boardBody.clientHeight;

        if (scrollDirection === 'down') {
            // Scrolling down
            if (currentScroll > 10) {
                hasScrolledDown = true; // Mark that we've scrolled down
            }

            if (currentScroll >= maxScroll - 5) { // -5 for slight tolerance
                // Reached bottom, pause then reverse
                stopAutoScroll();
                scrollDirection = 'up';
                startAutoScrollAfterPause(PAUSE_DURATION);
            } else {
                boardBody.scrollTop += SCROLL_SPEED;
            }
        } else {
            // Scrolling up
            if (currentScroll <= 5) { // 5 for slight tolerance
                // Reached top - check if reload is needed
                if (reloadPending && hasScrolledDown) {
                    // Reset flags BEFORE reload to prevent infinite loop
                    hasScrolledDown = false;
                    reloadPending = false;
                    location.reload();
                    return;
                }

                // Otherwise, pause then reverse
                stopAutoScroll();
                scrollDirection = 'down';
                hasScrolledDown = false; // Reset for next cycle
                startAutoScrollAfterPause(PAUSE_DURATION);
            } else {
                boardBody.scrollTop -= SCROLL_SPEED;
            }
        }
    }

    /**
     * Start auto-scroll
     */
    function startAutoScroll() {
        stopAutoScroll(); // Clear any existing intervals
        const intervalDelay = 1000 / SCROLL_FPS;
        autoScrollInterval = setInterval(performScroll, intervalDelay);
    }

    /**
     * Switch to card view
     */
    function showCardView() {
        if (cardView && tableView) {
            stopAutoScroll();
            cardView.style.display = 'block';
            tableView.style.display = 'none';
            currentView = 'card';
        }
    }

    /**
     * Switch to table view
     */
    function showTableView() {
        if (cardView && tableView) {
            cardView.style.display = 'none';
            tableView.style.display = 'block';
            currentView = 'table';

            // Get the board-body element after view is shown
            setTimeout(() => {
                boardBody = document.querySelector('.board-body');
                if (boardBody) {
                    // Reset scroll to top
                    boardBody.scrollTop = 0;
                    scrollDirection = 'down';

                    // Reset reload protection on fresh page load
                    reloadPending = false;
                    hasScrolledDown = false; // Must scroll down before reload can happen

                    // Start auto-scroll
                    startAutoScrollAfterPause(PAUSE_DURATION);
                }
            }, 100);
        }
    }

    // ------------------------------------------------------------------
    // Cursor navigation
    // ------------------------------------------------------------------

    /**
     * Build the ordered list of operation pks from THIS screen's table rows.
     * Only rows that carry a job get a data-operation-pk, so idle rows are
     * naturally skipped.
     */
    function buildCurrentRows() {
        const rows = document.querySelectorAll('.board-body .board-row[data-operation-pk]');
        currentRows = Array.from(rows).map(r => r.dataset.operationPk);
    }

    /**
     * Fetch the ordered Next-Jobs rows (operation pks) so the controller can
     * navigate onto the right-hand screen.
     */
    async function fetchNextRows() {
        try {
            const res = await fetch(NEXT_ROWS_URL);
            const data = await res.json();
            nextRows = (data.rows || [])
                .filter(r => r.operation_pk != null)
                .map(r => String(r.operation_pk));
        } catch (err) {
            console.error('Failed to fetch next rows:', err);
        }
    }

    function activeList() {
        return activeScreen === 'next' ? nextRows : currentRows;
    }

    /**
     * Apply the visual highlight to the row for the given pk on THIS screen
     * (and clear others). Scrolls it into view. Does NOT send to the server.
     */
    function highlightRow(pk) {
        document.querySelectorAll('.board-row.cursor-current').forEach(el => {
            el.classList.remove('cursor-current');
        });
        if (pk == null) return;
        const row = document.querySelector(`.board-row[data-operation-pk="${pk}"]`);
        if (row) {
            row.classList.add('cursor-current');
            row.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    }

    /**
     * Apply the current cursorIndex on the active screen: highlight (locally if
     * on Current-Jobs, cleared if on Next-Jobs) and schedule the debounced POST.
     */
    function applySelection() {
        const list = activeList();
        if (list.length === 0) return;
        cursorIndex = Math.max(0, Math.min(cursorIndex, list.length - 1));
        const pk = list[cursorIndex];

        cursorActive = true;
        // Current-Jobs highlights its own row; when the cursor is on Next-Jobs,
        // clear the local highlight (that screen highlights itself via socket).
        highlightRow(activeScreen === 'current' ? pk : null);
        resetIdleTimer();

        if (debounceTimer) clearTimeout(debounceTimer);
        pendingPk = pk;
        debounceTimer = setTimeout(() => {
            sendCursorUpdate(pendingPk);
            debounceTimer = null;
        }, DEBOUNCE_DELAY);
    }

    /**
     * POST the operation pk to the drawing cursor API.
     */
    function sendCursorUpdate(pk) {
        fetch(SET_CURSOR_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify({ operation_id: parseInt(pk, 10) })
        }).catch(err => console.error('Failed to set cursor:', err));
    }

    /**
     * Release the local cursor after inactivity. Mirrors the server-side 90s
     * timeout. We do not POST null - the server times out on its own, returning
     * the Drawing-Monitor to the logo.
     */
    function releaseCursor() {
        cursorActive = false;
        activeScreen = 'current';
        cursorIndex = -1;
        highlightRow(null);
    }

    function resetIdleTimer() {
        if (idleTimer) clearTimeout(idleTimer);
        idleTimer = setTimeout(releaseCursor, CURSOR_IDLE_MS);
    }

    /**
     * Handle keyboard / D-pad navigation.
     */
    function handleKeyPress(e) {
        const key = e.key;

        if (key === 'ArrowDown') {
            e.preventDefault();
            if (activeScreen === 'current') buildCurrentRows();
            cursorIndex = cursorIndex < 0 ? 0 : cursorIndex + 1;
            applySelection();
        } else if (key === 'ArrowUp') {
            e.preventDefault();
            if (activeScreen === 'current') buildCurrentRows();
            cursorIndex = cursorIndex < 0 ? 0 : cursorIndex - 1;
            applySelection();
        } else if (key === 'ArrowRight') {
            e.preventDefault();
            // Move onto the Next-Jobs screen (preserve row index, clamped).
            if (activeScreen === 'current' && nextRows.length > 0) {
                activeScreen = 'next';
                applySelection();
            }
        } else if (key === 'ArrowLeft') {
            e.preventDefault();
            // Move back onto the Current-Jobs screen (preserve row index, clamped).
            if (activeScreen === 'next') {
                activeScreen = 'current';
                buildCurrentRows();
                applySelection();
            }
        }
    }

    /**
     * On load, restore the cursor from the server (survives periodic reload).
     * Determines which screen holds the active operation.
     */
    async function restoreCursor() {
        try {
            const res = await fetch(CURSOR_STATUS_URL);
            const data = await res.json();
            if (!data.is_active || data.operation_id == null) return;

            buildCurrentRows();
            const idStr = String(data.operation_id);

            let idx = currentRows.indexOf(idStr);
            if (idx >= 0) {
                activeScreen = 'current';
                cursorIndex = idx;
                cursorActive = true;
                highlightRow(idStr);
                resetIdleTimer();
                return;
            }
            idx = nextRows.indexOf(idStr);
            if (idx >= 0) {
                activeScreen = 'next';
                cursorIndex = idx;
                cursorActive = true;
                highlightRow(null); // cursor is on the Next-Jobs TV
                resetIdleTimer();
            }
        } catch (err) {
            console.error('Failed to restore cursor:', err);
        }
    }

    /**
     * Mark that reload is needed (will execute when scroll reaches top)
     */
    function scheduleReload() {
        if (!reloadPending) {
            reloadPending = true;
            // Stop scheduling more reloads until this one completes
            if (reloadCheckInterval) {
                clearInterval(reloadCheckInterval);
                reloadCheckInterval = null;
            }
        }
    }

    /**
     * Initialize the view
     */
    function init() {
        if (/Android|SmartTV|TV|AFTT|AFTM/i.test(navigator.userAgent)) {
            document.body.classList.add('kiosk-device');
        }

        // Set initial view (table view)
        showTableView();

        // Build the cursor lists, then restore any active cursor from the server
        buildCurrentRows();
        fetchNextRows().then(restoreCursor);
        setInterval(fetchNextRows, NEXT_ROWS_REFRESH_MS);

        // Add keyboard event listener
        document.addEventListener('keydown', handleKeyPress);

        // Schedule reload - will execute when scroll reaches top
        reloadCheckInterval = setInterval(scheduleReload, RELOAD_INTERVAL);
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();
