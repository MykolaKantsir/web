const measureDrawingManager = {
    init: async function (drawingId, drawingData) {
        if (!drawingId) {
            console.log("No drawing requested. Skipping initialization.");
            return; // Stop execution if no drawingId is provided
        }

        const drawingImageBase64 = drawingData?.drawing?.drawing_image_base64;
        
        if (drawingImageBase64 && drawingImageBase64 !== "") {
            this.showDrawing(drawingImageBase64);
        } else {
            console.log("No drawing found, searching in Monitor G5...");
            await this.handleNoDrawing();
        }
    },

    showDrawing: function (base64Image) {
        const drawingImage = document.getElementById("measure-image");
        drawingImage.src = `data:image/png;base64,${base64Image}`;
        drawingImage.style.display = "block";

        // Hide file input
        document.getElementById("upload-measure").style.display = "none";
    },

    handleNoDrawing: async function () {
        console.log("Handling no drawing case...");

        // Search in Monitor G5
        await this.searchInMonitorG5();
    },

    searchInMonitorG5: async function () {
        console.log("Searching for drawing in Monitor G5...");
        
        try {
            const response = await fetch("/measuring/api/search_monitor_g5/", {
                method: "GET",
                credentials: "include",
            });

            if (!response.ok) {
                throw new Error("Failed to search in Monitor G5");
            }

            const data = await response.json();
            if (data.success && data.drawing?.drawing_image_base64) {
                this.showDrawing(data.drawing.drawing_image_base64);
            } else {
                console.log("No drawing found in Monitor G5.");
            }
        } catch (error) {
            console.error("❌ Error searching in Monitor G5:", error);
        }
    }
};
