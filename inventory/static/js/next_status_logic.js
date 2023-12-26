// next_status_logic.js

document.addEventListener('DOMContentLoaded', function() {
    document.body.addEventListener('click', function(event) {
        let targetElement = event.target.closest('.status-change-div');

        if (targetElement) {
            event.preventDefault();
            event.stopPropagation();

            // Retrieve the order ID from the parent container
            let orderId = targetElement.getAttribute('data-order-id');

            // Call the function to change the status of the order
            changeOrderNextStatus(orderId);
        }
    });
});

function changeOrderNextStatus(orderId) {
    var csrfToken = getCsrfToken();

    $.ajax({
        url: '/inventory/change_order_status/' + orderId + '/',
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': csrfToken
        },
        success: function(response) {
            console.log("Response received:", response);

            if(response.status === 'success') {
                // Find the .compact-order-card for this order
                let orderCard = document.querySelector(`[data-order-id="${orderId}"]`);
                if (orderCard) {
                    // Find the status div (second col-4 div)
                    let statusDiv = orderCard.querySelectorAll('.col-4')[1];
                    let statusParagraph = statusDiv.querySelector('p');

                    if(statusDiv && statusParagraph) {
                        // Update the status text
                        statusParagraph.textContent = response.new_status; 

                        // Update the class for the status div
                        // Remove old status class
                        let currentStatusClass = Array.from(statusDiv.classList).find(className => className.startsWith('order-status-'));
                        if(currentStatusClass) {
                            statusDiv.classList.remove(currentStatusClass);
                        }
                        // Add new status class
                        let newStatusClass = 'order-status-' + response.new_status.toLowerCase();
                        statusDiv.classList.add(newStatusClass);
                    }
                }
            } else {
                console.error("Error in response:", response.message);
            }
        },
        error: function(error) {
            console.error("Error changing status:", error);
        }
    });
}


// Reuse the existing getCsrfToken function from your order_logic.js or define it here if not already defined
function getCsrfToken() {
    // Retrieve the csrf token from the cookies
    let csrfToken = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, 'csrftoken'.length + 1) === ('csrftoken' + '=')) {
                csrfToken = decodeURIComponent(cookie.substring('csrftoken'.length + 1));
                break;
            }
        }
    }
    return csrfToken;
}
