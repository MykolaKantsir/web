// ✅ Ensure proper UI state on page load
document.addEventListener("DOMContentLoaded", function () {
    const fileInput = document.getElementById("upload-drawing");
    const imageElement = document.getElementById("image");
    const resetButton = document.getElementById("reset-drawing");
    const rotateButton = document.getElementById("rotate-button");

    if (!fileInput || !imageElement || !resetButton || !rotateButton) {
        return;
    }

    // ✅ Disable Rotate button initially
    rotateButton.disabled = true;

    // ✅ Check session storage and update UI on page load
    const storedImage = sessionStorage.getItem("uploadedImage");

    if (storedImage) {
        imageElement.src = storedImage;
        imageElement.style.display = "block";
        fileInput.style.display = "none";

        // ✅ Enable Rotate button after restoring image
        rotateButton.disabled = false;

        // ✅ Dispatch event to initialize Cropper
        document.dispatchEvent(new Event("imageLoaded"));
    } else {
        fileInput.style.display = "block";
        imageElement.style.display = "none";
    }

    // ✅ Handle file selection
    fileInput.addEventListener("change", function (event) {
        const file = event.target.files[0];
        if (!file) {
            return;
        }
    
        // ✅ Store filename in an HTML element
        let fileNameElement = document.getElementById("file-name");
        if (!fileNameElement) {
            fileNameElement = document.createElement("span");
            fileNameElement.id = "file-name";
            fileNameElement.style.display = "none"; // Keep it hidden
            fileInput.parentElement.appendChild(fileNameElement);
        }
        fileNameElement.textContent = file.name; // ✅ Store filename
    
        const fileType = file.type;
    
        if (fileType === "application/pdf") {
            processPDF(file).then(() => {
                finalizeUpload();
            });
    
        } else if (fileType.startsWith("image/")) {
            const fileReader = new FileReader();
            fileReader.onload = function (e) {
                const base64Image = e.target.result;
                imageElement.src = base64Image;
                imageElement.style.display = "block";
    
                // ✅ Store in session storage
                sessionStorage.setItem("uploadedImage", base64Image);
    
                finalizeUpload();
            };
            fileReader.readAsDataURL(file);
        } else {
            alert("Unsupported file type. Please upload a PDF or an image.");
        }
    });

    // ✅ Attach reset button event listener
    resetButton.addEventListener("click", resetDrawing);

    // ✅ Attach Rotate button event listener
    rotateButton.addEventListener("click", image_rotate90);
});

// ✅ Function to process the uploaded PDF and convert it to an image
function processPDF(file) {
    return new Promise((resolve, reject) => {
        const fileReader = new FileReader();
        fileReader.onload = function () {
            const typedArray = new Uint8Array(this.result);

            pdfjsLib.getDocument(typedArray).promise.then(function (pdf) {
                pdf.getPage(1).then(function (page) {
                    const viewport = page.getViewport({ scale: 1.5 });
                    const canvas = document.createElement("canvas");
                    const context = canvas.getContext("2d");

                    canvas.height = viewport.height;
                    canvas.width = viewport.width;

                    page.render({ canvasContext: context, viewport: viewport }).promise.then(function () {
                        const base64Image = canvas.toDataURL("image/jpeg");

                        const imageElement = document.getElementById("image");
                        imageElement.src = base64Image;
                        imageElement.style.display = "block";

                        sessionStorage.setItem("uploadedImage", base64Image);

                        document.getElementById("rotate-button").disabled = false;
                        document.dispatchEvent(new Event("imageLoaded"));

                        resolve();
                    });
                });
            }).catch((error) => {
                reject(error);
            });
        };
        fileReader.readAsArrayBuffer(file);
    });
}

// ✅ Function to finalize upload (hide file input and prevent multiple uploads)
function finalizeUpload() {
    const fileInput = document.getElementById("upload-drawing");
    const rotateButton = document.getElementById("rotate-button");
    const imageElement = document.getElementById("image");
    let cleanImageElement = document.getElementById("clean-image");

    // ✅ Ensure clean-image element exists
    if (!cleanImageElement) {
        cleanImageElement = document.createElement("img");
        cleanImageElement.id = "clean-image";
        cleanImageElement.style.display = "none"; // Keep it hidden
        imageElement.parentElement.appendChild(cleanImageElement); // Append inside the same parent
    }

    // ✅ Store the clean image only once
    if (!cleanImageElement.src) {
        cleanImageElement.src = imageElement.src;
    }

    if (fileInput) {
        fileInput.style.display = "none";
        fileInput.classList.add("d-none");
    }

    rotateButton.disabled = false;
    document.dispatchEvent(new Event("imageLoaded"));
}

// ✅ Function to reset the drawing and allow new upload
function resetDrawing() {
    sessionStorage.removeItem("uploadedImage");

    const imageElement = document.getElementById("image");
    const fileInput = document.getElementById("upload-drawing");
    const rotateButton = document.getElementById("rotate-button");

    imageElement.src = "";
    imageElement.style.display = "none";

    fileInput.style.display = "block";
    fileInput.classList.remove("d-none");
    fileInput.value = "";

    rotateButton.disabled = true;
}

// ✅ Rotate Image Physically in <img> Tag and Refresh Page
function image_rotate90() {
    const imageElement = document.getElementById("image");
    if (!imageElement || !imageElement.src) {
        return;
    }

    const canvas = document.createElement("canvas");
    const ctx = canvas.getContext("2d");
    const img = new Image();

    img.src = imageElement.src;

    img.onload = function () {
        let currentAngle = parseInt(imageElement.getAttribute("flip_angle")) || 0;
        let newAngle = (currentAngle + 90) % 360;
        imageElement.setAttribute("flip_angle", newAngle);

        if (newAngle === 90 || newAngle === 270) {
            canvas.width = img.height;
            canvas.height = img.width;
        } else {
            canvas.width = img.width;
            canvas.height = img.height;
        }

        ctx.translate(canvas.width / 2, canvas.height / 2);
        ctx.rotate((90 * Math.PI) / 180);
        ctx.drawImage(img, -img.width / 2, -img.height / 2);

        const rotatedImageSrc = canvas.toDataURL("image/jpeg");

        sessionStorage.setItem("uploadedImage", rotatedImageSrc);
        sessionStorage.setItem("flipAngle", newAngle);

        setTimeout(() => {
            location.reload();
        }, 300);
    };
}
