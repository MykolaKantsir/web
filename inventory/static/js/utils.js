// utils.js

// Get the CSRF token from the cookie
export function getCsrfToken() {
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

// Reusing functions from your original script
export function showAlert(message) {
    // Set the message
    document.getElementById('alert-message').textContent = message;
    // Show the custom alert
    document.getElementById('custom-alert').style.display = 'block';
    // Hide the alert without reloading the page after 1.5 seconds
    setTimeout(function() {
        document.getElementById('custom-alert').style.display = 'none';
    }, 1500);  // Adjust time as needed
}
