window.onload = function () {
    'use strict';

    var Cropper = window.Cropper;
    var image = document.getElementById('image');
    var cropButton = document.getElementById('crop-button');
    var spinnerContainer = document.getElementById('spinner-container');
    var currentMode = 'crop';


    // Predefined test dimensions with manually entered min and max values
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

    // Simulates cropping using handleCrop() and waits for each crop to complete
    async function simulateCropping() {
        console.log("Starting simulation of cropping...");

        for (let i = 0; i < testDimensions.length; i++) {
            const dim = testDimensions[i];

            // ✅ Simulating a crop event by calling handleCrop with the test data
            await simulateHandleCrop(dim);
        }

        console.log("Simulation of cropping completed.");
        updateTolerances(); // ✅ Update Min and Max after cropping
    }

    // Simulate calling handleCrop() by providing a predefined cropBoxData
    async function simulateHandleCrop(dim) {
        return new Promise((resolve) => {
            setTimeout(() => {
                const cropBoxData = {
                    x: dim.x,
                    y: dim.y,
                    width: dim.width,
                    height: dim.height
                };

                console.log(`Simulating crop for ${dim.id} at x:${dim.x}, y:${dim.y}`);

                // ✅ Pass `dim.id` to handleCropSimulation
                handleCropSimulation(cropBoxData, dim.value, dim.isVertical, dim.id);

                resolve(); // Mark this crop as completed before moving to the next one
            }, 200); // Adding slight delay to allow for image processing
        });
    }

    // ✅ Simulates handleCrop without OCR processing
    function handleCropSimulation(cropBoxData, recognizedText, isVertical, dimensionId) {
        console.log(`Handling simulated crop for ID: ${dimensionId || "Unknown"}`);
    
        // Ensure dimensionId is valid before processing
        let dimensionNumber = null;
    
        if (dimensionId && typeof dimensionId === "string" && dimensionId.startsWith("dimension-")) {
            dimensionNumber = parseInt(dimensionId.replace("dimension-", ""), 10);
        }
    
        // Fallback in case dimensionId is missing or invalid
        if (isNaN(dimensionNumber)) {
            console.warn(`Invalid or missing dimension ID: ${dimensionId}. Using fallback row number.`);
            dimensionNumber = document.querySelectorAll("#data-table tbody tr:not(#row-template)").length + 1;
        }
    
        console.log(`Processed Dimension Number: ${dimensionNumber}`);
    
        // Instead of actual OCR, we use the predefined text
        addRow(recognizedText, cropBoxData, isVertical);
    
        // Use the extracted dimension number for marking
        markCropped(cropBoxData, dimensionNumber, isVertical);
    }
    

    // ✅ Updates Min and Max values **after all rows are added**
    function updateTolerances() {
        console.log("Updating manually entered tolerances...");

        const rows = document.querySelectorAll("#data-table tbody tr:not(#row-template)");

        testDimensions.forEach((dim, index) => {
            const row = rows[index];
            if (row) {
                row.querySelector(".min-input").value = dim.min;
                row.querySelector(".max-input").value = dim.max;
            }
        });

        console.log("Tolerance updates complete.");
    }

    // Store original image source
    const originalImageSrc = image.src;

    var options = {
        aspectRatio: NaN,
        viewMode: 1,
        zoomOnWheel: true,
        scalable: true,
        movable: true,
        autoCropArea: 0.5,
        cropBoxMovable: true,
        cropBoxResizable: true,
        dragMode: 'crop',
        ready: function () {},
    };

    var cropper = new Cropper(image, options);

    // Show spinner
    function showSpinner() {
        spinnerContainer.classList.add('active');
    }

    // Hide spinner
    function hideSpinner() {
        spinnerContainer.classList.remove('active');
    }

    hideSpinner(); // Ensure spinner is hidden on page load

    // Handle Ctrl key for toggling modes
    document.addEventListener('keydown', function (event) {
        if (event.key === 'Control') {
            currentMode = currentMode === 'crop' ? 'move' : 'crop';
            cropper.setDragMode(currentMode);
            image.style.cursor = currentMode === 'move' ? 'grab' : '';
        }
    });

    // Function to determine if the text is vertical
    function isVertical(canvas) {
        const width = canvas.width;
        const height = canvas.height;
        return height > width;
    }

    // Function to draw all rectangles and numbers on the image
    function markCropped(cropBoxData, rowNumber, position = 1) {
        const img = new Image();
        img.src = image.src; // Use the current image source (preserve previous drawings)

        img.onload = function () {
            const canvas = document.createElement('canvas');
            canvas.width = img.naturalWidth; // Ensure correct dimensions
            canvas.height = img.naturalHeight;

            const ctx = canvas.getContext('2d');
            ctx.drawImage(img, 0, 0); // Keep previously drawn rectangles

            // Draw red rectangle
            ctx.strokeStyle = 'red';
            ctx.lineWidth = 2;
            ctx.strokeRect(
                cropBoxData.x,      // Correct x
                cropBoxData.y,      // Correct y
                cropBoxData.width,  // Correct width
                cropBoxData.height  // Correct height
            );

            // Determine position for the number
            let numberX = cropBoxData.x; // Default: top-left corner (position 1)
            let numberY = cropBoxData.y - 10; // Above the top-left corner

            // Update position based on requested placement
            switch (position) {
                case 2: // Top-center
                    numberX = cropBoxData.x + cropBoxData.width / 2;
                    numberY = cropBoxData.y - 10;
                    break;
                case 3: // Top-right
                    numberX = cropBoxData.x + cropBoxData.width;
                    numberY = cropBoxData.y - 10;
                    break;
                case 4: // Middle-right
                    numberX = cropBoxData.x + cropBoxData.width + 10;
                    numberY = cropBoxData.y + cropBoxData.height / 2;
                    break;
                case 5: // Bottom-right
                    numberX = cropBoxData.x + cropBoxData.width;
                    numberY = cropBoxData.y + cropBoxData.height + 20;
                    break;
                case 6: // Bottom-center
                    numberX = cropBoxData.x + cropBoxData.width / 2;
                    numberY = cropBoxData.y + cropBoxData.height + 20;
                    break;
                case 7: // Bottom-left
                    numberX = cropBoxData.x;
                    numberY = cropBoxData.y + cropBoxData.height + 20;
                    break;
                case 8: // Middle-left
                    numberX = cropBoxData.x - 20;
                    numberY = cropBoxData.y + cropBoxData.height / 2;
                    break;
                default: // Position 1 (top-left)
                    numberX = cropBoxData.x;
                    numberY = cropBoxData.y - 10;
                    break;
            }

            // Draw bold red number
            ctx.font = 'bold 24px Arial';
            ctx.fillStyle = 'red';
            ctx.fillText(rowNumber, numberX, numberY);

            // Update the main image's source and cropper
            image.src = canvas.toDataURL();
            cropper.replace(image.src); // Update cropper with the new image

            img.onerror = function () {
                console.error('Failed to load the image for drawing.');
            };
        };
    }


    // Function to restore the selection frame
    function restoreSelectionFrame(data) {
        cropper.setData(data); // Set the selection frame
    }

    // Function to handle cropping action
    async function handleCrop() {
        // Ensure there is an active selection
        const cropBoxData = cropper.getData();
        if (!cropBoxData.width || !cropBoxData.height) {
            alert("Please select a crop area before cropping.");
            return;
        }
    
        const croppedCanvas = cropper.getCroppedCanvas();
        if (!croppedCanvas) {
            alert("Failed to generate cropped image. Please try again.");
            return;
        }
    
        showSpinner();
    
        try {
            let canvasToProcess = croppedCanvas;
            if (isVertical(croppedCanvas)) { // Function still works
                canvasToProcess = rotate90(croppedCanvas);
            }
    
            const recognizedText = await readText(canvasToProcess);
    
            // Get row number
            const rowCount = document.querySelectorAll("#data-table tbody tr:not(#row-template)").length + 1;
    
            // ✅ Rename variable to avoid shadowing
            const isDimensionVertical = cropBoxData.height > cropBoxData.width;
    
            if (recognizedText) {
                addRow(recognizedText, cropBoxData, isDimensionVertical);
                markCropped(cropBoxData, rowCount, isDimensionVertical);
            } else {
                addRow('No text found', cropBoxData, isDimensionVertical);
                markCropped(cropBoxData, rowCount, isDimensionVertical);
            }
    
        } catch (error) {
            console.error("Error recognizing text:", error);
            alert("Error recognizing text.");
        } finally {
            hideSpinner();
        }
    }    
    

    // Function to rotate the canvas 90 degrees clockwise
    function rotate90(canvas) {
        const offscreenCanvas = document.createElement('canvas');
        offscreenCanvas.width = canvas.height;
        offscreenCanvas.height = canvas.width;
        const ctx = offscreenCanvas.getContext('2d');
        ctx.translate(offscreenCanvas.width / 2, offscreenCanvas.height / 2);
        ctx.rotate((90 * Math.PI) / 180);
        ctx.drawImage(canvas, -canvas.width / 2, -canvas.height / 2);
        return offscreenCanvas;
    }

    // Function to calculate tolerances correctly
    function calculateTolerances(value, general_tolerance) {
        console.log("Calculating tolerances for:", value); // Debugging
    
        let cleanedValue = value.replace(",", ".").trim();
    
        if (!/^\d*\.?\d+$/.test(cleanedValue)) {
            console.log("Invalid value for tolerances:", value);
            return [null, null]; 
        }
    
        const parsedValue = parseFloat(cleanedValue);
        if (isNaN(parsedValue)) {
            console.log("Parsed value is NaN:", value);
            return [null, null]; 
        }
    
        let min = parsedValue - general_tolerance;
        let max = parsedValue + general_tolerance;
    
        // Ensure min is never negative
        if (min < 0) {
            min = 0;
        }
    
        // ✅ Remove unnecessary trailing zeros
        min = parseFloat(min.toFixed(10)).toString();
        max = parseFloat(max.toFixed(10)).toString();
    
        console.log(`Min: ${min}, Max: ${max}`); // Debugging output
    
        return [min, max];
    }    


    // Function to add a new row with a structured dimension ID
    function addRow(content, cropBoxData, isDimensionVertical, general_tolerance = 0.1, manualMin = null, manualMax = null) {
        const tableBody = document.querySelector("#data-table tbody");
        const rowTemplate = document.getElementById("row-template");

        if (!rowTemplate) {
            console.error("Row template not found!");
            return;
        }

        // Clone the hidden template row
        const newRow = rowTemplate.cloneNode(true);
        newRow.classList.remove("d-none"); // Make it visible
        newRow.removeAttribute("id"); // Remove the template ID

        // Determine row number
        const rowCount = tableBody.querySelectorAll("tr:not(#row-template)").length + 1;
        newRow.querySelector(".row-number").textContent = rowCount;

        // Convert value to use a decimal point if possible
        let normalizedValue = content ? content.replace(",", ".").trim() : "";
        let parsedValue = parseFloat(normalizedValue);

        if (!isNaN(parsedValue)) {
            normalizedValue = parsedValue.toString();
        } else {
            console.warn("Text not recognized, setting empty value.");
            normalizedValue = "";
        }

        console.log("Adding row with value:", normalizedValue);

        // Set value input field
        const valueInput = newRow.querySelector(".value-input");
        if (valueInput) {
            valueInput.value = normalizedValue;
        } else {
            console.error("Value input field not found!");
        }

        // ✅ Call calculateTolerances() **only if min and max are not provided manually**
        let min = manualMin !== null ? manualMin : "";
        let max = manualMax !== null ? manualMax : "";

        if (manualMin === null || manualMax === null) {
            [min, max] = calculateTolerances(normalizedValue, general_tolerance);
        }

        // Set min and max input fields
        const minInput = newRow.querySelector(".min-input");
        const maxInput = newRow.querySelector(".max-input");

        if (minInput && maxInput) {
            minInput.value = min !== null ? min : "";
            maxInput.value = max !== null ? max : "";
        } else {
            console.error("Min/Max input fields not found!");
        }

        console.log("Min set to:", minInput?.value, "Max set to:", maxInput?.value);

        // ✅ Assign unique `name` for radio buttons per row
        const uniqueRadioName = `type-selection-${rowCount}`;
        newRow.querySelectorAll(".btn-check").forEach((radio, index) => {
            radio.name = uniqueRadioName;
            radio.id = `type${index + 1}-row${rowCount}`;
            const label = newRow.querySelector(`label[for="type${index + 1}"]`);
            if (label) {
                label.setAttribute("for", `type${index + 1}-row${rowCount}`);
            }
        });

        // Store crop data in hidden fields
        if (cropBoxData) {
            const dimensionId = `dimension-${rowCount}`;
            newRow.querySelector(".dimension-id").value = dimensionId;
            newRow.querySelector(".crop-x").value = cropBoxData.x.toFixed(2);
            newRow.querySelector(".crop-y").value = cropBoxData.y.toFixed(2);
            newRow.querySelector(".crop-width").value = cropBoxData.width.toFixed(2);
            newRow.querySelector(".crop-height").value = cropBoxData.height.toFixed(2);
            newRow.querySelector(".is-vertical").value = isDimensionVertical ? "1" : "0";
        }

        // Attach event listeners for preview
        newRow.addEventListener("mouseenter", renderPreview);
        newRow.querySelectorAll("input").forEach((input) => {
            input.addEventListener("focus", renderPreview);
        });

        // Append the new row
        tableBody.appendChild(newRow);
    }


    // Function to render the cropped image preview
    function renderPreview(event) {
        const row = event.currentTarget.closest("tr"); // Get the hovered or focused row
    
        if (!row) return; // If no row is found, do nothing
    
        // Retrieve crop data from hidden fields
        const cropX = parseFloat(row.querySelector(".crop-x")?.value);
        const cropY = parseFloat(row.querySelector(".crop-y")?.value);
        const cropWidth = parseFloat(row.querySelector(".crop-width")?.value);
        const cropHeight = parseFloat(row.querySelector(".crop-height")?.value);
    
        // Ensure crop data is valid
        if (isNaN(cropX) || isNaN(cropY) || isNaN(cropWidth) || isNaN(cropHeight)) {
            console.warn("Invalid crop data for preview.");
            return;
        }
    
        // Create a new cropped image from the original image
        const img = new Image();
        img.src = document.getElementById("image").src; // Use the original full image source
    
        img.onload = function () {
            const canvas = document.createElement("canvas");
            canvas.width = cropWidth;
            canvas.height = cropHeight;
            const ctx = canvas.getContext("2d");
    
            // Draw the cropped area onto the canvas
            ctx.drawImage(img, cropX, cropY, cropWidth, cropHeight, 0, 0, cropWidth, cropHeight);
    
            // Convert canvas to a data URL and update the preview image
            document.getElementById("preview-image").src = canvas.toDataURL();
        };
    
        img.onerror = function () {
            console.error("Failed to load the image for preview.");
        };
    }    
   

    // Function to recognize text from the cropped image
    function readText(croppedCanvas) {
        return new Promise((resolve, reject) => {
            if (!croppedCanvas) {
                resolve(null);
                return;
            }

            croppedCanvas.toBlob((blob) => {
                const reader = new FileReader();

                reader.onload = function () {
                    const base64Image = reader.result;

                    Tesseract.recognize(base64Image, 'eng', {})
                        .then(({ data: { text } }) => {
                            const trimmedText = text.trim();
                            resolve(trimmedText || null);
                        })
                        .catch((error) => {
                            reject(error);
                        });
                };

                reader.readAsDataURL(blob);
            }, 'image/png');
        });
    }

    // Attach event listener to the crop button
    cropButton.addEventListener('click', handleCrop);

    // Run simulation on page load
    //simulateCropping();
};


