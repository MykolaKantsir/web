// navigationPanelManager.js

const navigationPanelManager = {
  init: function () {
    console.log("📦 Navigation panel initialized.");

    // Assign handlers for download dropdown
    document.getElementById("download-pdf")?.addEventListener("click", this.downloadPDF);
    document.getElementById("download-csv")?.addEventListener("click", this.downloadCSV);
    document.getElementById("download-json")?.addEventListener("click", this.downloadJSON);
    document.getElementById("download-overlay-pdf")?.addEventListener("click", this.downloadOverlayPDF);
  },

  getDrawingId: function () {
    return document.body.dataset.drawingId || null;
  },

  downloadPDF: function () {
    const drawingId = navigationPanelManager.getDrawingId();
    if (!drawingId) return;
    window.location.href = `/measuring/api/download_protocol/?format=pdf&drawing_id=${drawingId}`;
  },

  downloadCSV: function () {
    const drawingId = navigationPanelManager.getDrawingId();
    if (!drawingId) return;
    window.location.href = `/measuring/api/download_protocol/?format=csv&drawing_id=${drawingId}`;
  },

  downloadJSON: function () {
    const drawingId = navigationPanelManager.getDrawingId();
    if (!drawingId) return;
    window.location.href = `/measuring/api/download_protocol/?format=json&drawing_id=${drawingId}`;
  },

  downloadOverlayPDF: function () {
    const drawingId = navigationPanelManager.getDrawingId();
    if (!drawingId) return;

    fetch(`/measuring/api/download_protocol/?format=overlay_pdf&protocol_id=20`)
      .then(res => res.json())
      .then(data => {
        if (data?.protocols?.length > 0) {
          drawingOverlayRenderer.init(data.protocols);  // ✅ updated call
        } else {
          alert("No protocols found for overlay rendering.");
        }
      })
      .catch(err => {
        console.error("❌ Failed to fetch overlay data:", err);
        alert("Failed to generate overlay PDF.");
      });
  }
};

window.navigationPanelManager = navigationPanelManager;
