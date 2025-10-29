/**
 * Current Jobs View Switcher
 * Toggles between card view and table (airport-style) view using arrow keys
 * Auto-scrolls in table view with pause at top and bottom
 */

(function() {
    'use strict';

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

    // Auto-scroll state
    let autoScrollInterval = null;
    let autoScrollTimeout = null;
    let scrollDirection = 'down'; // 'down' or 'up'
    let isPaused = false;

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

                    // Start auto-scroll
                    startAutoScrollAfterPause(PAUSE_DURATION);
                }
            }, 100);
        }
    }

    /**
     * Toggle between views
     */
    function toggleView() {
        if (currentView === 'card') {
            showTableView();
        } else {
            showCardView();
        }
    }

    /**
     * Handle keyboard navigation
     */
    function handleKeyPress(e) {
        // Arrow Right (→) - switch to next view
        if (e.keyCode === 39 || e.key === 'ArrowRight') {
            if (currentView === 'card') {
                showTableView();
            }
            e.preventDefault();
        }
        // Arrow Left (←) - switch to previous view
        else if (e.keyCode === 37 || e.key === 'ArrowLeft') {
            if (currentView === 'table') {
                showCardView();
            }
            e.preventDefault();
        }
    }

    /**
     * Initialize the view switcher
     */
    function init() {
        // Set initial view (table view)
        showTableView();

        // Add keyboard event listener
        document.addEventListener('keydown', handleKeyPress);
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();