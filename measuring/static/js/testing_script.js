// ✅ Predefined test dimensions with manually entered min/max values
const testDimensions = [
    { id: "dimension-1", x: 1639.28, y: 343.13, width: 116.91, height: 59.75, isVertical: false, value: "10.5", min: "10.4", max: "10.6" },
    { id: "dimension-2", x: 1852.31, y: 566.55, width: 59.75, height: 122.10, isVertical: true, value: "22.3", min: "22.0", max: "22.5" },
    { id: "dimension-3", x: 820.94, y: 400.28, width: 106.51, height: 54.56, isVertical: false, value: "15.8", min: "15.7", max: "15.9" },
    { id: "dimension-4", x: 1400.27, y: 418.47, width: 124.70, height: 51.96, isVertical: false, value: "8.9", min: "8.8", max: "9.0" },
    { id: "dimension-5", x: 1470.31, y: 602.80, width: 50.75, height: 150.29, isVertical: true, value: "31.2", min: "31.1", max: "31.4" },
    { id: "dimension-6", x: 1816.33, y: 787.77, width: 39.04, height: 46.13, isVertical: true, value: "12.7", min: "12.5", max: "12.9" },
    { id: "dimension-7", x: 1530.17, y: 886.09, width: 77.94, height: 44.16, isVertical: false, value: "20.0", min: "19.8", max: "20.2" },
    { id: "dimension-8", x: 574.14, y: 1397.88, width: 135.09, height: 44.16, isVertical: false, value: "9.5", min: "9.4", max: "9.6" },
    { id: "dimension-9", x: 103.92, y: 1392.68, width: 111.71, height: 51.96, isVertical: false, value: "14.4", min: "14.3", max: "14.5" },
    { id: "dimension-10", x: 114.31, y: 1156.27, width: 57.15, height: 106.51, isVertical: true, value: "25.6", min: "25.5", max: "25.7" },
    { id: "dimension-11", x: 610.51, y: 1140.69, width: 36.37, height: 70.14, isVertical: true, value: "18.9", min: "18.7", max: "19.1" },
    { id: "dimension-12", x: 1084.74, y: 387.77, width: 94.47, height: 70.85, isVertical: false, value: "12.3", min: "12.2", max: "12.5" },
    { id: "dimension-13", x: 821.31, y: 865.59, width: 60.51, height: 152.24, isVertical: true, value: "17.1", min: "16.9", max: "17.3" },
    { id: "dimension-14", x: 906.03, y: 861.23, width: 104.69, height: 72.75, isVertical: false, value: "7.8", min: "7.7", max: "7.9" },
    { id: "dimension-15", x: 301.36, y: 309.36, width: 171.46, height: 90.93, isVertical: false, value: "14.9", min: "14.8", max: "15.0" },
    { id: "dimension-16", x: 181.57, y: 627.24, width: 56.46, height: 48.39, isVertical: false, value: "10.1", min: "10.0", max: "10.3" },
    { id: "dimension-17", x: 1314.78, y: 1264.21, width: 61.41, height: 42.51, isVertical: false, value: "16.7", min: "16.6", max: "16.8" },
    { id: "dimension-18", x: 493.60, y: 964.03, width: 41.57, height: 64.95, isVertical: true, value: "22.0", min: "21.8", max: "22.2" },
    { id: "dimension-19", x: 418.26, y: 974.42, width: 46.76, height: 75.34, isVertical: true, value: "28.5", min: "28.3", max: "28.7" },
    { id: "dimension-20", x: 322.14, y: 966.63, width: 54.56, height: 93.52, isVertical: true, value: "19.4", min: "19.3", max: "19.5" },
    { id: "dimension-21", x: 255.85, y: 969.99, width: 38.71, height: 80.65, isVertical: true, value: "9.3", min: "9.2", max: "9.4" },
    { id: "dimension-22", x: 1161.13, y: 1531.04, width: 39.99, height: 82.65, isVertical: true, value: "26.8", min: "26.7", max: "26.9" }
];

// ✅ Simulate cropping using handleCrop() and wait for each crop to complete
async function simulateCropping() {
    console.log("🔄 Starting simulated cropping...");

    for (let i = 0; i < testDimensions.length; i++) {
        const dim = testDimensions[i];

        // ✅ Simulating a crop event by calling handleCrop with the test data
        await simulateHandleCrop(dim);
    }

    console.log("✅ Simulation of cropping completed.");
    updateTolerances(testDimensions); // ✅ Update Min and Max after cropping
}

// ✅ Simulate calling handleCrop() by providing predefined cropBoxData
async function simulateHandleCrop(dim) {
    return new Promise((resolve) => {
        setTimeout(() => {
            const cropBoxData = {
                x: dim.x,
                y: dim.y,
                width: dim.width,
                height: dim.height
            };

            console.log(`🎯 Simulating crop for ${dim.id} at x:${dim.x}, y:${dim.y}`);

            // ✅ Pass `dim.id` to handleCropSimulation
            handleCropSimulation(cropBoxData, dim.value, dim.isVertical, dim.id);

            resolve(); // Mark this crop as completed before moving to the next one
        }, 200); // Adding slight delay to simulate real processing
    });
}

// ✅ Simulate handleCrop without OCR processing
function handleCropSimulation(cropBoxData, recognizedText, isVertical, dimensionId) {
    console.log(`🔹 Handling simulated crop for ID: ${dimensionId || "Unknown"}`);

    let dimensionNumber = null;

    if (dimensionId && typeof dimensionId === "string" && dimensionId.startsWith("dimension-")) {
        dimensionNumber = parseInt(dimensionId.replace("dimension-", ""), 10);
    }

    if (isNaN(dimensionNumber)) {
        console.warn(`⚠ Invalid or missing dimension ID: ${dimensionId}. Using fallback row number.`);
        dimensionNumber = document.querySelectorAll("#data-table tbody tr:not(#row-template)").length + 1;
    }

    console.log(`📌 Processed Dimension Number: ${dimensionNumber}`);

    // ✅ Add row with test values instead of OCR
    addRow(recognizedText, cropBoxData, isVertical);

    // ✅ Mark cropped area with the correct number
    markCropped(cropBoxData, dimensionNumber);
}

// ✅ Automatically start the simulation when the page loads
// Uncomment to enable auto-testing
// window.onload = function() {
//     console.log("🔄 Running simulated cropping on page load...");
//     simulateCropping();
// };
