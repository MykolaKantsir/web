/**
 * Next Jobs View
 *
 * Airport-style table board with auto-scroll + AJAX change polling.
 *
 * Cursor receiver (Phase 2): this screen sits to the RIGHT of Current-Jobs.
 * The Current-Jobs remote can move the cursor onto this screen; the cursor
 * position is broadcast over the existing drawing WebSocket (ws/drawing/).
 * This page listens, highlights the row whose operation pk matches, and
 * pauses auto-scroll while a row is highlighted. It never sends anything -
 * it is a pure display (the remote lives on the Current-Jobs TV).
 */

(function() {
    'use strict';

    // View state
    let currentView = 'table';
    const cardView = document.getElementById('card-view');
    const tableView = document.getElementById('table-view');
    let boardBody = null;

    // Auto-scroll configuration
    const SCROLL_SPEED = 1;
    const PAUSE_DURATION = 3000;
    const SCROLL_FPS = 60;

    // Auto-scroll state
    let autoScrollInterval = null;
    let autoScrollTimeout = null;
    let scrollDirection = 'down';
    let isPaused = false;

    // AJAX update state
    let isRequestInProgress = false;

    // Cursor / WebSocket state
    const CURSOR_STATUS_URL = '/monitoring/api/drawing/cursor-status/';
    const POLL_INTERVAL = 10000;      // check cursor status every 10s
    let ws = null;
    let cursorCheckInterval = null;
    let highlightActive = false;      // pauses auto-scroll while a row is highlighted

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
        // Freeze scrolling while the cursor highlights a row on this screen.
        if (highlightActive || isPaused || currentView !== 'table' || !boardBody) {
            return;
        }

        const currentScroll = boardBody.scrollTop;
        const maxScroll = boardBody.scrollHeight - boardBody.clientHeight;

        if (scrollDirection === 'down') {
            // Scrolling down
            if (currentScroll >= maxScroll - 5) {
                // Reached bottom, pause then reverse
                stopAutoScroll();
                scrollDirection = 'up';
                startAutoScrollAfterPause(PAUSE_DURATION);
            } else {
                boardBody.scrollTop += SCROLL_SPEED;
            }
        } else {
            // Scrolling up
            if (currentScroll <= 5) {
                // Reached top, pause then reverse
                stopAutoScroll();
                scrollDirection = 'down';
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
        stopAutoScroll();

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
                    // Apply row-no-operation class based on job name
                    const rows = boardBody.querySelectorAll('.board-row');
                    rows.forEach(row => {
                        const jobName = row.getAttribute('data-job-name');
                        if (jobName === 'No operation') {
                            row.classList.add('row-no-operation');
                        }
                    });

                    boardBody.scrollTop = 0;
                    scrollDirection = 'down';
                    startAutoScrollAfterPause(PAUSE_DURATION);
                }
            }, 100);
        }
    }

    // ==========================================
    // Cursor highlight (received over WebSocket)
    // ==========================================

    /**
     * Highlight the row for the given operation pk. If this board has no such
     * row (cursor is on another screen), clear any highlight and let auto-scroll
     * resume.
     */
    function highlightRow(pk) {
        document.querySelectorAll('.board-row.cursor-current').forEach(el => {
            el.classList.remove('cursor-current');
        });

        const row = pk != null
            ? document.querySelector(`.board-row[data-operation-pk="${pk}"]`)
            : null;

        if (row) {
            row.classList.add('cursor-current');
            highlightActive = true;
            row.scrollIntoView({ behavior: 'smooth', block: 'center' });
        } else {
            highlightActive = false;
        }
    }

    function clearHighlight() {
        highlightRow(null);
    }

    /**
     * Connect to the drawing WebSocket to receive cursor moves.
     */
    function connectWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/drawing/`;

        ws = new WebSocket(wsUrl);

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.type === 'drawing') {
                highlightRow(String(data.operation_id));
            }
        };

        ws.onerror = (error) => {
            console.error('WebSocket error:', error);
        };

        ws.onclose = () => {
            ws = null;
        };
    }

    function disconnectWebSocket() {
        if (ws) {
            ws.close();
            ws = null;
        }
    }

    /**
     * Poll cursor status: open the socket while a cursor is active, close it and
     * clear the highlight when the cursor goes inactive (times out).
     */
    async function checkCursorStatus() {
        try {
            const response = await fetch(CURSOR_STATUS_URL);
            const data = await response.json();

            if (data.is_active && !ws) {
                connectWebSocket();
            } else if (!data.is_active && ws) {
                disconnectWebSocket();
                clearHighlight();
            } else if (!data.is_active) {
                clearHighlight();
            }
        } catch (error) {
            console.error('Failed to check cursor status:', error);
        }
    }

    // ==========================================
    // AJAX Update Functions (Original Code)
    // ==========================================

    function showLoading() {
        let loadingDiv = document.getElementById("loading");
        if (loadingDiv) {
            loadingDiv.classList.remove("hidden");
        }
    }

    function hideLoading() {
        let loadingDiv = document.getElementById("loading");
        if (loadingDiv) {
            loadingDiv.classList.add("hidden");
        }
    }

    function showError() {
        let errorDiv = document.getElementById("error");
        if (errorDiv) {
            errorDiv.classList.remove("hidden");
        }
    }

    function hideError() {
        let errorDiv = document.getElementById("error");
        if (errorDiv) {
            errorDiv.classList.add("hidden");
        }
    }

    function getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]').value;
    }

    function checkForUpdates() {
        if (isRequestInProgress) {
            return;
        }

        isRequestInProgress = true;

        let data = [];
        $(".job-card").each(function () {
            let machinePk = $(this).data('machine-pk');
            let jobMonitorOperationId = $(this).data('job-monitor-operation-id');
            data.push({ machine_pk: machinePk, job_monitor_operation_id: jobMonitorOperationId });
        });

        hideError();
        showLoading();

        $.ajax({
            url: "/monitoring/check-next-jobs/",
            method: "POST",
            headers: {
                "X-CSRFToken": getCSRFToken()
            },
            contentType: "application/x-www-form-urlencoded",
            data: { data: JSON.stringify(data) },
            success: function (response) {
                if (response.changed) {
                    location.reload();
                } else {
                    hideLoading();
                }
            },
            error: function (xhr, status, error) {
                console.error("Error checking for updates: ", error);
                hideLoading();
                showError();
            },
            complete: function () {
                isRequestInProgress = false;
            }
        });
    }


    // ==========================================
    // Initialization
    // ==========================================

    function init() {
        // Set initial view (table view)
        showTableView();

        // Start cursor status polling (opens the socket when a cursor is active)
        cursorCheckInterval = setInterval(checkCursorStatus, POLL_INTERVAL);
        checkCursorStatus();

        // Start AJAX polling
        setInterval(checkForUpdates, 120000);
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();
