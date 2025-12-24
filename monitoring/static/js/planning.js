/**
 * Planning Page JavaScript
 * Handles searchable operation dropdowns and assignment updates
 */

(function() {
    'use strict';

    // Debounce helper
    function debounce(func, wait) {
        let timeout;
        return function(...args) {
            clearTimeout(timeout);
            timeout = setTimeout(() => func.apply(this, args), wait);
        };
    }

    // Show status message
    function showStatus(message, type) {
        const statusEl = document.getElementById('status-message');
        if (!statusEl) return;

        statusEl.textContent = message;
        statusEl.className = 'status-message ' + type;

        // Auto-hide after 3 seconds
        setTimeout(() => {
            statusEl.classList.add('hidden');
        }, 3000);
    }

    // Search for operations
    async function searchOperations(query) {
        const url = new URL(API_URLS.availableOperations, window.location.origin);
        if (query) {
            url.searchParams.set('search', query);
        }

        try {
            const response = await fetch(url, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            if (!response.ok) {
                throw new Error('Search failed');
            }

            return await response.json();
        } catch (error) {
            console.error('Search error:', error);
            return { operations: [] };
        }
    }

    // Assign operation to slot
    async function assignOperation(slot, operationId) {
        try {
            const response = await fetch(API_URLS.manualAssign, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': CSRF_TOKEN,
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify({
                    machine_pk: MACHINE_PK,
                    slot: slot,
                    operation_id: operationId
                })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Assignment failed');
            }

            showStatus('Operation assigned successfully', 'success');
            return true;
        } catch (error) {
            console.error('Assignment error:', error);
            showStatus(error.message || 'Failed to assign operation', 'error');
            return false;
        }
    }

    // Clear operation from slot
    async function clearOperation(slot) {
        return await assignOperation(slot, null);
    }

    // Toggle operation status between setup and in progress
    async function toggleOperationStatus(operationId, isSetup) {
        try {
            const response = await fetch(API_URLS.toggleStatus, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': CSRF_TOKEN,
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify({
                    operation_id: operationId,
                    is_setup: isSetup
                })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Status toggle failed');
            }

            showStatus(`Status updated to ${isSetup ? 'Setup' : 'In Progress'}`, 'success');
            return true;
        } catch (error) {
            console.error('Status toggle error:', error);
            showStatus(error.message || 'Failed to update status', 'error');
            return false;
        }
    }

    // Initialize status toggle buttons for an operation slot
    function initStatusToggle(container) {
        const operationId = container.dataset.operationId;
        const isSetup = container.dataset.isSetup === 'true';
        const slot = container.dataset.slot;

        // Only show for 'current' slot with an operation assigned
        if (!operationId || slot !== 'current') {
            return;
        }

        const toggleContainer = container.querySelector('.status-toggle-container');
        if (!toggleContainer) return;

        const setupBtn = toggleContainer.querySelector('.setup-btn');
        const progressBtn = toggleContainer.querySelector('.progress-btn');

        // Show the toggle container
        toggleContainer.style.display = 'flex';

        // Set initial active state
        function updateActiveState(isSetupActive) {
            setupBtn.classList.toggle('active', isSetupActive);
            progressBtn.classList.toggle('active', !isSetupActive);
        }

        updateActiveState(isSetup);

        // Setup button click
        setupBtn.addEventListener('click', async () => {
            const success = await toggleOperationStatus(operationId, true);
            if (success) {
                updateActiveState(true);
                container.dataset.isSetup = 'true';
            }
        });

        // Progress button click
        progressBtn.addEventListener('click', async () => {
            const success = await toggleOperationStatus(operationId, false);
            if (success) {
                updateActiveState(false);
                container.dataset.isSetup = 'false';
            }
        });
    }

    // Render search results
    function renderResults(resultsContainer, operations, onSelect) {
        resultsContainer.innerHTML = '';

        if (operations.length === 0) {
            resultsContainer.innerHTML = '<div class="no-results">No operations found</div>';
            resultsContainer.classList.add('active');
            return;
        }

        operations.forEach((op, index) => {
            const item = document.createElement('div');
            item.className = 'search-result-item';
            item.dataset.id = op.id;
            item.dataset.index = index;

            item.innerHTML = `
                <div class="op-name">${escapeHtml(op.name)}</div>
                <div class="op-details">
                    <span>ID: ${escapeHtml(op.monitor_operation_id || '-')}</span>
                    <span>Report: ${escapeHtml(op.report_number || '-')}</span>
                    <span>Qty: ${op.quantity || 0}</span>
                </div>
            `;

            item.addEventListener('click', () => {
                onSelect(op);
            });

            resultsContainer.appendChild(item);
        });

        resultsContainer.classList.add('active');
    }

    // Escape HTML to prevent XSS
    function escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // Initialize a search input
    function initSearchInput(searchInput) {
        const slot = searchInput.dataset.slot;
        const container = searchInput.closest('.operation-slot');
        const hiddenInput = container.querySelector('.operation-id');
        const resultsContainer = container.querySelector('.search-results');
        const clearBtn = container.querySelector('.clear-btn');

        let currentHighlight = -1;
        let currentResults = [];

        // Debounced search
        const doSearch = debounce(async (query) => {
            searchInput.classList.add('loading');
            const data = await searchOperations(query);
            searchInput.classList.remove('loading');

            currentResults = data.operations || [];
            currentHighlight = -1;

            renderResults(resultsContainer, currentResults, (op) => {
                selectOperation(op);
            });
        }, 300);

        // Select an operation
        async function selectOperation(op) {
            searchInput.value = op.name;
            hiddenInput.value = op.id;
            resultsContainer.classList.remove('active');
            resultsContainer.innerHTML = '';

            // Save to server
            const success = await assignOperation(slot, op.id);

            if (success) {
                // Update container data attributes
                container.dataset.operationId = op.id;
                container.dataset.isSetup = op.is_setup ? 'true' : 'false';

                // Reinitialize status toggle for this slot
                initStatusToggle(container);
            }
        }

        // Handle input
        searchInput.addEventListener('input', (e) => {
            const query = e.target.value.trim();
            if (query.length >= 1) {
                doSearch(query);
            } else {
                resultsContainer.classList.remove('active');
                resultsContainer.innerHTML = '';
            }
        });

        // Handle focus - show results if we have a query
        searchInput.addEventListener('focus', () => {
            const query = searchInput.value.trim();
            if (query.length >= 1 && currentResults.length > 0) {
                resultsContainer.classList.add('active');
            } else if (query.length >= 1) {
                doSearch(query);
            }
        });

        // Handle keyboard navigation
        searchInput.addEventListener('keydown', (e) => {
            const items = resultsContainer.querySelectorAll('.search-result-item');

            if (e.key === 'ArrowDown') {
                e.preventDefault();
                currentHighlight = Math.min(currentHighlight + 1, items.length - 1);
                updateHighlight(items);
            } else if (e.key === 'ArrowUp') {
                e.preventDefault();
                currentHighlight = Math.max(currentHighlight - 1, 0);
                updateHighlight(items);
            } else if (e.key === 'Enter') {
                e.preventDefault();
                if (currentHighlight >= 0 && currentResults[currentHighlight]) {
                    selectOperation(currentResults[currentHighlight]);
                }
            } else if (e.key === 'Escape') {
                resultsContainer.classList.remove('active');
                searchInput.blur();
            }
        });

        function updateHighlight(items) {
            items.forEach((item, index) => {
                item.classList.toggle('highlighted', index === currentHighlight);
                if (index === currentHighlight) {
                    item.scrollIntoView({ block: 'nearest' });
                }
            });
        }

        // Clear button
        clearBtn.addEventListener('click', async () => {
            const hadValue = hiddenInput.value;
            searchInput.value = '';
            hiddenInput.value = '';
            resultsContainer.classList.remove('active');
            resultsContainer.innerHTML = '';

            if (hadValue) {
                const success = await clearOperation(slot);

                if (success) {
                    // Remove data attributes and hide toggle
                    delete container.dataset.operationId;
                    delete container.dataset.isSetup;
                    delete container.dataset.isIdle;
                    const toggleContainer = container.querySelector('.status-toggle-container');
                    if (toggleContainer) {
                        toggleContainer.style.display = 'none';
                    }
                    // Remove active state from idle button
                    const idleBtn = container.querySelector('.idle-btn');
                    if (idleBtn) {
                        idleBtn.classList.remove('active');
                    }
                }
            }
        });

        // Close results when clicking outside
        document.addEventListener('click', (e) => {
            if (!container.contains(e.target)) {
                resultsContainer.classList.remove('active');
            }
        });
    }

    // Initialize "Mark as Idle" buttons
    function initIdleButtons() {
        document.querySelectorAll('.idle-btn').forEach(btn => {
            btn.addEventListener('click', async () => {
                const slot = btn.dataset.slot;
                const container = btn.closest('.operation-slot');
                const searchInput = container.querySelector('.operation-search');
                const hiddenInput = container.querySelector('.operation-id');

                // Assign special "idle" value - we use operation_id = 'idle'
                const success = await assignIdleOperation(slot);

                if (success) {
                    searchInput.value = '(Idle - No Operation)';
                    hiddenInput.value = 'idle';
                    container.dataset.isIdle = 'true';
                    delete container.dataset.operationId;

                    // Add active state to idle button
                    btn.classList.add('active');

                    // Hide status toggle
                    const toggleContainer = container.querySelector('.status-toggle-container');
                    if (toggleContainer) {
                        toggleContainer.style.display = 'none';
                    }
                }
            });
        });
    }

    // Assign idle (no operation) to slot
    async function assignIdleOperation(slot) {
        try {
            const response = await fetch(API_URLS.manualAssign, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': CSRF_TOKEN,
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify({
                    machine_pk: MACHINE_PK,
                    slot: slot,
                    operation_id: 'idle'  // Special value for "no operation"
                })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Failed to mark as idle');
            }

            showStatus('Marked as idle (no operation)', 'success');
            return true;
        } catch (error) {
            console.error('Idle assignment error:', error);
            showStatus(error.message || 'Failed to mark as idle', 'error');
            return false;
        }
    }

    // Initialize status toggles for monitor's operations
    function initMonitorStatusToggles() {
        document.querySelectorAll('.operation-display[data-monitor-slot]').forEach(container => {
            const operationId = container.dataset.operationId;
            if (!operationId) return;

            const toggleContainer = container.querySelector('.monitor-status-toggle');
            if (!toggleContainer) return;

            const setupBtn = toggleContainer.querySelector('.setup-btn');
            const progressBtn = toggleContainer.querySelector('.progress-btn');

            if (!setupBtn || !progressBtn) return;

            // Setup button click
            setupBtn.addEventListener('click', async () => {
                const success = await toggleOperationStatus(operationId, true);
                if (success) {
                    setupBtn.classList.add('active');
                    progressBtn.classList.remove('active');
                }
            });

            // Progress button click
            progressBtn.addEventListener('click', async () => {
                const success = await toggleOperationStatus(operationId, false);
                if (success) {
                    setupBtn.classList.remove('active');
                    progressBtn.classList.add('active');
                }
            });
        });
    }

    // Initialize all search inputs and status toggles on page load
    document.addEventListener('DOMContentLoaded', () => {
        const searchInputs = document.querySelectorAll('.operation-search');
        searchInputs.forEach(initSearchInput);

        // Initialize status toggles for manual overrides
        const operationSlots = document.querySelectorAll('.operation-slot');
        operationSlots.forEach(initStatusToggle);

        // Initialize "Mark as Idle" buttons
        initIdleButtons();

        // Initialize status toggles for monitor's operations
        initMonitorStatusToggles();
    });

})();
