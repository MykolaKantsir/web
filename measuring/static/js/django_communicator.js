// ✅ Function to send cropped dimension data to Django
function sendDimensionData(dimensionData) {
    console.log("📡 Sending dimension data to Django:", dimensionData);
    // TODO: Implement AJAX POST request to Django
}

// ✅ Function to save uploaded drawing details in Django
function saveDrawing(drawingData) {
    console.log("📡 Saving drawing data to Django:", drawingData);
    // TODO: Implement AJAX POST request to Django
}

// ✅ Function to fetch saved drawing and dimensions when the page loads
function fetchDrawingData() {
    console.log("📡 Fetching drawing and dimensions from Django...");
    // TODO: Implement AJAX GET request to Django
}

// ✅ Function to update an existing dimension in Django
function updateDimension(id, newData) {
    console.log(`📡 Updating dimension ID ${id} with data:`, newData);
    // TODO: Implement AJAX PUT request to Django
}

// ✅ Function to delete a dimension from Django
function deleteDimension(id) {
    console.log(`📡 Deleting dimension ID ${id} from Django`);
    // TODO: Implement AJAX DELETE request to Django
}
