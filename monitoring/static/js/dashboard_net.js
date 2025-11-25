/**
 * Dashboard View Switcher with Auto-Scroll
 * Toggles between card view and table (airport-style) view using arrow keys
 * Auto-scrolls in table view with pause at top and bottom
 * Real-time AJAX updates for machine status
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
            if (currentScroll >= maxScroll - 5) {
                stopAutoScroll();
                scrollDirection = 'up';
                startAutoScrollAfterPause(PAUSE_DURATION);
            } else {
                boardBody.scrollTop += SCROLL_SPEED;
            }
        } else {
            if (currentScroll <= 5) {
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

            setTimeout(() => {
                boardBody = document.querySelector('.board-body');
                if (boardBody) {
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
        if (e.keyCode === 39 || e.key === 'ArrowRight') {
            if (currentView === 'card') {
                showTableView();
            }
            e.preventDefault();
        } else if (e.keyCode === 37 || e.key === 'ArrowLeft') {
            if (currentView === 'table') {
                showCardView();
            }
            e.preventDefault();
        }
    }

    /**
     * Map status to CSS class name
     */
    function getStatusClass(status) {
        if (!status || status === 'loading' || status === 'Loading...') {
            return 'row-offline';
        }

        const statusUpper = status.toUpperCase().trim();

        if (statusUpper === 'ACTIVE') return 'row-active';
        if (statusUpper === 'STOPPED') return 'row-stopped';
        if (statusUpper === 'FEED-HOLD' || statusUpper === 'FEED_HOLD') return 'row-feed-hold';
        if (statusUpper === 'ALARM') return 'row-alarm';
        if (statusUpper === 'INTERRUPTED') return 'row-interrupted';
        if (statusUpper === 'SEMI_AUTOMATIC' || statusUpper === 'SEMI-AUTOMATIC') return 'row-semi-automatic';

        return 'row-offline';
    }

    /**
     * Update table view with machine status
     */
    function updateTableView(machines) {
        if (currentView !== 'table') return;

        for (const [machineName, state] of Object.entries(machines)) {
            const row = document.querySelector(`[data-machine-name="${machineName}"]`);
            if (row) {
                const status = state.status || 'OFFLINE';

                // Update status text
                const statusText = row.querySelector('.status-text');
                if (statusText) {
                    statusText.textContent = status;
                }

                // Update data attribute
                row.setAttribute('data-status', status);

                // Remove all status classes
                row.classList.remove('row-active', 'row-stopped', 'row-feed-hold',
                                   'row-alarm', 'row-interrupted', 'row-semi-automatic', 'row-offline');

                // Add appropriate status class
                const statusClass = getStatusClass(status);
                row.classList.add(statusClass);
            }
        }
    }

    // Function to format ISO 8601 duration (P0DT00H00M00S) to HH:MM:SS format
    function formatDuration(duration) {
        const matches = duration.match(/P(?:\d+D)?T(\d+H)?(\d+M)?(\d+S)?/);
        if (!matches) return "00:00:00";

        const hours = parseInt(matches[1]) || 0;
        const minutes = parseInt(matches[2]) || 0;
        const seconds = parseInt(matches[3]) || 0;

        return String(hours).padStart(2, '0') + ":" +
               String(minutes).padStart(2, '0') + ":" +
               String(seconds).padStart(2, '0');
    }

    // Function to parse HH:MM:SS time format into total seconds
    function parseTime(timeString) {
        const [hours, minutes, seconds] = timeString.split(":").map(Number);
        return hours * 3600 + minutes * 60 + seconds;
    }

    // Function to update the visual background of the remain time row based on time passed
    function update_remain_time_visual(remainTimeRowElement, remainTime, lastCycleTime) {
        // Check if time values are valid before updating the visual
        if (!remainTimeRowElement || remainTime === "loading" || lastCycleTime === "loading") return;

        const maxTime = parseTime(lastCycleTime);
        const remainTimeSeconds = parseTime(remainTime);
        const timePassed = maxTime - remainTimeSeconds;
        const percentagePassed = (timePassed / maxTime) * 100;

        if (remainTimeSeconds > 0) {
            remainTimeRowElement.style.background = `linear-gradient(90deg, green ${100 - percentagePassed}%, orange ${100 - percentagePassed}%)`;
        } else {
            remainTimeRowElement.style.background = 'orange';
        }
    }

    // Function to fetch the latest machine states from the server
    function fetchMachineStates() {
        fetch('/monitoring/dashboard/', {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => updateMachineCards(data.machines))
        .catch(error => console.error('Error fetching machine states:', error));
    }

    // Function to update the content of each machine card
    function updateMachineCards(machines) {
        // Update card view
        for (const [machineName, state] of Object.entries(machines)) {
            const card = document.getElementById(`machine_${machineName}`);
            if (card) {
                // Update text fields
                card.querySelector('.status').textContent = state.status || 'loading';
                card.querySelector('.this_cycle_duration').textContent = formatDuration(state.this_cycle_duration) || 'loading';
                card.querySelector('.remain_time').textContent = formatDuration(state.remain_time) || 'loading';
                card.querySelector('.last_cycle_duration').textContent = formatDuration(state.last_cycle_duration) || 'loading';
                card.querySelector('.current_tool').textContent = state.current_tool || 'loading';
                card.querySelector('.active_nc_program').textContent = state.active_nc_program || 'loading';
                card.querySelector('.current_machine_time').textContent = formatDuration(state.current_machine_time) || 'loading';

                // Update remaining time visual if valid times are present
                const remainTimeRowElement = card.querySelector('.remain-time-row');
                if (state.remain_time && state.last_cycle_duration) {
                    update_remain_time_visual(remainTimeRowElement, state.remain_time, state.last_cycle_duration);
                }
            }
        }

        // Update card background colors based on status
        update_visual();

        // Update table view
        updateTableView(machines);
    }

    // Function to update the card background color based on machine status
    function update_visual() {
        const cards = document.getElementsByClassName('card-body');
        for (let card of cards) {
            const status = card.querySelector('.status').textContent;
            let backgroundColor = "";
            let textColor = "black"; // Default text color

            if (status === 'STOPPED') {
                backgroundColor = "orange";
                textColor = "white";
            } else if (status === 'FEED-HOLD') {
                backgroundColor = "blue";
                textColor = "white";
            } else if (status === 'ACTIVE') {
                backgroundColor = "green";
                textColor = "white";
            } else if (status === 'ALARM') {
                backgroundColor = "red";
                textColor = "white";
            }

            // Set the background color of the card
            card.style.backgroundColor = backgroundColor;

            // Set the text color for all relevant elements within the card
            const textElements = card.querySelectorAll('.status, .this_cycle_duration, .remain_time, .last_cycle_duration, .current_tool, .active_nc_program, .current_machine_time');
            textElements.forEach(element => {
                element.style.color = textColor;
            });
        }
    }

    // Function to start the periodic fetching of machine states every 30 seconds
    function startFetching() {
        fetchMachineStates();  // Initial fetch
        setInterval(fetchMachineStates, 2000);  // Fetch every 2 seconds
    }

    /**
     * Initialize the dashboard view
     */
    function init() {
        // Set initial view (table view)
        showTableView();

        // Add keyboard event listener
        document.addEventListener('keydown', handleKeyPress);

        // Start AJAX polling
        startFetching();
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();
