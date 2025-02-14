document.addEventListener("DOMContentLoaded", function () {
    console.log("upload_file.js loaded and ready!");

    const fileInput = document.getElementById("upload-drawing");
    const fileNameDisplay = document.getElementById("file-name");
    const imageElement = document.getElementById("image");

    if (!fileInput || !fileNameDisplay || !imageElement) {
        console.error("Some elements are missing! Check your HTML IDs.");
        return;
    }

    fileInput.addEventListener("change", function (event) {
        const file = event.target.files[0];

        if (!file) {
            console.warn("No file selected.");
            return;
        }

        const fileName = file.name;
        const fileType = file.type;
        const virtualPath = `/virtual/path/${fileName}`; // Simulated file path

        console.log(`📂 Selected File: ${fileName}`);
        console.log(`📁 Virtual Path: ${virtualPath}`);

        if (fileType === "application/pdf") {
            console.log("📜 PDF detected, processing...");

            processPDF(file, fileName, virtualPath).then(() => {
                finalizeUpload();
            });

        } else if (fileType === "image/jpeg" || fileType === "image/png") {
            console.log("🖼️ Image detected, displaying preview...");

            const fileReader = new FileReader();
            fileReader.onload = function (e) {
                const base64Image = e.target.result;
                imageElement.src = base64Image;
                imageElement.style.display = "block";

                // ✅ Save in session storage
                sessionStorage.setItem("uploadedImage", base64Image);
                sessionStorage.setItem("uploadedFileName", fileName);
                sessionStorage.setItem("uploadedFilePath", virtualPath);

                finalizeUpload();
            };
            fileReader.readAsDataURL(file);
        } else {
            alert("Unsupported file type. Please upload a PDF or an image.");
        }
    });

    // ✅ Load stored image after page refresh
    const storedImage = sessionStorage.getItem("uploadedImage");
    const storedFileName = sessionStorage.getItem("uploadedFileName");
    const storedFilePath = sessionStorage.getItem("uploadedFilePath");

    if (storedImage) {
        imageElement.src = storedImage;
        imageElement.style.display = "block";

        console.log(`✅ Restored File: ${storedFileName}`);
        console.log(`✅ Restored Path: ${storedFilePath}`);

        finalizeUpload();
    }
});

// ✅ Function to process the uploaded PDF and convert it to an image
function processPDF(file, fileName, virtualPath) {
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

                        // ✅ Save in session storage
                        sessionStorage.setItem("uploadedImage", base64Image);
                        sessionStorage.setItem("uploadedFileName", fileName);
                        sessionStorage.setItem("uploadedFilePath", virtualPath);

                        console.log(`📂 PDF Converted: ${fileName}`);
                        console.log(`📁 Saved Path: ${virtualPath}`);

                        resolve();
                    });
                });
            }).catch((error) => {
                console.error("❌ Error processing PDF:", error);
                reject();
            });
        };
        fileReader.readAsArrayBuffer(file);
    });
}

// ✅ Function to hide file input & file name display, and prevent continuous reloads
function finalizeUpload() {
    console.log("✅ Finalizing upload: Hiding file input and file name display.");

    const fileInput = document.getElementById("upload-drawing");
    const fileNameDisplay = document.getElementById("file-name");

    if (fileInput) {
        fileInput.style.display = "none"; // Hide file input
    }
    if (fileNameDisplay) {
        fileNameDisplay.style.display = "none"; // Hide file name display
    }

    // ✅ Prevent continuous page reloads
    if (!sessionStorage.getItem("pageReloaded")) {
        sessionStorage.setItem("pageReloaded", "true");
        setTimeout(() => {
            location.reload();
        }, 500);
    }
}
