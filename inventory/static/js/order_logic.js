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
const bulkBtn = document.getElementById('bulkStatusChangeButton');
if (bulkBtn) {
  bulkBtn.addEventListener('click', function () {
    const selectedOrders = document.querySelectorAll('.order-checkbox:checked');
    const selectEl = document.getElementById('bulkStatusSelect');
    const newStatus = selectEl ? selectEl.value : null;
    if (!newStatus) return; // nothing to do if control missing

    selectedOrders.forEach(function (checkbox) {
      const orderId = checkbox.dataset.orderId;
      changeOrderStatus(orderId, newStatus);
    });
  });
}

// Clear selection
const clearBtn = document.getElementById('clearSelectionButton');
if (clearBtn) {
  clearBtn.addEventListener('click', function () {
    const selectedOrders = document.querySelectorAll('.order-checkbox:checked');

    selectedOrders.forEach(function (checkbox) {
      checkbox.checked = false;

      // Also hide the checkmark overlay
      const parentDiv = checkbox.closest('.order-card');
      if (parentDiv) {
        const overlay = parentDiv.querySelector('.checkmark-overlay');
        if (overlay) overlay.classList.remove('visible');
      }
    });

    // Update the visibility of multiple status actions once, after unchecking all
    if (typeof updateBulkActionVisibility === 'function') {
      updateBulkActionVisibility();
    }
  });
}

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
const sortBtn = document.getElementById('sortByStatus');
if (sortBtn) {
  sortBtn.addEventListener('click', function () {
    const weekContainers = document.querySelectorAll('.week-container');
    if (!weekContainers.length) return;

    weekContainers.forEach(function (weekContainer) {
      // collect cards
      const orders = Array.from(weekContainer.querySelectorAll('.order-card'));

      // sort by data-status (case-insensitive)
      orders.sort(function (a, b) {
        const statusA = (a.dataset.status || a.getAttribute('data-status') || '').toLowerCase();
        const statusB = (b.dataset.status || b.getAttribute('data-status') || '').toLowerCase();
        return statusA.localeCompare(statusB);
      });

      // re-append in new order
      orders.forEach(function (order) {
        if (order.parentNode) order.parentNode.appendChild(order);
      });
    });
  });
}

// Sort orders by manufacturer when clicking on the button
const sortManBtn = document.getElementById('sortByManufacturer');
if (sortManBtn) {
  sortManBtn.addEventListener('click', function () {
    const weekContainers = document.querySelectorAll('.week-container');
    if (!weekContainers.length) return;

    weekContainers.forEach(function (weekContainer) {
      // collect cards
      const orders = Array.from(weekContainer.querySelectorAll('.order-card'));

      // sort by data-manufacturer
      orders.sort(function (a, b) {
        const manufacturerA = (a.dataset.manufacturer || a.getAttribute('data-manufacturer') || '').toLowerCase();
        const manufacturerB = (b.dataset.manufacturer || b.getAttribute('data-manufacturer') || '').toLowerCase();
        return manufacturerA.localeCompare(manufacturerB);
      });

      // re-append in new order
      orders.forEach(function (order) {
        if (order.parentNode) order.parentNode.appendChild(order);
      });
    });
  });
}

// Comments section
document.addEventListener('DOMContentLoaded', function() {
    // Attach event listener to comment forms
    document.querySelectorAll('.comment-form-container form').forEach(function(form) {
        form.addEventListener('submit', function(event) {
            event.preventDefault();  // Prevent the default form submission
            submitComment(this);
        });
    });
});

// Submit a comment
function submitComment(form) {
    var orderId = form.getAttribute('data-order-id'); // Extract orderId from form action
    var commentText = form.querySelector('textarea[name="comment_text"]').value;
    var csrfToken = getCsrfToken(); // Reuse existing function to get CSRF token

    fetch(`/inventory/add_comment/${orderId}/`, {  
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify({ comment_text: commentText })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            // Update the comments section in the UI
            updateCommentsUI(orderId, data.comment);
            // Clear the textarea after submission
            form.querySelector('textarea[name="comment_text"]').value = '';
        } else {
            showAlert("Error: " + data.message);
        }
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}

// Update the comments section in the UI
function updateCommentsUI(orderId, newComment) {
    var commentsContainer = document.getElementById('order-card-' + orderId).querySelector('.order-comments');
    var commentsList = document.getElementById('comments-list-' + orderId);

    // Create a new list item for the comment
    var newCommentElement = document.createElement('li');
    newCommentElement.className = 'comment-text';
    newCommentElement.textContent = newComment.text; // plain text from server

    // Append the new comment
    commentsList.appendChild(newCommentElement);
    commentsContainer.classList.add('has-comments');

    // Make any anchors inside this new comment open in a new tab
    retargetCommentLinks(newCommentElement);

    // If the comments container is hidden, show it
    if (commentsContainer.style.display === 'none') {
        commentsContainer.style.display = 'block';
    }
}

// --- Ensure comment links open in a new tab ---
function retargetCommentLinks(scope) {
  (scope || document).querySelectorAll('.order-comments a').forEach(function (a) {
    a.setAttribute('target', '_blank');
    a.setAttribute('rel', 'noopener noreferrer');
  });
}

document.addEventListener('DOMContentLoaded', function () {
  retargetCommentLinks(document);
});