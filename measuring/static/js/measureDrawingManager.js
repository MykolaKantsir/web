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
            await this.showDrawing(drawingImageBase64);
        } else {
            console.error("❌ No drawing found, searching in Monitor G5...");
            await this.handleNoDrawing();
        }

        // ✅ Populate table **before** initializing dimensions
        if (drawingData.dimensions) {
            measureTableManager.populateTable(drawingData.dimensions);
        }

        // ✅ Initialize dimensions once the drawing is set
        if (drawingData?.dimensions) {
            this.initializeDimensions(drawingData.dimensions);

        }
        
        // ✅ Apply transformations after the drawing is rendered
        this.applyTransformations(this.getCanvasImage(), this.getCleanImage());
    
        // ✅ Move click detection inside `init()` so it's only initialized once
        this.initClickDetection();
    },

    showDrawing: function (base64Image) {
        console.log("🎨 Entering showDrawing...");
        const canvas = document.getElementById("measure-canvas");
        const ctx = canvas.getContext("2d");
        const img = new Image();
        img.src = `data:image/png;base64,${base64Image}`;
    
        return new Promise((resolve) => { // ✅ Return a Promise that resolves when the image loads
            img.onload = function () {
                console.log("✅ Image loaded! Now setting canvas size...");
                canvas.width = img.naturalWidth;
                canvas.height = img.naturalHeight;
    
                // ✅ Draw the image
                ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
                console.log("✅ Drawing rendered.");
    
                // ✅ Store a clean copy
                document.getElementById("clean-drawing").src = img.src;
    
                resolve(); // ✅ Resolve the promise after the image is fully loaded
            };
        });
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
    
    getTextPosition: function (scaledX, scaledY, scaledWidth, scaledHeight, textPosition) {
        let textX = scaledX;
        let textY = scaledY - 10; // Default: above
    
        if (textPosition === 2) textY = scaledY + scaledHeight + 25; // Below
        if (textPosition === 3) textX = scaledX - 30; // Left
        if (textPosition === 4) textX = scaledX + scaledWidth + 5; // Right
        // More positions can be added later
    
        return { textX, textY };
    },
    
    markDimension: function (dimData, color = "orange", canvas = null) {
        if (!canvas) canvas = this.getCanvasImage();
        if (!canvas) {
            console.error("❌ No valid canvas found.");
            return;
        }
    
        const ctx = canvas.getContext("2d");
    
        // ✅ Apply transformations using stored scaling factors
        const scaledX = dimData.originalX
        const scaledY = dimData.originalY
        const scaledWidth = dimData.originalWidth
        const scaledHeight = dimData.originalHeight
    
        // ✅ Retrieve row number from the first cell in the row
        const rowNumberCell = dimData.row.querySelector("td:first-child");
        const rowNumber = rowNumberCell ? rowNumberCell.textContent.trim() : "??";
    
        console.log(`📐 Marking Dimension - Row: ${rowNumber}, Scaled Position: (${scaledX}, ${scaledY}), Size: ${scaledWidth}x${scaledHeight}`);
    
        ctx.strokeStyle = color;
        ctx.lineWidth = 2;
        ctx.strokeRect(scaledX, scaledY, scaledWidth, scaledHeight);
    
        // ✅ Get text position
        const { textX, textY } = this.getTextPosition(scaledX, scaledY, scaledWidth, scaledHeight, 1);
    
        ctx.font = "bold 24px Arial";
        ctx.fillStyle = color;
        ctx.fillText(rowNumber, textX, textY);
    
        return canvas; // ✅ Return updated canvas
    },
    
    markAllDimensions: function (color = "orange") {
        console.log("🔄 Marking all dimensions...");
        let canvas = this.getCanvasImage();
        if (!canvas || this.dimensionsData.length === 0) {
            console.error("❌ No valid canvas or empty dimensions.");
            return;
        }
    
        const ctx = canvas.getContext("2d");
    
        // ✅ Ensure clean drawing is placed before marking dimensions
        const cleanImage = this.getCleanImage();
        if (!cleanImage || !cleanImage.src) {
            console.error("❌ Clean drawing not found.");
            return;
        }
    
        const img = new Image();
        img.src = cleanImage.src;
    
        img.onload = () => {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            ctx.drawImage(img, 0, 0, canvas.width, canvas.height); // ✅ Draw clean image
    
            // ✅ Draw all dimensions using the **same canvas instance**
            this.dimensionsData.forEach(dimData => {
                canvas = this.markDimension(dimData, color, canvas); // ✅ Keep using updated canvas
            });
    
            console.log("✅ All dimensions marked.");
        };
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
                    console.log(`✅ Clicked dimension row: ${dimData.row.querySelector('.row-number')?.textContent.trim() || 'N/A'}`);
                    console.log(`Value: ${dimData.row.querySelector('.value-cell')?.textContent || 'N/A'}`);
                    const row = measureTableManager.getRowByDimensionId(dimData.row.querySelector(".dimension-id")?.textContent.trim());
                    if (row) {
                        measureInputManager.selectDimension(row);
                    } else {
                        console.warn(`⚠️ No table row found for clicked dimension.`);
                    }
                    return;
                }
            }
            console.log("❌ No dimension found at this click location.");
        });
    },

    handleNoDrawing: async function () {
        // Todo: Implement Monitor G5 drawing retrieval
        console.error("❌ Monitor G5 drawing retrieval not implemented.");
    }
};

