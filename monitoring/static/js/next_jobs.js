/**
 * Next Jobs View Switcher with Auto-Scroll
 * Toggles between card view and table (airport-style) view using arrow keys
 * Auto-scrolls in table view with pause at top and bottom
 */

(function() {
    'use strict';

    // View switching state
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
        if (isPaused || currentView !== 'table' || !boardBody) {
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

        // Debug: Check if scrolling is possible
        if (boardBody) {
            const scrollHeight = boardBody.scrollHeight;
            const clientHeight = boardBody.clientHeight;
            const maxScroll = scrollHeight - clientHeight;
            console.log(`[AUTO-SCROLL] Starting: scrollHeight=${scrollHeight}, clientHeight=${clientHeight}, maxScroll=${maxScroll}`);
        }

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

    /**
     * Handle keyboard navigation
     */
    function handleKeyPress(e) {
        // Arrow Right (→) - switch to table view
        if (e.keyCode === 39 || e.key === 'ArrowRight') {
            if (currentView === 'card') {
                showTableView();
            }
            e.preventDefault();
        }
        // Arrow Left (←) - switch to card view
        else if (e.keyCode === 37 || e.key === 'ArrowLeft') {
            if (currentView === 'table') {
                showCardView();
            }
            e.preventDefault();
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
    // Kiosk Scaling (Original Code)
    // ==========================================

    function scaleForKioskLayout() {
        const DESIGN_WIDTH = 1280;
        const DESIGN_HEIGHT = 720;

        const isKioskDevice = /Android|SmartTV|TV|AFTT|AFTM/i.test(navigator.userAgent);

        if (!isKioskDevice) {
            return;
        }

        function applyScale() {
            const body = document.body;

            // Reset transform first to get accurate viewport dimensions
            body.style.transform = 'none';
            body.style.width = '';
            body.style.height = '';

            // Force a reflow to ensure dimensions are updated
            void body.offsetHeight;

            // Use screen dimensions instead of viewport for Android TV
            // because viewport meta tag is ignored by Fully Kiosk Browser
            // Also account for device pixel ratio if present
            const dpr = window.devicePixelRatio || 1;
            const actualWidth = window.screen.width * dpr;
            const actualHeight = window.screen.height * dpr;

            // Calculate scale with actual screen dimensions
            const scaleW = actualWidth / DESIGN_WIDTH;
            const scaleH = actualHeight / DESIGN_HEIGHT;
            const scale = Math.min(scaleW, scaleH);

            // Apply the transform
            body.style.transformOrigin = "top left";
            body.style.transform = `scale(${scale})`;
            body.style.width = DESIGN_WIDTH + "px";
            body.style.height = DESIGN_HEIGHT + "px";
            body.style.overflow = "hidden";
        }

        // Apply with multiple attempts at different delays
        function applyScaleMultiple() {
            setTimeout(applyScale, 100);   // First try
            setTimeout(applyScale, 500);   // Second try
            setTimeout(applyScale, 1000);  // Third try
        }

        window.addEventListener("resize", applyScale);
        document.addEventListener("DOMContentLoaded", applyScaleMultiple);

        // Initial application with multiple attempts
        applyScaleMultiple();
    }

    // ==========================================
    // Initialization
    // ==========================================

    function init() {
        // Set initial view (table view)
        showTableView();

        // Add keyboard event listener
        document.addEventListener('keydown', handleKeyPress);

        // Start AJAX polling
        setInterval(checkForUpdates, 120000);

        // Initialize kiosk scaling
        scaleForKioskLayout();
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();
