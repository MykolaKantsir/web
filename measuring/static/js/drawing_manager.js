// ✅ Function to mark cropped areas on the drawing
function markCropped(cropBoxData, rowNumber, position = 1) {
    const imageElement = document.getElementById("image");

    if (!imageElement || !imageElement.src) {
        return;
    }

    const img = new Image();
    img.src = imageElement.src;

    img.onload = function () {
        setTimeout(() => {
            const canvas = document.createElement("canvas");
            canvas.width = img.naturalWidth;
            canvas.height = img.naturalHeight;

            const ctx = canvas.getContext("2d");
            ctx.drawImage(img, 0, 0); // ✅ Preserve previous markings

            // ✅ Draw red rectangle
            ctx.strokeStyle = 'red';
            ctx.lineWidth = 2;
            ctx.strokeRect(
                cropBoxData.x,
                cropBoxData.y,
                cropBoxData.width,
                cropBoxData.height
            );

            // ✅ Draw row number in bold red
            ctx.font = 'bold 24px Arial';
            ctx.fillStyle = 'red';
            ctx.fillText(rowNumber, cropBoxData.x, cropBoxData.y - 10);

            // ✅ Update the image source
            const markedImageSrc = canvas.toDataURL();
            imageElement.src = markedImageSrc;

            // ✅ Store the marked version in session storage
            sessionStorage.setItem("uploadedImage", markedImageSrc);

            // ✅ Ensure Cropper.js uses the updated image **after marking**
            if (window.cropper) {
                window.cropper.replace(markedImageSrc);
            } else {
                reinitializeCropper(); // ✅ Call from cropper_manager.js
            }
        }, 100);
    };

    img.onerror = function () {};
}

// ✅ Function to mark all dimensions on the clean drawing
function markAllDimensions(cleanDrawing, dimensions) {
    if (!cleanDrawing || !cleanDrawing.src || dimensions.length === 0) {
        return;
    }

    const img = new Image();
    img.src = cleanDrawing.src; // ✅ Start with a clean drawing

    img.onload = function () {
        const canvas = document.createElement("canvas");
        canvas.width = img.naturalWidth;
        canvas.height = img.naturalHeight;

        const ctx = canvas.getContext("2d");
        ctx.drawImage(img, 0, 0); // ✅ Draw the base clean drawing

        // ✅ Iterate over dimensions and draw markings
        dimensions.forEach((dim, index) => {
            ctx.strokeStyle = 'red';
            ctx.lineWidth = 2;
            ctx.strokeRect(dim.x, dim.y, dim.width, dim.height);

            // ✅ Draw row number
            ctx.font = 'bold 24px Arial';
            ctx.fillStyle = 'red';
            ctx.fillText(index + 1, dim.x, dim.y - 10);
        });

        // ✅ Convert canvas back to an image
        const markedImageSrc = canvas.toDataURL();
        document.getElementById("image").src = markedImageSrc;

        // ✅ Store the marked version in session storage
        sessionStorage.setItem("uploadedImage", markedImageSrc);

        // ✅ Ensure Cropper.js uses the updated image
        if (window.cropper) {
            window.cropper.replace(markedImageSrc);
        } else {
            reinitializeCropper(); // ✅ Call from cropper_manager.js
        }
    };

    img.onerror = function () {};
}

// ✅ Function to render the cropped image preview when hovering or focusing on a row
function renderPreview(event) {
    const row = event.currentTarget.closest("tr"); // Get the hovered or focused row

    if (!row) return;

    // ✅ Retrieve crop data from hidden fields
    const cropX = parseFloat(row.querySelector(".crop-x")?.value);
    const cropY = parseFloat(row.querySelector(".crop-y")?.value);
    const cropWidth = parseFloat(row.querySelector(".crop-width")?.value);
    const cropHeight = parseFloat(row.querySelector(".crop-height")?.value);

    // ✅ Ensure crop data is valid
    if (isNaN(cropX) || isNaN(cropY) || isNaN(cropWidth) || isNaN(cropHeight)) {
        return;
    }

    // ✅ Create a cropped preview from the full image
    const img = new Image();
    img.src = document.getElementById("image").src; // Use the full image source

    img.onload = function () {
        const canvas = document.createElement("canvas");
        canvas.width = cropWidth;
        canvas.height = cropHeight;
        const ctx = canvas.getContext("2d");

        // ✅ Draw the cropped area onto the canvas
        ctx.drawImage(img, cropX, cropY, cropWidth, cropHeight, 0, 0, cropWidth, cropHeight);

        // ✅ Convert canvas to an image & update preview
        document.getElementById("preview-image").src = canvas.toDataURL();
    };

    img.onerror = function () {};
}

// ✅ Function to rotate a canvas 90° clockwise
function rotate90(canvas) {
    const offscreenCanvas = document.createElement("canvas");
    offscreenCanvas.width = canvas.height;
    offscreenCanvas.height = canvas.width;
    const ctx = offscreenCanvas.getContext("2d");

    ctx.translate(offscreenCanvas.width / 2, offscreenCanvas.height / 2);
    ctx.rotate((90 * Math.PI) / 180);
    ctx.drawImage(canvas, -canvas.width / 2, -canvas.height / 2);

    return offscreenCanvas;
}

// ✅ Ensure rotate90 is available globally for `new_template.js`
window.rotate90 = rotate90;
