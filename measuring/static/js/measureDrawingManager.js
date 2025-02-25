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
    },

    markDimension: function (dimension, rowNumber, color = 'orange') {
        const imageElement = document.getElementById("measure-image");
        if (!imageElement || !imageElement.src) {
            return;
        }
    
        const img = new Image();
        img.src = imageElement.src;
    
        img.onload = function () {
            const canvas = document.createElement("canvas");
            canvas.width = img.naturalWidth;
            canvas.height = img.naturalHeight;
    
            const ctx = canvas.getContext("2d");
            ctx.drawImage(img, 0, 0);
    
            // Draw rectangle
            ctx.strokeStyle = color;
            ctx.lineWidth = 2;
            ctx.strokeRect(dimension.x, dimension.y, dimension.width, dimension.height);
    
            // Draw row number
            ctx.font = 'bold 24px Arial';
            ctx.fillStyle = color;
            ctx.fillText(rowNumber, dimension.x, dimension.y - 10);
    
            // Update image source
            imageElement.src = canvas.toDataURL();
        };
    },
    
    markAllDimensions: function (cleanDrawing, dimensions, color = 'orange') {
        if (!cleanDrawing || !cleanDrawing.src || dimensions.length === 0) {
            return;
        }
    
        const img = new Image();
        img.src = cleanDrawing.src;
    
        img.onload = function () {
            const canvas = document.createElement("canvas");
            canvas.width = img.naturalWidth;
            canvas.height = img.naturalHeight;
    
            const ctx = canvas.getContext("2d");
            ctx.drawImage(img, 0, 0);
    
            // Iterate over dimensions and draw markings
            dimensions.forEach((dim, index) => {
                ctx.strokeStyle = color;
                ctx.lineWidth = 2;
                ctx.strokeRect(dim.x, dim.y, dim.width, dim.height);
    
                // Draw row number
                ctx.font = 'bold 24px Arial';
                ctx.fillStyle = color;
                ctx.fillText(index + 1, dim.x, dim.y - 10);
            });
    
            // Update image source
            document.getElementById("measure-image").src = canvas.toDataURL();
        };
    }    
};
