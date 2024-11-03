let currentIndex = 0;
let isCarouselActive = false;
let isTransitioningToMainPage = false; // New flag to prevent restarting the carousel
let carouselTimeout;

// Function to show a large job card overlay
function showLargeJobCard(index) {
    const overlay = document.getElementById("large-next-job-card-overlay");
    const mainContent = document.getElementById("main-content-1"); // Select the main content by ID
    const machines = document.querySelectorAll(".job-card");

    if (overlay && machines.length > 0) {
        // Hide the main content when showing the large card
        mainContent.style.display = "none";

        // Retrieve the data for the selected machine based on the index
        const machinePk = machines[index].dataset.machinePk;
        const jobMonitorOperationId = machines[index].dataset.jobMonitorOperationId;

        // Update the overlay content with new machine and job data
        updateLargeJobCardContent(machinePk, jobMonitorOperationId);

        overlay.classList.remove("hidden");
        overlay.classList.add("visible");

        // Reset the carousel timeout to hide the overlay after 120 seconds
        clearTimeout(carouselTimeout);
        carouselTimeout = setTimeout(hideLargeJobCard, 120000);
    }
}

// Function to hide the large job card overlay
function hideLargeJobCard() {
    const overlay = document.getElementById("large-next-job-card-overlay");
    const mainContent = document.getElementById("main-content-1"); // Select the main content by ID

    if (overlay) {
        overlay.classList.remove("visible");
        overlay.classList.add("hidden");

        // Show the main content when hiding the large card
        mainContent.style.display = "flex"; // Or the appropriate display style for your layout
        isCarouselActive = false;
        isTransitioningToMainPage = true;  // Set the flag to prevent the carousel from restarting

        // Disable the transition flag after a short delay to avoid immediate key press issues
        setTimeout(() => {
            isTransitioningToMainPage = false;
        }, 500); // Adjust the timeout as needed
    }
}

// Function to switch to the next card or go back to the main page if we reach the end
function showNextCard() {
    const machines = document.querySelectorAll(".job-card");
    if (currentIndex < machines.length - 1) {
        currentIndex++;
        showLargeJobCard(currentIndex);
    } else {
        // If at the last card, return to the main page
        hideLargeJobCard();
    }
}

// Function to switch to the previous card
function showPreviousCard() {
    if (currentIndex > 0) {
        currentIndex--;
        showLargeJobCard(currentIndex);
    }
}

// Event listener for arrow keys
document.addEventListener("keydown", function(event) {
    // Prevent carousel restart if we're transitioning back to the main page
    if (isTransitioningToMainPage) {
        return;
    }

    if (isCarouselActive) {
        if (event.key === "PageDown") {
            showNextCard();
        } else if (event.key === "PageUp") {
            showPreviousCard();
        }
    }
});

// Function to start the carousel when the user presses an arrow key
function startCarousel() {
    if (!isCarouselActive) {
        isCarouselActive = true;
        currentIndex = 0;  // Start from the first job card
        showLargeJobCard(currentIndex);
    }
}

// Start the carousel when user presses the right arrow key on the main page
document.addEventListener("keydown", function(event) {
    // Prevent carousel restart if we're transitioning back to the main page
    if (isTransitioningToMainPage) {
        return;
    }

    if (event.key === "PageDown" && !isCarouselActive) {
        startCarousel();
    }
});

// Function to update the content of the large card based on the machine and job data
function updateLargeJobCardContent(machinePk, jobMonitorOperationId) {
    const machineData = getMachineData(machinePk);
    const jobData = getJobData(jobMonitorOperationId);

    document.querySelector("#large-next-job-card-overlay .machine-row .col-6.text-left h2").textContent = machineData.name;
    document.querySelector("#large-next-job-card-overlay .machine-row .col-6.text-right h2").textContent = jobData.name;
    document.querySelector("#large-next-job-card-overlay .job-details-row .col-4.text-left .value").textContent = jobData.material;
    document.querySelector("#large-next-job-card-overlay .job-details-row .col-4.text-center .value").textContent = jobData.quantity;
    document.querySelector("#large-next-job-card-overlay .job-details-row .col-4.text-right .value").textContent = jobData.location;
    
    const img = document.querySelector("#large-next-job-card-overlay .large-pdf-placeholder img");
    if (jobData.drawing_image_base64 && img) {
        img.src = jobData.drawing_image_base64;
    }
    // Get the background color dynamically from the parent element
    const barcodeParent = document.querySelector(".job-details-row.m-0");
    const backgroundColor = window.getComputedStyle(barcodeParent).backgroundColor;

    // Generate the barcode and display it in the SVG
    JsBarcode("#barcode-svg", jobData.report_number, {
        format: "CODE128",       // Keep the barcode format
        lineColor: "#000",       // Black barcode color
        width: 8,                // Increase the width of the bars (4x wider)
        height: 100,             // Keep the height the same
        displayValue: false,     // Disable the human-readable string
        background: backgroundColor  // Set background color dynamically
    });
}


// Function to get machine data from the DOM
function getMachineData(machinePk) {
    let machineElement = document.querySelector(`.job-card[data-machine-pk='${machinePk}']`);
    
    return {
        name: machineElement.querySelector(".machine-row .col-6.text-left h5").textContent
    };
}

// Function to get job data from the DOM
function getJobData(jobMonitorOperationId) {
    // Select the small job card using jobMonitorOperationId
    let jobElement = document.querySelector(`.job-card[data-job-monitor-operation-id='${jobMonitorOperationId}']`);
    
    return {
        name: jobElement.querySelector(".machine-row .col-6.text-right h5").textContent,
        material: jobElement.querySelector(".job-details-row .col-4.text-left .value").textContent,
        quantity: jobElement.querySelector(".job-details-row .col-4.text-center .value").textContent,
        location: jobElement.querySelector(".job-details-row .col-4.text-right .value").textContent,
        drawing_image_base64: jobElement.querySelector(".pdf-placeholder img") ? 
                             jobElement.querySelector(".pdf-placeholder img").src : null,
        report_number: jobElement.querySelector(".job-details-row #barcode-" + jobElement.dataset.machinePk + " .value").textContent // Get the report number from the small card
    };
}