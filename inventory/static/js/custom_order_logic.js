import { getCsrfToken } from './utils.js';
import { showAlert } from './utils.js';

document.addEventListener('DOMContentLoaded', function() {
    // Attach event listener to the custom order form submission
    var form = document.getElementById('customOrderForm');
    form.addEventListener('submit', function(event) {
        event.preventDefault();  // Prevent the default form submission
        createCustomOrder();
    });
});

// Create a custom order
function createCustomOrder() {
    var csrfToken = getCsrfToken();  // Reuse the existing function to get CSRF token
    var quantity = document.getElementById('quantity').value;
    var description = document.getElementById('description');

    // Construct the data payload
    var data = {
        quantity: quantity,
        description: description.value,
    };

    fetch('/inventory/create_custom_order/', {  // Corrected URL
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
            // Clear the description input field
            description.value = '';
            showAlert('Custom order successfully placed.');
        } else {
            showAlert("Error: " + data.message);
        }
    })
    .catch((error) => {
        console.error('Error:', error);
        showAlert('Failed to create custom order.');
    });
}



