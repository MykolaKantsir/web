// ✅ Global variable to store CSRF Token
let csrfToken = null;

// ✅ Function to check if the user is logged in before loading the page
async function checkLoginStatus() {
    try {
        const response = await fetch("/measuring/api/check_auth/", {
            method: "GET",
            credentials: "include", // ✅ Ensures session cookie is sent
        });

        if (!response.ok) {
            throw new Error("User not authenticated");
        }

        const data = await response.json();
        if (!data.authenticated) {
            throw new Error("User not authenticated");
        }
    } catch (error) {
        window.location.replace("/accounts/login/");
    }
}

// ✅ Function to request CSRF token from Django
async function fetchCsrfToken() {
    try {
        const response = await fetch("/accounts/login/", {
            method: "GET",
            credentials: "include", // Ensure cookies are sent
        });

        if (response.ok) {
            csrfToken = getCsrfToken();
        }
    } catch (error) {}
}

// ✅ Function to get CSRF token from cookies
function getCsrfToken() {
    if (csrfToken) return csrfToken; // ✅ Use global CSRF token if available

    const cookies = document.cookie;
    const csrfCookie = cookies.split("; ").find(row => row.startsWith("csrftoken="));

    return csrfCookie ? csrfCookie.split("=")[1] : null;
}

// ✅ Function to send cropped dimension data to Django
async function sendDimensionData(dimensionData) {
    if (!dimensionData || !dimensionData.drawing_id) {
        return;  // ✅ Ensure valid data
    }

    // ✅ Ensure CSRF token is available
    const csrfToken = getCsrfToken();
    if (!csrfToken) {
        console.error("❌ CSRF token is missing.");
        return null;
    }

    try {
        const response = await fetch("/measuring/api/create_or_update_dimension/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrfToken  // ✅ CSRF token for security
            },
            body: JSON.stringify(dimensionData),
            credentials: "include"  // ✅ Ensure cookies (sessionid) are sent
        });

        const data = await response.json();

        if (data.success) {
            return data.dimension_id;  // ✅ Return newly created or updated dimension_id
        } else {
            console.error("❌ Failed to save dimension:", data.error);
            return null;
        }
    } catch (error) {
        console.error("❌ Error sending dimension data:", error);
        return null;
    }
}

// ✅ Function to send drawing data to the backend
async function sendDrawingData(drawingData) {
    const csrfToken = getCsrfToken();

    try {
        const response = await fetch("/measuring/api/create_drawing/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrfToken
            },
            body: JSON.stringify(drawingData)
        });

        const data = await response.json();

        if (data.success) {
            document.getElementById("image").setAttribute("drawing-id", data.drawing_id);
        }
    } catch (error) {}
}

// ✅ Function to fetch saved drawing and dimensions when the page loads
function fetchDrawingData() {
    // TODO: Implement AJAX GET request to Django
}

// ✅ Function to update an existing dimension in Django
function updateDimension(id, newData) {
    // TODO: Implement AJAX PUT request to Django
}

// ✅ Function to delete a dimension from Django
function deleteDimension(id) {
    // TODO: Implement AJAX DELETE request to Django
}

// ✅ Fetch CSRF Token as soon as page loads
document.addEventListener("DOMContentLoaded", function () {
    fetchCsrfToken();
});
