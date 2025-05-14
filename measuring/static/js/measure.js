document.addEventListener("DOMContentLoaded", async function () {
    // ✅ 1. Get drawing ID passed from Django template (set on <body>)
    let drawingId = document.body.dataset.drawingId || null;
    if (!drawingId) {
        console.error("❌ No drawing ID found — cannot proceed.");
        return;
    }

    // ✅ 2. Ask protocolManager if there are unfinished protocols to handle
    // - Shows modal if needed
    // - User can choose to continue or create a new one
    // - Returns selected protocol ID or null
    const selectedProtocolId = await protocolManager.checkAndSelectProtocol(drawingId);

    // ✅ 3. Save selected protocol ID to be used when submitting measurements
    // This ID will be attached to all measurements sent to Django
    if (selectedProtocolId) {
        measureInputManager.selectedProtocolId = selectedProtocolId;
    }

    // ✅ 4. Fetch all drawing data (dimensions, scale, etc.)
    const drawingData = await django_communicator.getDrawingData(drawingId);

    if (drawingData) {
        // ✅ 5. Initialize the drawing manager — handles rendering + overlay logic
        await measureDrawingManager.init(drawingId, drawingData);

        // ✅ 6. If dimensions are available, populate the table
        if (drawingData.dimensions) {
            measureTableManager.populateTable(drawingData.dimensions);

            // ✅ 7. If a protocol was selected, fetch its measured values from the server
            // and apply them to the table (MV column) + visually mark as measured
            if (selectedProtocolId) {
                const protocolData = await django_communicator.getProtocolData(selectedProtocolId);

                if (protocolData?.protocol?.measured_values) {
                    protocolData.protocol.measured_values.forEach(mv => {
                        measureTableManager.updateMeasuredValue(mv.dimension_id, mv.value);
                        measureTableManager.markAsMeasured(mv.dimension_id);
                    });
                    console.log(`✅ Loaded ${protocolData.protocol.measured_values.length} measured values from Protocol #${selectedProtocolId}`);
                } else {
                    console.warn("⚠️ Protocol selected, but no measured values returned.");
                }
            }
        }
    }

    // ✅ 8. Initialize additional interactive tools and UI logic
    measureInputManager.init();       // input and enter button
    measurePreviewManager.init();     // dynamic preview during typing
    navigationPanelManager.init();    // handles nav panel buttons (downloads etc.)
});
