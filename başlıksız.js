const pdfCanvas = document.getElementById("pdf-canvas");
const ctx = pdfCanvas.getContext("2d");

let pdfDoc = null;
let currentPage = 1;
let scale = 1.5;

// Yüklenen PDF'i Görüntüle
document.getElementById("pdf-upload").addEventListener("change", (e) => {
    const file = e.target.files[0];
    if (file && file.type === "application/pdf") {
        const reader = new FileReader();
        reader.onload = function () {
            const typedarray = new Uint8Array(reader.result);

            pdfjsLib.getDocument(typedarray).promise.then((pdf) => {
                pdfDoc = pdf;
                renderPage(currentPage);
            });
        };
        reader.readAsArrayBuffer(file);
    }
});

function renderPage(num) {
    pdfDoc.getPage(num).then((page) => {
        const viewport = page.getViewport({ scale });
        pdfCanvas.width = viewport.width;
        pdfCanvas.height = viewport.height;

        const renderContext = {
            canvasContext: ctx,
            viewport: viewport,
        };

        page.render(renderContext);
    });
}

// Metin Ekleme
document.getElementById("add-text").addEventListener("click", () => {
    const text = prompt("Eklenecek metni girin:");
    if (text) {
        ctx.font = "16px Arial";
        ctx.fillStyle = "red";
        ctx.fillText(text, 50, 50); // Metni belirli bir koordinata yerleştirir
    }
});

// Şekil Çizme
document.getElementById("draw-shape").addEventListener("click", () => {
    ctx.strokeStyle = "blue";
    ctx.lineWidth = 2;
    ctx.strokeRect(100, 100, 150, 100); // Dikdörtgen çizme
});

// PDF'yi Kaydetme
document.getElementById("save-pdf").addEventListener("click", () => {
    const { jsPDF } = window.jspdf;
    const pdf = new jsPDF();

    // Canvas'ı PDF'e çevir
    const imgData = pdfCanvas.toDataURL("image/png");
    pdf.addImage(imgData, "PNG", 0, 0, 210, 297); // A4 ölçülerinde PDF'e ekler

    // Kaydet
    pdf.save("edited.pdf");
});