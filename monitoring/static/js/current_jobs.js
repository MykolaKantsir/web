/**
 * Current Jobs View Switcher
 * Toggles between card view and table (airport-style) view using arrow keys
 */

(function() {
    'use strict';

    // Current view state: 'card' or 'table'
    let currentView = 'card';

    // DOM elements
    const cardView = document.getElementById('card-view');
    const tableView = document.getElementById('table-view');

    /**
     * Switch to card view
     */
    function showCardView() {
        if (cardView && tableView) {
            cardView.style.display = 'block';
            tableView.style.display = 'none';
            currentView = 'card';
            console.log('Switched to card view');
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
            console.log('Switched to table view');
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
        // Set initial view (card view)
        showCardView();

        // Add keyboard event listener
        document.addEventListener('keydown', handleKeyPress);

        console.log('Current Jobs view switcher initialized');
        console.log('Use Arrow Left (←) and Arrow Right (→) to switch between views');
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();