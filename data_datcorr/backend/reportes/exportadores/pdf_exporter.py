import logging
import io

from fastapi.responses import StreamingResponse

logger = logging.getLogger("datcorr")


class PDFExporter:

    FORMATO = "pdf"

    def exportar(self, datos: list[dict], nombre_archivo: str) -> StreamingResponse:
        try:
            from reportlab.lib.pagesizes import A4, landscape
            from reportlab.lib import colors
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.units import mm

            buffer = io.BytesIO()
            page_size = landscape(A4)
            doc = SimpleDocTemplate(
                buffer, pagesize=page_size,
                leftMargin=10*mm, rightMargin=10*mm,
                topMargin=10*mm, bottomMargin=10*mm,
            )

            styles = getSampleStyleSheet()
            elements = []

            elements.append(Paragraph(f"Reporte: {nombre_archivo}", styles["Title"]))
            elements.append(Spacer(1, 5*mm))

            if datos:
                headers = list(datos[0].keys())
                data = [headers]
                for row in datos:
                    data.append([str(row.get(h, "")) for h in headers])

                col_width = (page_size[0] - 20*mm) / max(len(headers), 1)
                table = Table(data, colWidths=col_width)
                table.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#3F51B5")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTSIZE", (0, 0), (-1, 0), 8),
                    ("FONTSIZE", (0, 1), (-1, -1), 7),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F5F5F5")]),
                ]))
                elements.append(table)

            doc.build(elements)
            buffer.seek(0)

            return StreamingResponse(
                buffer,
                media_type="application/pdf",
                headers={
                    "Content-Disposition": f'attachment; filename="{nombre_archivo}.pdf"',
                    "Cache-Control": "private",
                },
            )
        except Exception as e:
            logger.error(f"Error generando PDF: {e}", exc_info=True)
            raise
