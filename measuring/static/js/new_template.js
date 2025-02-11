window.onload = function () {
    'use strict';

    var Cropper = window.Cropper;
    var image = document.getElementById('image');
    var cropButton = document.getElementById('crop-button');
    var spinnerContainer = document.getElementById('spinner-container');
    var currentMode = 'crop';

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
        // Replace commas with dots for decimal recognition
        let cleanedValue = value.replace(",", ".").trim();

        // Ensure it's a valid float number
        if (!/^\d*\.?\d+$/.test(cleanedValue)) {
            return [null, null]; // Invalid format, return empty values
        }

        const parsedValue = parseFloat(cleanedValue);

        if (isNaN(parsedValue)) {
            return [null, null]; // Return nulls if value is not a number
        }

        let min = parsedValue - general_tolerance;
        let max = parsedValue + general_tolerance;

        // Ensure min is never negative
        if (min < 0) {
            min = 0;
        }

        return [min.toFixed(3), max.toFixed(3)]; // Return formatted values
    }


    // Function to add a new row with a structured dimension ID
    function addRow(content, cropBoxData, isDimensionVertical, general_tolerance = 0.1) {
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
        
        // Generate the dimension ID (e.g., "dimension-1")
        const dimensionId = `dimension-${rowCount}`;
        newRow.setAttribute("data-dimension-id", dimensionId); // Set as row attribute
    
        // Fix radio button `name` attributes to be unique per row
        newRow.querySelectorAll(".btn-check").forEach((radio, index) => {
            const uniqueName = `type-selection-${rowCount}`;
            radio.name = uniqueName;
            radio.id = `type${index + 1}-row${rowCount}`;
            newRow.querySelector(`label[for="type${index + 1}"]`).setAttribute("for", `type${index + 1}-row${rowCount}`);
        });
    
        // Append the new row
        tableBody.appendChild(newRow);
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
};

