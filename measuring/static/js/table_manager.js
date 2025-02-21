// ✅ Function to add a new row with structured dimension data
function addRow(content, cropBoxData, isDimensionVertical, toleranceLevel = "M") {
    const tableBody = document.querySelector("#data-table tbody");
    const rowTemplate = document.getElementById("row-template");

    if (!rowTemplate) {
        return;
    }

    const newRow = rowTemplate.cloneNode(true);
    newRow.classList.remove("d-none");
    newRow.removeAttribute("id");

    // ✅ Determine row number
    const rowCount = tableBody.querySelectorAll("tr:not(#row-template)").length + 1;
    newRow.querySelector(".row-number").textContent = rowCount;

    // ✅ Convert value format (replace comma with dot)
    let normalizedValue = content ? content.replace(",", ".").trim() : "";
    let parsedValue = parseFloat(normalizedValue);

    if (!isNaN(parsedValue)) {
        normalizedValue = parsedValue.toString();
    }

    newRow.querySelector(".value-input").value = normalizedValue || "";

    // ✅ Assign unique dimension ID
    const dimensionId = `dimension-${rowCount}`;
    newRow.querySelector(".dimension-id").value = dimensionId;

    // ✅ Store crop data in hidden fields
    newRow.querySelector(".crop-x").value = cropBoxData.x.toFixed(2);
    newRow.querySelector(".crop-y").value = cropBoxData.y.toFixed(2);
    newRow.querySelector(".crop-width").value = cropBoxData.width.toFixed(2);
    newRow.querySelector(".crop-height").value = cropBoxData.height.toFixed(2);
    newRow.querySelector(".is-vertical").value = isDimensionVertical ? "1" : "0";

    // ✅ Get tolerance based on the selected level ("c", "m", or "f")
    let [min, max] = calculateTolerances(normalizedValue, toleranceLevel);

    newRow.querySelector(".min-input").value = min !== null ? min : "";
    newRow.querySelector(".max-input").value = max !== null ? max : "";

    // ✅ Assign unique name for radio button group
    const uniqueRadioName = `type-selection-${rowCount}`;
    newRow.querySelectorAll(".btn-check").forEach((radio, index) => {
        radio.name = uniqueRadioName;
        radio.id = `type${index + 1}-row${rowCount}`;
        const label = newRow.querySelector(`label[for="type${index + 1}"]`);
        if (label) {
            label.setAttribute("for", `type${index + 1}-row${rowCount}`); 
        }
    });

    // ✅ Attach event listener for Enter key on value input field
    newRow.querySelector(".value-input").addEventListener("keydown", handleValueChange);

    // ✅ Attach event listeners for preview
    newRow.addEventListener("mouseenter", renderPreview);
    newRow.querySelectorAll("input").forEach((input) => {
        input.addEventListener("focus", renderPreview);
    });

    // ✅ Append the new row to the table
    tableBody.appendChild(newRow);

    // ✅ Validate & auto-save if OCR produced valid values
    if (validateDimension(newRow)) {
        saveDimension(newRow);
    }
}

// ✅ Function to update tolerances after adding all test dimensions
function updateTolerances(testDimensions) {
    const rows = document.querySelectorAll("#data-table tbody tr:not(#row-template)");

    testDimensions.forEach((dim, index) => {
        const row = rows[index];
        if (row) {
            row.querySelector(".min-input").value = dim.min;
            row.querySelector(".max-input").value = dim.max;
        }
    });
}

// ✅ General Tolerance Lookup Table (ISO 2768-based)
// "c" = Coarse, "m" = Medium, "f" = Fine
const toleranceTable = {
    "0-3": { "c": 0.2, "m": 0.1, "f": 0.05 },
    "3-6": { "c": 0.3, "m": 0.1, "f": 0.05 },
    "6-30": { "c": 0.5, "m": 0.2, "f": 0.1 },
    "30-120": { "c": 0.8, "m": 0.3, "f": 0.15 },
    "120-400": { "c": 1.2, "m": 0.5, "f": 0.2 },
    "400-1000": { "c": 2, "m": 0.8, "f": 0.3 },
    "1000-2000": { "c": 3, "m": 1.2, "f": 0.5 },
    "2000-4000": { "c": 4, "m": 2, "f": 0.5 },
};

