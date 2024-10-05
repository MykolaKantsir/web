let isRequestInProgress = false;

function showLoading() {
    // Add logic to display loading spinner
    let loadingDiv = document.createElement("div");
    loadingDiv.id = "loading";
    loadingDiv.style.position = "fixed";
    loadingDiv.style.top = "0";
    loadingDiv.style.left = "0";
    loadingDiv.style.width = "100%";
    loadingDiv.style.height = "100%";
    loadingDiv.style.backgroundColor = "rgba(0, 0, 0, 0.5)";
    loadingDiv.style.color = "white";
    loadingDiv.style.display = "flex";
    loadingDiv.style.justifyContent = "center";
    loadingDiv.style.alignItems = "center";
    loadingDiv.innerText = "Loading...";
    document.body.appendChild(loadingDiv);
}

function hideLoading() {
    // Remove loading spinner
    let loadingDiv = document.getElementById("loading");
    if (loadingDiv) {
        document.body.removeChild(loadingDiv);
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
        let jobPk = $(this).data('job-pk');
        data.push({ machine_pk: machinePk, job_pk: jobPk });
    });

    showLoading(); // Show the loading spinner

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
            }
        },
        error: function (xhr, status, error) {
            console.error("Error checking for updates: ", error);
        },
        complete: function () {
            hideLoading(); // Hide the loading spinner
            isRequestInProgress = false; // Reset the flag after completion
        }
    });
}

// Run check every 30 seconds
setInterval(checkForUpdates, 30000);
