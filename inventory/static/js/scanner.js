function showAlert(message) {
    // Set the message
    document.getElementById('alert-message').textContent = message;
    // Show the custom alert
    document.getElementById('custom-alert').style.display = 'block';
    // Hide the alert and reload after 1.5 seconds
    setTimeout(function() {
        document.getElementById('custom-alert').style.display = 'none';
        location.reload();
    }, 2000);
}

document.getElementById('barcode-form').addEventListener('submit', function(e) {
    e.preventDefault();
    let barcode = document.getElementById('barcode-input').value;
    let csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    fetch('', {
        method: 'POST',
        body: JSON.stringify({ 'barcode': barcode }),
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        }
    })
    .then(response => response.json())
    .then(data => {
        showAlert(data.message); // Display a message to the user
    });
});

document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('barcode-input').focus();
});