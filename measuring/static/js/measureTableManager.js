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

    highlightSelectedRow: function (row) {
        this.clearRowHighlights();
        row.classList.add("selected-row");
    },
    
    clearRowHighlights: function () {
        document.querySelectorAll("#measure-dimension-table tbody tr").forEach(row => {
            row.classList.remove("selected-row");
        });
    }
    
};
