document.addEventListener("DOMContentLoaded", async function () {
    let drawingId = document.body.dataset.drawingId || null;

    if (!drawingId) {
        console.error("❌ No drawing requested. Exiting initialization.");
        return;
    }

    const drawingData = await django_communicator.getDrawingData(drawingId);

    if (drawingData) {
        await measureDrawingManager.init(drawingId, drawingData);
        
        // ✅ Populate table with dimensions
        if (drawingData.dimensions) {
            measureTableManager.populateTable(drawingData.dimensions);
        }
    }

    // ✅ Initialize event listeners for table and input interactions
    measureInputManager.init();
    measurePreviewManager.init();
    navigationPanelManager.init();
});