// ✅ Function to calculate tolerances based on size and tolerance level
function calculateTolerances(value) {
    if (typeof value !== "string") {
        value = value.toString(); // ✅ Convert number to string if needed
    }

    let cleanedValue = value.replace(",", ".").trim();

    if (!/^\d*\.?\d+$/.test(cleanedValue)) {
        return [null, null]; // Invalid input
    }

    const parsedValue = parseFloat(cleanedValue);
    if (isNaN(parsedValue)) {
        return [null, null];
    }

    // ✅ Get selected tolerance level from HTML
    const selectedTolerance = document.querySelector('input[name="mode-selection"]:checked')?.id.split("-")[1] || "M";

    // ✅ Determine the correct tolerance range
    let selectedValue = null;
    for (const range in toleranceTable) {
        const [min, max] = range.split("-").map(Number);
        if (parsedValue >= min && parsedValue < max) {
            selectedValue = toleranceTable[range][selectedTolerance];
            break;
        }
    }

    if (selectedValue === null) {
        return [null, null]; // Out of range
    }

    let min = parsedValue - selectedValue;
    let max = parsedValue + selectedValue;

    if (min < 0) min = 0;

    min = parseFloat(min.toFixed(10)).toString();
    max = parseFloat(max.toFixed(10)).toString();

    return [min, max];
}


// ✅ Function to handle value changes in the table
function handleValueChange(event) {
    if (event.key === "Enter") {
        const inputField = event.target;
        const row = inputField.closest("tr"); // ✅ Find the closest row

        if (!row || row.id === "row-template") {
            console.warn("⚠ No valid row found. Ignoring input.");
            return;
        }

        const value = parseFloat(inputField.value.replace(",", ".").trim());
        if (isNaN(value)) {
            alert("⚠ Invalid number entered.");
            return;
        }

        const selectedTolerance = document.querySelector('input[name="mode-selection"]:checked')?.id.split("-")[1] || "M";
        const [min, max] = calculateTolerances(value, selectedTolerance);

        row.querySelector(".min-input").value = min;
        row.querySelector(".max-input").value = max;

        saveDimension(row); // ✅ Save the dimension data
    }
}

// ✅ Function to send dimension data & update row sync status
async function saveDimension(row) {
    const drawingId = document.getElementById("image").getAttribute("drawing-id");
    if (!drawingId) {
        console.error("❌ No drawing ID found. Cannot save dimension.");
        return;
    }

    // ✅ Get dimension ID (convert empty string to null)
    const dimensionId = row.getAttribute("dimension-id") || null;

    const dimensionData = {
        dimension_id: dimensionId,  // ✅ Send null if new
        drawing_id: drawingId,
        x: parseFloat(row.querySelector(".crop-x").value),
        y: parseFloat(row.querySelector(".crop-y").value),
        width: parseFloat(row.querySelector(".crop-width").value),
        height: parseFloat(row.querySelector(".crop-height").value),
        value: row.querySelector(".value-input").value.trim(),
        min_value: parseFloat(row.querySelector(".min-input").value),
        max_value: parseFloat(row.querySelector(".max-input").value),
        is_vertical: row.querySelector(".is-vertical").value === "1",
        page: 1,  // Adjust if multiple pages exist
        type_selection: parseInt(row.querySelector('input[name^="type-selection-"]:checked')?.value || "2")
    };

    // ✅ Get the sync status cell
    let syncStatusCell = row.querySelector(".sync-status");
    if (!syncStatusCell) {
        syncStatusCell = document.createElement("td");
        syncStatusCell.classList.add("sync-status");
        row.appendChild(syncStatusCell);
    }

    // ⏳ Show loading icon while sending
    syncStatusCell.innerHTML = "⏳";

    try {
        const updatedDimensionId = await sendDimensionData(dimensionData);
        if (updatedDimensionId) {
            syncStatusCell.innerHTML = "✅";  // Success
            row.setAttribute("dimension-id", updatedDimensionId);  // Store new dimension ID in row
        } else {
            syncStatusCell.innerHTML = "⚠️";  // Failure
        }
    } catch (error) {
        syncStatusCell.innerHTML = "❌";  // Error
    }
}

// ✅ Function to validate if a dimension row contains valid data
function validateDimension(row) {
    if (!row || row.id === "row-template") {
        return false; // ❌ Ignore template row
    }

    // ✅ Get input values
    const valueInput = row.querySelector(".value-input");
    const minInput = row.querySelector(".min-input");
    const maxInput = row.querySelector(".max-input");

    const value = parseFloat(valueInput?.value.replace(",", ".").trim());
    const minValue = parseFloat(minInput?.value.replace(",", ".").trim());
    const maxValue = parseFloat(maxInput?.value.replace(",", ".").trim());

    // ✅ Ensure all values are valid positive numbers
    if (isNaN(value) || value <= 0 || isNaN(minValue) || minValue <= 0 || isNaN(maxValue) || maxValue <= 0) {
        return false; // ❌ Invalid data
    }

    return true; // ✅ Valid data
}
