document.addEventListener("DOMContentLoaded", async function () {
    console.log("Measure.js loaded");

    let drawingId = document.body.dataset.drawingId || null;

    if (!drawingId) {
        console.log("No drawing requested. Exiting initialization.");
        return;
    }

    console.log("Fetching drawing data for ID:", drawingId);
    const drawingData = await django_communicator.getDrawingData(drawingId);

    if (drawingData) {
        await measureDrawingManager.init(drawingId, drawingData);
        
        // ✅ Populate table with dimensions
        if (drawingData.dimensions) {
            measureTableManager.populateTable(drawingData.dimensions);
            
            // ✅ Mark all dimensions on the drawing
            measureDrawingManager.markAllDimensions(document.getElementById("measure-image"), drawingData.dimensions);
        }
    }

    // ✅ Initialize event listeners for table and input interactions
    measureInputManager.init();
    measurePreviewManager.init();

    console.log("Measure.js initialization complete");
});
