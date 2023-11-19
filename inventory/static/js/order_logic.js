document.addEventListener('DOMContentLoaded', function() {
    // Listen to click events on a parent element that exists on page load
    document.body.addEventListener('click', function(event) {
        // Check if the clicked element is an order button
        if (event.target && event.target.classList.contains('order-button')) {
            event.preventDefault();  // Prevent the default form submission
            var productId = event.target.dataset.productId;
            var productToolType = event.target.dataset.productToolType;
            createOrder(productId, productToolType);
        }
    });
});

function showAlert(message) {
    // TODO: Implement a better way to show alerts
    alert(message);
}

// Get the CSRF token from the cookie
function getCsrfToken() {
    var name = 'csrftoken=';
    var decodedCookie = decodeURIComponent(document.cookie);
    var ca = decodedCookie.split(';');
    for(var i = 0; i < ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0) == ' ') {
            c = c.substring(1);
        }
        if (c.indexOf(name) == 0) {
            return c.substring(name.length, c.length);
        }
    }
    return "";
}

// Update the visibility of the multiple status buttons
function updateBulkActionVisibility() {
    var selectedOrders = document.querySelectorAll('.order-checkbox:checked').length;
    var bulkActions = [document.getElementById('bulkStatusChangeButton'), 
                       document.getElementById('clearSelectionButton'), 
                       document.getElementById('bulkStatusSelect')];
    
    bulkActions.forEach(function(action) {
        if (selectedOrders > 0) {
            action.hidden = false;
        } else {
            action.hidden = true;
        }
    });
}

// Create a new order
function createOrder(productId, productToolType) {
    var csrfToken = getCsrfToken();
    var quantityInput = document.querySelector('.quantity-input[data-product-id="' + productId + '"]');
    var quantity = quantityInput ? quantityInput.value : 1;  // Default to 1 if not found

    
    // Construct your data here. Example:
    var data = {
        product_id: productId,
        product_tool_type: productToolType,
        quantity: quantity,
    };

    fetch('create_order/', {  
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            showAlert(data.message);
        } else {
            showAlert("Error: " + data.message);
        }
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}

// Change single order status
function changeOrderStatus(orderId, newStatus) {
    // Convert newStatus to lowercase for class manipulation
    var newStatusClass = 'order-status-' + newStatus.toLowerCase();
    $.ajax({
        url: '/inventory/change_order_status/' + orderId + '/',
        type: 'POST',
        data: {
            'status': newStatus,
            'csrfmiddlewaretoken': getCsrfToken() // Assuming you have a function to get CSRF token
        },
        success: function(response) {
            // Update the class of the order card
            var orderCard = document.getElementById('order-card-' + orderId);

            // Remove existing status classes
            orderCard.classList.forEach(function(className) {
                if (className.startsWith('order-status-')) {
                    orderCard.classList.remove(className);
                }
            });

            // Add the new status class
            orderCard.classList.add(newStatusClass);
            
            // Add the new status class
            orderCard.classList.add(newStatusClass);

            // Update the status dropdown to reflect the new status
            var statusSelect = document.getElementById('statusSelect' + orderId);
            if (statusSelect) {
                for (var i = 0; i < statusSelect.options.length; i++) {
                    if (statusSelect.options[i].value.toLowerCase() === newStatus.toLowerCase()) {
                        statusSelect.selectedIndex = i;
                        break;
                    }
                }
            }

        },
        error: function(error) {
            // Handle error
        }
    });
}

// Select multiple orders
document.getElementById('bulkStatusChangeButton').addEventListener('click', function() {
    var selectedOrders = document.querySelectorAll('.order-checkbox:checked');
    var newStatus = document.getElementById('bulkStatusSelect').value;

    selectedOrders.forEach(function(checkbox) {
        var orderId = checkbox.dataset.orderId;
        changeOrderStatus(orderId, newStatus);
    });
});

// Clear selection
document.getElementById('clearSelectionButton').addEventListener('click', function() {
    var selectedOrders = document.querySelectorAll('.order-checkbox:checked');
    selectedOrders.forEach(function(checkbox) {
        checkbox.checked = false;
        // Update the visibility of multiple status actions
        updateBulkActionVisibility();

        // Also hide the checkmark overlay
        var parentDiv = checkbox.closest('.order-card');
        if (parentDiv) {
            var overlay = parentDiv.querySelector('.checkmark-overlay');
            if (overlay) {
                overlay.classList.remove('visible');
            }
        }
    });
});

// Check/uncheck the checkbox when clicking on the image
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.image-container').forEach(function(container) {
        container.addEventListener('click', function() {
            var overlay = this.querySelector('.checkmark-overlay');
            overlay.classList.toggle('visible');
            // Toggle the corresponding checkbox
            var parentDiv = this.closest('.order-card');
            if (parentDiv) {
                var checkbox = parentDiv.querySelector('.order-checkbox');
                if (checkbox) {
                    checkbox.checked = !checkbox.checked;
                    // Update the visibility of multiple status actions
                    updateBulkActionVisibility();
                }
            }
        });
    });
});

// Show/hide the week's orders
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.week-header').forEach(function(header) {
        header.addEventListener('click', function() {
            var targetId = this.getAttribute('data-target');
            var content = document.querySelector(targetId);
            if (content) {
                content.classList.toggle('show');
            }
        });
    });
});

// Sort orders by status
function sortByStatus() {
    document.querySelectorAll('.week-container').forEach(function(weekContainer) {
        // Get all order cards within this week container
        var orderCards = Array.from(weekContainer.querySelectorAll('.order-card'));

        // Sort the order cards by their status
        orderCards.sort(function(cardA, cardB) {
            var statusA = cardA.getAttribute('data-status').toLowerCase();
            var statusB = cardB.getAttribute('data-status').toLowerCase();
            return statusA.localeCompare(statusB);
        });

        // Append the sorted order cards back to the week container
        orderCards.forEach(function(card) {
            weekContainer.appendChild(card);
        });
    });
}

// Sort orders by status when clicking on the button
document.getElementById('sortByStatus').addEventListener('click', function() {
    // Iterate over each week container
    document.querySelectorAll('.week-container').forEach(function(weekContainer) {
        // Get all order cards within this week container
        var orders = Array.from(weekContainer.querySelectorAll('.order-card'));

        // Sort the orders based on the data-status attribute
        orders.sort(function(a, b) {
            var statusA = a.getAttribute('data-status').toLowerCase();
            var statusB = b.getAttribute('data-status').toLowerCase();
            return statusA.localeCompare(statusB);
        });

        // Reorder the elements in the DOM based on the sorted array
        orders.forEach(function(order) {
            // This moves the element to the end of its parent container
            order.parentNode.appendChild(order);
        });
    });
});

// Sort orders by manufacturer when clicking on the button
document.getElementById('sortByManufacturer').addEventListener('click', function() {
    // Iterate over each week container
    document.querySelectorAll('.week-container').forEach(function(weekContainer) {
        // Get all order cards within this week container
        var orders = Array.from(weekContainer.querySelectorAll('.order-card'));

        // Sort the orders based on the data-manufacturer attribute
        orders.sort(function(a, b) {
            var manufacturerA = a.getAttribute('data-manufacturer').toLowerCase();
            var manufacturerB = b.getAttribute('data-manufacturer').toLowerCase();
            return manufacturerA.localeCompare(manufacturerB);
        });

        // Reorder the elements in the DOM based on the sorted array
        orders.forEach(function(order) {
            // This moves the element to the end of its parent container
            order.parentNode.appendChild(order);
        });
    });
});