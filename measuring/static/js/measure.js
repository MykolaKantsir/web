// ✅ Main script for measuring functionality

document.addEventListener("DOMContentLoaded", async function () {
    console.log("Measure.js loaded");

    // ✅ Global variable to store current drawing ID
    let drawingId = document.body.dataset.drawingId || null;

    // ✅ If no drawing is requested, do nothing
    if (!drawingId) {
        console.log("No drawing requested. Exiting initialization.");
        return;
    }

    console.log("Fetching drawing data for ID:", drawingId);
    const drawingData = await django_communicator.getDrawingData(drawingId);
    await measureDrawingManager.init(drawingId, drawingData);

    // ✅ Initialize event listeners for table and input interactions
    measureTableManager.init();
    measureInputManager.init();
    measurePreviewManager.init();

    console.log("Measure.js initialization complete");
});
