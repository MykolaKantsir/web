document.addEventListener('DOMContentLoaded', function () {
    // Function to send AJAX request
    function sendCreateLabelsRequest(productId, productToolType) {
        fetch('/inventory/create_labels/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                product_id: productId,
                product_tool_type: productToolType
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                alert(data.message);
            } else {
                alert(`Error: ${data.message}`);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while creating labels.');
        });
    }

    // Function to get CSRF token
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Event delegation for dynamically added buttons
    document.body.addEventListener('click', function(event) {
        if (event.target.matches('.print-label-button')) {
            const productId = event.target.getAttribute('data-product-id');
            const productToolType = event.target.getAttribute('data-product-tool-type');
            sendCreateLabelsRequest(productId, productToolType);
        }

        if (event.target.matches('.add-to-print-button')) {
            const productId = event.target.getAttribute('data-product-id');
            const productToolType = event.target.getAttribute('data-product-tool-type');
            // Implement the logic for adding to print here
            // For now, just sending the create labels request
            sendCreateLabelsRequest(productId, productToolType);
        }

        if (event.target.matches('.print-all-labels-button')) {
            // Implement the logic for printing all labels here
            // For now, this is just a placeholder
            alert('Print all labels functionality is not yet implemented.');
        }
    });
});
