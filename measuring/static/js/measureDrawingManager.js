const measureDrawingManager = {
    dimensionsData: [], // ✅ Stores rectangle positions and corresponding rows
    scaleX: 1, // ✅ Scaling factors (for transformation handling)
    scaleY: 1,

    init: async function (drawingId, drawingData) {
        console.log("🔄 Initializing measureDrawingManager...");
        if (!drawingId) {
            console.error("❌ No drawing requested. Skipping initialization.");
            return;
        }

        console.log("📥 Fetching drawing...");
        const drawingImageBase64 = drawingData?.drawing?.drawing_image_base64;

        if (drawingImageBase64 && drawingImageBase64 !== "") {
            console.log("🖼️ Drawing found, rendering...");
            this.showDrawing(drawingImageBase64);
        } else {
            console.error("❌ No drawing found, searching in Monitor G5...");
            await this.handleNoDrawing();
        }

        // ✅ Initialize dimensions once the drawing is set
        if (drawingData?.dimensions) {
            this.initializeDimensions(drawingData.dimensions);
        }
    },

    showDrawing: function (base64Image) {
        console.log("🎨 Entering showDrawing...");
        const canvas = this.getCanvasImage();
        const ctx = canvas.getContext("2d");
        const img = new Image();
        img.src = `data:image/png;base64,${base64Image}`;

        img.onload = function () {
            console.log(`🖼️ Original Image Size: ${img.naturalWidth}x${img.naturalHeight}`);
            console.log(`📏 Canvas Client Size: ${canvas.clientWidth}x${canvas.clientHeight}`);

            measureDrawingManager.applyTransformations(canvas, img);

            canvas.width = img.naturalWidth;
            canvas.height = img.naturalHeight;
            console.log(`🖌️ Canvas Set to: ${canvas.width}x${canvas.height}`);

            ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
            console.log(`✅ Drawing Rendered at: ${canvas.width}x${canvas.height}`);

            document.getElementById("clean-drawing").src = img.src;
        };
    },

    applyTransformations: function (canvas, img) {
        console.log("🔄 Applying transformations...");
        this.scaleX = canvas.clientWidth / img.naturalWidth;
        this.scaleY = canvas.clientHeight / img.naturalHeight;
        console.log(`🔍 Computed Scale Factors - scaleX: ${this.scaleX}, scaleY: ${this.scaleY}`);
    },

    getCanvasImage: function () {
        return document.getElementById("measure-canvas");
    },

    getCleanImage: function () {
        return document.getElementById("clean-drawing");
    },

    initializeDimensions: function (dimensions) {
        console.log("📥 Initializing dimensions...");
        
        // ✅ Populate dimension data before drawing
        this.populateDimensionsData(dimensions);

        // ✅ Mark all dimensions after setting up the data
        this.markAllDimensions();
    },

    populateDimensionsData: function (dimensions) {
        console.log("📌 Populating dimensionsData...");
        this.dimensionsData = [];

        // ✅ Get all table rows (excluding header row)
        const rows = Array.from(document.querySelectorAll("#measure-dimension-table tbody tr")).slice(1);

        dimensions.forEach((dim, index) => {
            const row = rows[index] || null;
            if (!row) {
                console.warn(`⚠️ No row found for Dimension ${index + 1}`);
                return;
            }

            this.dimensionsData.push({
                originalX: dim.x,
                originalY: dim.y,
                originalWidth: dim.width,
                originalHeight: dim.height,
                row: row
            });
        });

        console.log("✅ Dimensions data populated.");
    },

    markDimension: function (dimData, color = "orange", canvas = null) {
        if (!canvas) canvas = this.getCanvasImage();
        if (!canvas) {
            console.error("❌ No valid canvas found.");
            return;
        }

        const ctx = canvas.getContext("2d");

        // ✅ Apply transformations using stored scaling factors
        const scaledX = dimData.originalX * this.scaleX;
        const scaledY = dimData.originalY * this.scaleY;
        const scaledWidth = dimData.originalWidth * this.scaleX;
        const scaledHeight = dimData.originalHeight * this.scaleY;

        console.log(`📐 Marking Dimension - Row: ${dimData.row.rowIndex}, Scaled Position: (${scaledX}, ${scaledY}), Size: ${scaledWidth}x${scaledHeight}`);

        ctx.strokeStyle = color;
        ctx.lineWidth = 2;
        ctx.strokeRect(scaledX, scaledY, scaledWidth, scaledHeight);

        ctx.font = "bold 24px Arial";
        ctx.fillStyle = color;
        ctx.fillText(dimData.row.rowIndex, scaledX, scaledY - 10);

        return canvas;
    },

    markAllDimensions: function (color = "orange") {
        console.log("🔄 Marking all dimensions...");
        let canvas = this.getCanvasImage();
        const ctx = canvas.getContext("2d");

        if (!canvas || this.dimensionsData.length === 0) {
            console.error("❌ No valid canvas or empty dimensions.");
            return;
        }

        // ✅ Clear canvas before drawing
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // ✅ Draw all dimensions using the same canvas instance
        this.dimensionsData.forEach(dimData => {
            canvas = this.markDimension(dimData, color, canvas);
        });

        console.log("✅ All dimensions marked.");
    },

    initClickDetection: function () {
        console.log("🔄 Initializing click detection...");
        const canvas = this.getCanvasImage();
        if (!canvas) return;

        canvas.addEventListener("click", function (event) {
            const rect = canvas.getBoundingClientRect();
            const clickX = event.clientX - rect.left;
            const clickY = event.clientY - rect.top;

            console.log(`🖱️ Click at: x=${clickX}, y=${clickY}`);

            // ✅ Check if the click is inside any transformed dimension
            for (let dimData of measureDrawingManager.dimensionsData) {
                const scaledX = dimData.originalX * measureDrawingManager.scaleX;
                const scaledY = dimData.originalY * measureDrawingManager.scaleY;
                const scaledWidth = dimData.originalWidth * measureDrawingManager.scaleX;
                const scaledHeight = dimData.originalHeight * measureDrawingManager.scaleY;

                if (
                    clickX >= scaledX && clickX <= scaledX + scaledWidth &&
                    clickY >= scaledY && clickY <= scaledY + scaledHeight
                ) {
                    console.log(`✅ Clicked dimension row: ${dimData.row.rowIndex}`);
                    console.log(`Value: ${dimData.row.querySelector('.value-cell')?.textContent || 'N/A'}`);
                    measureInputManager.selectDimension(dimData.row);
                    return;
                }
            }
            console.log("❌ No dimension found at this click location.");
        });
    }
};

// ✅ Initialize click detection when the page loads
document.addEventListener("DOMContentLoaded", function () {
    measureDrawingManager.initClickDetection();
});
