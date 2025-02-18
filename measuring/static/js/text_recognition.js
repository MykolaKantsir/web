// ✅ Function to recognize text from the cropped image
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

                // ✅ Use Tesseract.js to recognize text
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
