// templateDownloadManager.js

const templateDownloadManager = {
  init() {
    document.getElementById("download-template-json")?.addEventListener("click", this.downloadJSON);
    document.getElementById("download-template-csv")?.addEventListener("click", this.downloadCSV);
    document.getElementById("download-template-empty-form")?.addEventListener("click", this.downloadEmptyForm);
    document.getElementById("download-template-overlay-pdf")?.addEventListener("click", this.downloadOverlayPDF);
  },

  getDrawingId() {
    return document.getElementById("image")?.getAttribute("drawing-id") || null;
  },

  downloadJSON() {
    const drawingId = templateDownloadManager.getDrawingId();
    if (!drawingId) {
      alert("No drawing saved yet. Please crop at least one dimension first.");
      return;
    }
    window.location.href = `/measuring/api/download_template/?drawing_id=${drawingId}&format=json`;
  },

  downloadCSV() {
    const drawingId = templateDownloadManager.getDrawingId();
    if (!drawingId) {
      alert("No drawing saved yet. Please crop at least one dimension first.");
      return;
    }
    window.location.href = `/measuring/api/download_template/?drawing_id=${drawingId}&format=csv`;
  },

  downloadEmptyForm() {
    const drawingId = templateDownloadManager.getDrawingId();
    if (!drawingId) {
      alert("No drawing saved yet. Please crop at least one dimension first.");
      return;
    }

    fetch(`/measuring/api/empty_protocol_form/?drawing_id=${drawingId}&numbering=true`)
      .then(res => res.json())
      .then(data => {
        drawingOverlayRenderer.renderEmptyForm(data, { numbering: true });
      })
      .catch(err => {
        console.error("Failed to load empty form data:", err);
        alert("Failed to generate empty form.");
      });
  },

  downloadOverlayPDF() {
    const drawingId = templateDownloadManager.getDrawingId();
    if (!drawingId) {
      alert("No drawing saved yet. Please crop at least one dimension first.");
      return;
    }

    fetch(`/measuring/api/empty_protocol_form/?drawing_id=${drawingId}&numbering=true`)
      .then(res => res.json())
      .then(data => {
        drawingOverlayRenderer.renderOverlayForm(data);
      })
      .catch(err => {
        console.error("Failed to load overlay data:", err);
        alert("Failed to generate overlay PDF.");
      });
  }
};

// Initialize when DOM is ready
document.addEventListener("DOMContentLoaded", () => {
  templateDownloadManager.init();
});
