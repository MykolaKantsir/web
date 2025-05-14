const measureTableManager = {
    init: function () {
        console.log("Initializing measureTableManager...");
        this.clearTable();
    },

    clearTable: function () {
        const tableBody = document.querySelector("#measure-dimension-table tbody");
        if (tableBody) {
            // Remove all rows **except** the row template
            tableBody.querySelectorAll("tr:not(#row-template)").forEach(row => row.remove());
        }
    },

    addRow: function (dimension, index) {
        const tableBody = document.querySelector("#measure-dimension-table tbody");
        const rowTemplate = document.getElementById("row-template");
        
        if (!rowTemplate || !tableBody) {
            console.error("❌ Table template or body not found");
            return;
        }

        const newRow = rowTemplate.cloneNode(true);
        newRow.classList.remove("d-none");
        newRow.removeAttribute("id");

        // Set row values
        newRow.querySelector(".row-number").textContent = index + 1;
        newRow.querySelector(".value-cell").textContent = dimension.value || "";
        newRow.querySelector(".min-cell").textContent = dimension.min_value || "";
        newRow.querySelector(".max-cell").textContent = dimension.max_value || "";

        // Store hidden attributes
        newRow.querySelector(".dimension-id").textContent = dimension.id;
        newRow.querySelector(".crop-x").textContent = dimension.x;
        newRow.querySelector(".crop-y").textContent = dimension.y;
        newRow.querySelector(".crop-width").textContent = dimension.width;
        newRow.querySelector(".crop-height").textContent = dimension.height;
        newRow.querySelector(".is-vertical").textContent = dimension.is_vertical ? "1" : "0";
        
        // Attach event listeners
        newRow.addEventListener("click", () => measureInputManager.selectDimension(newRow));
        newRow.addEventListener("mouseenter", () => measurePreviewManager.showPreview(newRow));
        newRow.addEventListener("mouseleave", () => measurePreviewManager.hidePreview());

        // Append to table
        tableBody.appendChild(newRow);
    },

    populateTable: function (dimensions) {
        this.clearTable();
        dimensions.forEach((dimension, index) => {
            this.addRow(dimension, index);
        });
        console.log(`✅ Populated table with ${dimensions.length} dimensions`);
    },

    markAsMeasured: function (dimensionId) {
        const rows = document.querySelectorAll("#measure-dimension-table tbody tr");
        for (let row of rows) {
            const rowDimensionId = row.querySelector(".dimension-id").textContent.trim();
            if (rowDimensionId === String(dimensionId)) {
                const statusCell = row.querySelector(".status-column");
                if (statusCell) {
                    statusCell.innerHTML = "✅"; // Add a green checkmark
                }
                console.log(`✅ Marked dimension ${dimensionId} as measured.`);
                return;
            }
        }
        console.error(`❌ Could not find dimension ${dimensionId} in table.`);
    },

    getRowByDimensionId: function (dimensionId) {
        const rows = document.querySelectorAll("#measure-dimension-table tbody tr");
    
        for (let row of rows) {
            const rowDimensionId = row.querySelector(".dimension-id")?.textContent.trim();
            if (rowDimensionId === dimensionId) {
                return row; // ✅ Found the correct row
            }
        }
    
        console.warn(`⚠️ No row found for Dimension ID: ${dimensionId}`);
        return null; // ✅ Return null if not found
    },    

    highlightSelectedRow: function (row) {
        this.clearRowHighlights();
        row.classList.add("selected-row");
    },
    
    clearRowHighlights: function () {
        document.querySelectorAll("#measure-dimension-table tbody tr").forEach(row => {
            row.classList.remove("selected-row");
        });
    },

    updateMeasuredValue: function (dimensionId, measuredValue) {
        const rows = document.querySelectorAll("#measure-dimension-table tbody tr");

        rows.forEach(row => {
            const dimIdCell = row.querySelector(".dimension-id");
            if (!dimIdCell) return;

            if (dimIdCell.textContent === String(dimensionId)) {
                const mvCell = row.querySelector(".measured-cell");
                const min = parseFloat(row.querySelector(".min-cell").textContent);
                const max = parseFloat(row.querySelector(".max-cell").textContent);

                // Format value by removing trailing zeros
                const formattedValue = parseFloat(measuredValue).toString();

                // Update the cell
                mvCell.textContent = formattedValue;

                // Clear previous styling
                mvCell.classList.remove("bg-success", "bg-danger", "text-white");

                // Apply tolerance-based styling
                const value = parseFloat(measuredValue);
                if (value >= min && value <= max) {
                    mvCell.classList.add("bg-success", "text-white");
                } else {
                    mvCell.classList.add("bg-danger", "text-white");
                }
            }
        });
    }
    
};
