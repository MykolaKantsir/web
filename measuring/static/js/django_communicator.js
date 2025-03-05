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

// ✅ Function to send drawing data to the backend
async function sendDrawingData(drawingData) {
    const csrfToken = getCsrfToken();
    const canvas = document.getElementById("measure-canvas");
    if (!canvas) {
        console.error("❌ Canvas element not found.");
        return;
    }

    // Convert canvas to Base64
    const imageBase64 = canvas.toDataURL("image/png");
    drawingData.imageBase64 = imageBase64;

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
            document.getElementById("measure-canvas").setAttribute("drawing-id", data.drawing_id);
        }
    } catch (error) {}
}

// ✅ Function to fetch drawing and dimension data
async function getDrawingData(drawingId) {
    try {
        const response = await fetch(`/measuring/api/drawing/${drawingId}/`, {
            method: "GET",
            credentials: "include",
        });

        if (!response.ok) {
            throw new Error("Failed to fetch drawing data");
        }

        const data = await response.json();
        console.log("✅ Drawing Data:", data);

        if (data.drawing && data.drawing.drawing_image_base64) {  // ✅ Corrected key usage
            const canvas = document.getElementById("measure-canvas");
            const ctx = canvas.getContext("2d");
            const img = new Image();
            img.src = `data:image/png;base64,${data.drawing.drawing_image_base64}`;  // ✅ Ensure proper Base64 format

            img.onload = function () {
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                ctx.drawImage(img, 0, 0, canvas.width, canvas.height);

                // ✅ Store clean drawing AFTER it is loaded
                const cleanDrawing = document.getElementById("clean-drawing");
                cleanDrawing.src = img.src;  // ✅ Use image source directly from the fetched data

            };
        }
        return data;
    } catch (error) {
        console.error("❌ Error fetching drawing data:", error);
        return null;
    }
}


// ✅ Function to send measured values to Django
async function sendMeasurement(measuredData) {
    if (!measuredData || !measuredData.dimensionId || !measuredData.drawingId || !measuredData.measuredValue) {
        console.error("❌ Invalid measurement data");
        return;
    }

    const csrfToken = getCsrfToken();
    if (!csrfToken) {
        console.error("❌ CSRF token is missing.");
        return null;
    }

    try {
        const response = await fetch("/measuring/api/save_measurement/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrfToken,
            },
            body: JSON.stringify(measuredData),
            credentials: "include",
        });

        const data = await response.json();

        if (data.success) {
            console.log("✅ Measurement saved successfully:", data);
            return { protocolId: data.protocolId, dimensionId: data.dimensionId };
        } else {
            console.error("❌ Failed to save measurement:", data.error);
            return null;
        }
    } catch (error) {
        console.error("❌ Error sending measurement data:", error);
        return null;
    }
}

// ✅ Fetch CSRF Token as soon as page loads
document.addEventListener("DOMContentLoaded", function () {
    fetchCsrfToken();
});

window.django_communicator = {
    checkLoginStatus,
    fetchCsrfToken,
    getCsrfToken,
    getDrawingData,
    sendDrawingData
};
