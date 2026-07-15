import csv
import io
import logging

from fastapi.responses import StreamingResponse

logger = logging.getLogger("datcorr")


class CSVExporter:

    FORMATO = "csv"

    def exportar(self, datos: list[dict], nombre_archivo: str) -> StreamingResponse:
        try:
            output = io.StringIO()
            if datos:
                writer = csv.DictWriter(output, fieldnames=list(datos[0].keys()))
                writer.writeheader()
                writer.writerows(datos)
            output.seek(0)
            content = output.getvalue()
            return StreamingResponse(
                iter([content]),
                media_type="text/csv",
                headers={
                    "Content-Disposition": f'attachment; filename="{nombre_archivo}.csv"',
                    "Cache-Control": "private",
                },
            )
        except Exception as e:
            logger.error(f"Error generando CSV: {e}", exc_info=True)
            raise
