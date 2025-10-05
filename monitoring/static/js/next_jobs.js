let isRequestInProgress = false;

function showLoading() {
    let loadingDiv = document.getElementById("loading");
    if (loadingDiv) {
        loadingDiv.classList.remove("hidden");  // Show loading overlay
    }
}

function hideLoading() {
    let loadingDiv = document.getElementById("loading");
    if (loadingDiv) {
        loadingDiv.classList.add("hidden");  // Hide loading overlay
    }
}

function showError() {
    let errorDiv = document.getElementById("error");
    if (errorDiv) {
        errorDiv.classList.remove("hidden");  // Show error overlay
    }
}

function hideError() {
    let errorDiv = document.getElementById("error");
    if (errorDiv) {
        errorDiv.classList.add("hidden");  // Hide error overlay
    }
}

function getCSRFToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]').value;
}

function checkForUpdates() {
    if (isRequestInProgress) {
        return;
    }

    isRequestInProgress = true;

    let data = [];
    $(".job-card").each(function () {
        let machinePk = $(this).data('machine-pk');
        let jobMonitorOperationId = $(this).data('job-monitor-operation-id');
        data.push({ machine_pk: machinePk, job_monitor_operation_id: jobMonitorOperationId });
    });

    hideError();  // Hide error message if any previous error occurred
    showLoading();  // Show the loading spinner before making the request

    $.ajax({
        url: "/monitoring/check-next-jobs/",
        method: "POST",
        headers: {
            "X-CSRFToken": getCSRFToken()  // Add the CSRF token here
        },
        contentType: "application/x-www-form-urlencoded",
        data: { data: JSON.stringify(data) },  // Send the data as a string
        success: function (response) {
            if (response.changed) {
                location.reload();
            } else {
                hideLoading();  // Hide loading overlay if no changes
            }
        },
        error: function (xhr, status, error) {
            console.error("Error checking for updates: ", error);
            hideLoading();  // Hide loading spinner in case of error
            showError();  // Show error overlay when request fails
        },
        complete: function () {
            isRequestInProgress = false;  // Reset the flag after completion
        }
    });
}

// Run check every 120 seconds
setInterval(checkForUpdates, 120000);

/**
 * Scale layout for Android TV / Kiosk devices.
 * Keeps the 1920x1080 design ratio consistent on devices
 * that report smaller CSS resolutions (e.g., 960x540).
 */
function scaleForKioskLayout() {
    const DESIGN_WIDTH = 1920;
    const DESIGN_HEIGHT = 1080;

    // Detect Android/SmartTV devices only
    const isKioskDevice = /Android|SmartTV|TV|AFTT|AFTM/i.test(navigator.userAgent);

    if (!isKioskDevice) {
        return; // Skip scaling on desktops and normal devices
    }

    function applyScale() {
        const scaleW = window.innerWidth / DESIGN_WIDTH;
        const scaleH = window.innerHeight / DESIGN_HEIGHT;
        const scale = Math.min(scaleW, scaleH);

        const body = document.body;
        body.style.transformOrigin = "top left";
        body.style.transform = `scale(${scale})`;
        body.style.width = DESIGN_WIDTH + "px";
        body.style.height = DESIGN_HEIGHT + "px";
        body.style.overflow = "hidden";
    }

    window.addEventListener("resize", applyScale);
    document.addEventListener("DOMContentLoaded", applyScale);
    applyScale();
}

// Initialize kiosk scaling
scaleForKioskLayout();
