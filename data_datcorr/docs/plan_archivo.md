
from pathlib import Path
import pypandoc

text = r"""# Plan de Implementación del Módulo de Reportes – DATCORR

## Objetivo

Construir un módulo de reportes escalable, reutilizable y orientado a PostgreSQL, evitando desarrollar un reporte independiente para cada necesidad.

## Principios

- Un único motor de reportes.
- Separación entre consulta, presentación y exportación.
- Reutilización de filtros.
- Arquitectura preparada para crecer.

# Fase 1 – Estructura

Crear un módulo **Reportes** con cuatro categorías iniciales:

- Consultas
- Inventario
- Movimientos
- Usuarios

## Fase 2 – Pantalla única

Cada reporte utilizará la misma interfaz:

1. Filtros
2. Vista previa
3. Exportación (PDF, Excel, CSV e impresión)

## Fase 3 – Flujo único

Usuario → Selección de reporte → Filtros → Generar → Vista previa → Exportar

## Fase 4 – Motor de reportes



ReportService

↓

Repository

↓

Consulta SQL

↓

DataFrame

↓

Render

↓

Exportador


Cada nuevo reporte solamente deberá aportar:

- Consulta SQL
- Columnas
- Filtros
- Nombre del reporte

## Reportes prioritarios

### Inventario

- Cantidad de expedientes
- Cantidad de cajas
- Estado
- Organismo
- Localidad

### Movimientos

- Ingresos
- Egresos
- Devoluciones
- Movimientos por fecha
- Movimientos por usuario

### Consultas

- Expedientes consultados
- Usuarios que consultan
- Frecuencia de búsquedas

### Usuarios

- Altas
- Bajas
- Modificaciones
- Roles
- Permisos

### Auditoría

- Operación
- Usuario
- Fecha
- Dirección IP
- Detalle

### Estadísticos

- Crecimiento histórico
- Expedientes por mes
- Ocupación del depósito
- Tendencias

## Arquitectura sugerida



backend/

reportes/

report_service.py

exportadores/

pdf_exporter.py

excel_exporter.py

csv_exporter.py

consultas/

inventario.py

movimientos.py

usuarios.py

auditoria.py

repositories/

report_repository.py


## Método de ejecución

### Etapa 1

Crear la estructura de carpetas y el `ReportService`.

### Etapa 2

Implementar un `ReportRepository` genérico para ejecutar consultas parametrizadas sobre PostgreSQL.

### Etapa 3

Desarrollar los exportadores (CSV, Excel, PDF).

### Etapa 4

Construir la pantalla única de reportes con filtros reutilizables.

### Etapa 5

Implementar los reportes prioritarios uno por uno utilizando el mismo motor.

### Etapa 6

Agregar permisos por tipo de reporte.

### Etapa 7

Incorporar reportes estadísticos y posteriormente programación automática, plantillas y dashboards.

## Beneficios

- Escalabilidad.
- Mantenimiento sencillo.
- Reutilización del código.
- Consistencia visual y funcional.
- Facilidad para incorporar nuevos organismos y nuevos reportes.
  """

out="/mnt/data/Plan_Implementacion_Modulo_Reportes_DATCORR.md"
pypandoc.convert_text(text,"md",format="md",outputfile=out,extra_args=["--standalone"])
print(out)
