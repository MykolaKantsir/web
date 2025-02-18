// ✅ Function to add a new row with structured dimension data
function addRow(content, cropBoxData, isDimensionVertical, general_tolerance = 0.1, manualMin = null, manualMax = null) {
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

    // ✅ Handle tolerances (manually entered or calculated)
    let min = manualMin !== null ? manualMin : "";
    let max = manualMax !== null ? manualMax : "";

    if (manualMin === null || manualMax === null) {
        [min, max] = calculateTolerances(normalizedValue, general_tolerance);
    }

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

    // ✅ Attach event listeners for preview
    newRow.addEventListener("mouseenter", renderPreview);
    newRow.querySelectorAll("input").forEach((input) => {
        input.addEventListener("focus", renderPreview);
    });

    // ✅ Append the new row to the table
    tableBody.appendChild(newRow);
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

// ✅ Function to calculate tolerances correctly
function calculateTolerances(value, general_tolerance) {
    let cleanedValue = value.replace(",", ".").trim();

    if (!/^\d*\.?\d+$/.test(cleanedValue)) {
        return [null, null];
    }

    const parsedValue = parseFloat(cleanedValue);
    if (isNaN(parsedValue)) {
        return [null, null];
    }

    let min = parsedValue - general_tolerance;
    let max = parsedValue + general_tolerance;

    if (min < 0) min = 0;

    min = parseFloat(min.toFixed(10)).toString();
    max = parseFloat(max.toFixed(10)).toString();

    return [min, max];
}
