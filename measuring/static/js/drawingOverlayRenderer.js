// drawingOverlayRenderer.js

const drawingOverlayRenderer = {
    protocols: [],
    pages: [],

    async init(protocols) {
        this.protocols = protocols;
        this.pages = [];

        for (const protocol of protocols) {
            const { canvas, width, height, imageData, orientation } =
                await this.renderProtocolToCanvas(protocol);

            this.pages.push({
                imageData,
                orientation,
                protocol,
                width,
                height
            });
        }

        this.generatePDF();
    },

    async renderProtocolToCanvas(protocol) {
        const canvas = document.createElement("canvas");
        const ctx = canvas.getContext("2d");

        const img = new Image();
        img.src = `data:image/png;base64,${protocol.drawing_image_base64}`;

        await new Promise(resolve => {
            img.onload = () => {
                canvas.width = img.naturalWidth;
                canvas.height = img.naturalHeight;
                ctx.drawImage(img, 0, 0);
                resolve();
            };
        });

        // Overlay metadata in top-left corner (text box with transparent bg)
        this.renderMetadataOverlay(ctx, protocol);

        // Draw dimension rectangles and measured values
        this.renderDimensions(ctx, protocol.dimensions);

        const imageData = canvas.toDataURL("image/png");
        const aspectRatio = canvas.width / canvas.height;
        const orientation = aspectRatio > 1 ? "landscape" : "portrait";

        return { canvas, imageData, width: canvas.width, height: canvas.height, orientation };
    },

    renderMetadataOverlay(ctx, protocol) {
        const padding = 8;
        const fontSize = 18;
        const lines = [
            `Drawing: ${protocol.drawing}`,
            `Protocol ID: ${protocol.protocol_id}`,
            `Date: ${protocol.protocol_datetime.split("T")[0]}`
        ];

        ctx.font = `bold ${fontSize}px Arial`;
        const textWidth = Math.max(...lines.map(line => ctx.measureText(line).width));
        const boxHeight = lines.length * (fontSize + 4);

        // Semi-transparent white box
        ctx.fillStyle = "rgba(255, 255, 255, 0.85)";
        ctx.fillRect(padding, padding, textWidth + 2 * padding, boxHeight);

        ctx.fillStyle = "#000";
        lines.forEach((line, i) => {
            ctx.fillText(line, padding * 2, padding + (i + 1) * (fontSize + 2) - 4);
        });
    },

    renderDimensions(ctx, dimensions) {
        dimensions.forEach(dim => {
            const { x, y, width: w, height: h } = dim;

            ctx.fillStyle = "#ffffff";
            ctx.fillRect(x, y, w, h);

            ctx.strokeStyle = "#000000";
            ctx.lineWidth = 2;
            ctx.strokeRect(x, y, w, h);

            ctx.fillStyle = "#000000";
            ctx.font = "bold 16px Arial";
            ctx.textAlign = "center";
            ctx.textBaseline = "middle";

            const text = String(dim.measured_value);
            if (dim.is_vertical) {
                ctx.save();
                ctx.translate(x + w / 2, y + h / 2);
                ctx.rotate(-Math.PI / 2);
                ctx.fillText(text, 0, 0);
                ctx.restore();
            } else {
                ctx.fillText(text, x + w / 2, y + h / 2);
            }
        });
    },

    generatePDF() {
    const { jsPDF } = window.jspdf;
    const firstPage = this.pages[0];
    const pdf = new jsPDF(firstPage.orientation, "mm", "a4");

    const margin = 10; // consistent margin around the image

    this.pages.forEach((page, index) => {
        const { imageData, orientation, width, height } = page;

        if (index > 0) {
            pdf.addPage(orientation, "a4");
        }

        const pageWidth = pdf.internal.pageSize.getWidth();
        const pageHeight = pdf.internal.pageSize.getHeight();

        const imageAspect = width / height;
        const targetWidth = pageWidth - 2 * margin;
        const targetHeight = targetWidth / imageAspect;

        // Optional: auto-adjust if height overflows page
        const finalHeight = (targetHeight + 2 * margin > pageHeight)
            ? pageHeight - 2 * margin
            : targetHeight;

        const finalWidth = finalHeight * imageAspect;

        // Center horizontally if width shrinks
        const offsetX = (pageWidth - finalWidth) / 2;
        const offsetY = margin;

        pdf.addImage(imageData, "PNG", offsetX, offsetY, finalWidth, finalHeight);
    });

    this.savePDF(pdf);
    },

    savePDF(pdf) {
        pdf.save("overlay_protocols.pdf");
    }
};
