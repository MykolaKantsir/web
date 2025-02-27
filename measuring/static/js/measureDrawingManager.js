const measureDrawingManager = {
    dimensionsData: [], // ✅ Stores rectangle positions and corresponding rows

    init: async function (drawingId, drawingData) {
        if (!drawingId) {
            console.error("❌ No drawing requested. Skipping initialization.");
            return;
        }

        const drawingImageBase64 = drawingData?.drawing?.drawing_image_base64;
        
        if (drawingImageBase64 && drawingImageBase64 !== "") {
            this.showDrawing(drawingImageBase64);
        } else {
            console.error("❌ No drawing found, searching in Monitor G5...");
            await this.handleNoDrawing();
        }
    },

    showDrawing: function (base64Image) {
        const canvas = document.getElementById("measure-canvas");
        const ctx = canvas.getContext("2d");
        const img = new Image();
        img.src = `data:image/png;base64,${base64Image}`;

        img.onload = function () {
            canvas.width = img.naturalWidth;
            canvas.height = img.naturalHeight;
            ctx.drawImage(img, 0, 0);

            // Store a clean copy
            document.getElementById("clean-drawing").src = img.src;
        };
    },

    markDimension: function (dimension, row, color = 'orange', canvas = null, image = null) {
        if (!canvas) canvas = document.getElementById("measure-canvas");
        if (!image) image = document.getElementById("clean-drawing");
    
        if (!canvas || !image || !image.src) {
            console.error("❌ Canvas or clean drawing not found.");
            return;
        }
    
        const ctx = canvas.getContext("2d");
        
        // Draw dimension on top of existing canvas content (no clearing)
        ctx.strokeStyle = color;
        ctx.lineWidth = 2;
        ctx.strokeRect(dimension.x, dimension.y, dimension.width, dimension.height);
        
        ctx.font = 'bold 24px Arial';
        ctx.fillStyle = color;
        ctx.fillText(row.rowIndex + 1, dimension.x, dimension.y - 10);

        // Store dimension position and corresponding row
        this.dimensionsData.push({ x: dimension.x, y: dimension.y, width: dimension.width, height: dimension.height, row: row });
    },
    
    markAllDimensions: function (dimensions, color = 'orange') {
        const canvas = document.getElementById("measure-canvas");
        const image = document.getElementById("clean-drawing");
    
        if (!canvas || !image || !image.src || dimensions.length === 0) {
            console.error("❌ No clean drawing available or empty dimensions.");
            return;
        }
    
        const ctx = canvas.getContext("2d");
        const img = new Image();
        img.src = image.src;
    
        img.onload = function () {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            ctx.drawImage(img, 0, 0);

            measureDrawingManager.dimensionsData = []; // Clear previous data
    
            // Get all table rows and ensure marking starts from 1
            const rows = document.querySelectorAll("#measure-dimension-table tbody tr");
            dimensions.forEach((dim, index) => {
                const row = rows[index];
                measureDrawingManager.markDimension(dim, row, color, canvas, image);
                console.log(`📏 Dimension ${index + 1}: x=${dim.x}, y=${dim.y}, width=${dim.width}, height=${dim.height}, Row: ${row.rowIndex + 1}, Value: ${dim.value}`);
            });
        };
    },

    initClickDetection: function () {
        const canvas = document.getElementById("measure-canvas");
        if (!canvas) return;
    
        canvas.addEventListener("click", function (event) {
            const rect = canvas.getBoundingClientRect();
            const clickX = event.clientX - rect.left;
            const clickY = event.clientY - rect.top;
    
            console.log(`🖱️ Click at: x=${clickX}, y=${clickY}`);
    
            // Check if the click is inside any dimension
            for (let dimData of measureDrawingManager.dimensionsData) {
                if (
                    clickX >= dimData.x && clickX <= dimData.x + dimData.width &&
                    clickY >= dimData.y && clickY <= dimData.y + dimData.height
                ) {
                    console.log(`✅ Clicked dimension row: ${dimData.row.rowIndex + 1}`);
                    console.log(`Value: ${dimData.row.querySelector('.value-cell')?.textContent || 'N/A'}`);
                    measureInputManager.selectDimension(dimData.row);
                    return;
                }
            }
            console.log("❌ No dimension found at this click location.");
        });
    }
};

// Initialize click detection when the page loads
document.addEventListener("DOMContentLoaded", function () {
    measureDrawingManager.initClickDetection();
});
