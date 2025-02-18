// ✅ Listen for the image load event
document.addEventListener("imageLoaded", function () {
    initializeCropper();
});

// ✅ Function to initialize Cropper.js
function initializeCropper() {
    const imageElement = document.getElementById("image");

    if (!imageElement || !imageElement.src) {
        return;
    }

    if (window.cropper) {
        window.cropper.destroy();
    }

    window.cropper = new Cropper(imageElement, {
        aspectRatio: NaN,
        viewMode: 1,
        zoomOnWheel: true,
        scalable: true,
        movable: true,
        autoCropArea: 0.5,
        cropBoxMovable: true,
        cropBoxResizable: true,
        dragMode: 'crop'
    });

    // ✅ Dispatch event so new_template.js knows Cropper is ready
    document.dispatchEvent(new Event("cropperInitialized"));
}
