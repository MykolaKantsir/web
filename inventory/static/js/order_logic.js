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
