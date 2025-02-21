// ✅ Ensure Cropper is initialized
function ensureCropperInitialized() {
    if (!window.cropper) {
        triggerCropperAfterUpload(); // ✅ From cropper_manager.js
    }
}

// ✅ Handle cropping action
async function handleCrop() {
    ensureCropperInitialized(); // ✅ Ensure Cropper is ready

    const imageElement = document.getElementById("image");
    if (!imageElement || !imageElement.src) {
        alert("❌ No image available for cropping.");
        return;
    }

    const cropBoxData = window.cropper.getData();
    if (!cropBoxData.width || !cropBoxData.height) {
        alert("Please select a crop area before cropping.");
        return;
    }

    const croppedCanvas = window.cropper.getCroppedCanvas();
    if (!croppedCanvas) {
        alert("Failed to generate cropped image. Please try again.");
        return;
    }

    showSpinner(); // ✅ Show spinner before processing

    try {
        let canvasToProcess = croppedCanvas;
        if (isVertical(croppedCanvas)) {
            canvasToProcess = window.rotate90(croppedCanvas);
        }

        const recognizedText = await readText(canvasToProcess);
        const rowCount = document.querySelectorAll("#data-table tbody tr:not(#row-template)").length + 1;
        const isDimensionVertical = cropBoxData.height > cropBoxData.width;

        // ✅ Get the selected tolerance level from the radio button group
        let selectedTolerance = document.querySelector('input[name="mode-selection"]:checked')?.id || "mode-m";
        selectedTolerance = selectedTolerance.replace("mode-", "").toUpperCase(); // Convert to "R", "M", or "F"


        // ✅ Only send the drawing once, on the first crop
        const drawingId = imageElement.getAttribute("drawing-id");
        if (!drawingId) {
            const drawingData = {
                filename: document.getElementById("file-name").textContent, // ✅ Retrieve filename
                drawing_image_base64: document.getElementById("clean-image").src.split(",")[1], // ✅ Clean base64 image
                flip_angle: parseFloat(imageElement.getAttribute("flip_angle")) || 0,
                pages_count: 1, // Assuming a single-page drawing for now
                url: ""  // Empty for now
            };

            await sendDrawingData(drawingData);
        }

        // ✅ Pass selectedTolerance to addRow()
        addRow(recognizedText || "No text found", cropBoxData, isDimensionVertical, selectedTolerance);

        markCropped(cropBoxData, rowCount);
        
        // ✅ Disable Rotate Button After First Crop
        const rotateButton = document.getElementById("rotate-button");
        if (rotateButton) {
            rotateButton.disabled = true;
        }

    } catch (error) {
        console.error("❌ Error recognizing text:", error);
        alert("Error recognizing text.");
    } finally {
        hideSpinner();
    }
}

// ✅ Function to check if the cropped area is vertical
function isVertical(canvas) {
    return canvas.height > canvas.width;
}

// ✅ Show the spinner
function showSpinner() {
    const spinnerContainer = document.getElementById("spinner-container");
    if (spinnerContainer) {
        spinnerContainer.classList.add("active");
    }
}

// ✅ Hide the spinner
function hideSpinner() {
    const spinnerContainer = document.getElementById("spinner-container");
    if (spinnerContainer) {
        spinnerContainer.classList.remove("active");
    }
}

// ✅ Event Listeners
document.addEventListener("cropperInitialized", function () {
    // ✅ Enable Crop Button
    document.getElementById("crop-button").addEventListener("click", handleCrop);
});
