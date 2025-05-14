const measureInputManager = {
    inputField: null,
    submitButton: null,
    
    init: function () {
        console.log("Initializing measureInputManager...");
        this.inputField = document.getElementById("measurement-input");
        this.submitButton = document.getElementById("submit-measurement");
        
        if (this.inputField && this.submitButton) {
            this.inputField.addEventListener("keypress", (event) => {
                if (event.key === "Enter") {
                    this.submitMeasurement();
                }
            });
            this.submitButton.addEventListener("click", () => this.submitMeasurement());
        }
    },

    selectDimension: function (row) {
        if (!this.inputField) {
            console.error("❌ Measurement input field not found");
            return;
        }
    
        // Clear input field before setting new values
        this.inputField.value = "";
    
        // Extract data from the selected row
        const dimensionId = row.querySelector(".dimension-id").textContent.trim();
        const drawingId = document.body.dataset.drawingId;
        const value = row.querySelector(".value-cell").textContent;
        const min = row.querySelector(".min-cell").textContent;
        const max = row.querySelector(".max-cell").textContent;
    
        console.log("Setting measurement input field data:", { drawingId, dimensionId, value, min, max });
    
        // Store IDs as data attributes inside the input field
        this.inputField.dataset.drawingId = drawingId;
        this.inputField.dataset.dimensionId = dimensionId;
    
        // Update placeholder text with dimension info
        this.inputField.placeholder = `${value} [${min} : ${max}]`;
    
        // Highlight the selected row
        measureTableManager.highlightSelectedRow(row);
    },

    submitMeasurement: async function () {
    const input = this.inputField;
    const measuredValue = parseFloat(input.value);

    if (!input || isNaN(measuredValue) || measuredValue <= 0) {
        console.error("❌ Invalid measurement value entered");
        alert("Please enter a valid positive number.");
        return;
    }

    const measuredData = {
        measuredValue: measuredValue.toFixed(3),
        dimensionId: input.dataset.dimensionId,
        drawingId: input.dataset.drawingId,
        protocolId: input.dataset.protocolId || null,
    };

    console.log("📤 Submitting measurement:", measuredData);

    let response = await sendMeasurement(measuredData);

    // Handle duplicate detection
    if (response?.duplicate) {
        const confirmReplace = confirm(
            `A value (${response.existing_value}) has already been recorded for this dimension.\nDo you want to replace it with ${measuredValue.toFixed(3)}?`
        );

        if (!confirmReplace) return;

        measuredData.replace = true;
        response = await sendMeasurement(measuredData);
    }

    // Final success check
    if (response?.success && response.protocolId && response.dimensionId) {
        console.log("✅ Measurement saved successfully:", response);
        input.dataset.protocolId = response.protocolId;
        measureTableManager.markAsMeasured(response.dimensionId);
        measureTableManager.updateMeasuredValue(response.dimensionId, measuredData.measuredValue);
        input.value = "";
        this.selectNextDimension(response.dimensionId);
    } else {
        console.error("❌ Failed to save measurement");
        alert("Failed to save measurement. Please try again.");
    }
    },

    selectNextDimension: function (currentDimensionId) {
        const rows = document.querySelectorAll("#measure-dimension-table tbody tr");
        let selectNext = false;
        for (let row of rows) {
            const rowDimensionId = row.querySelector(".dimension-id").textContent.trim();
            const statusCell = row.querySelector(".status-column");
    
            if (selectNext) {
                // Skip rows that are already marked as measured
                if (!statusCell || statusCell.innerHTML.trim() !== "✅") {
                    this.selectDimension(row);
                    return;
                }
            }
    
            if (rowDimensionId === String(currentDimensionId)) {
                selectNext = true;
            }
        }
    }
};
