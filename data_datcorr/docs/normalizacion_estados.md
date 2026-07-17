# Normalización de Estados

## Propósito

Unificar el campo `estado` de todas las tablas `Datcorr_database` (una por organismo/schema) a solo 2 valores canónicos: `VERIFICADO` y `DATCORR`, eliminando inconsistencias tipográficas y valores que no representan estados reales.

## Estados canónicos finales

| Estado | Significado |
|---|---|
| `DATCORR` | Pendiente / en gestión (o no especificado) |
| `VERIFICADO` | Completado / retirado |

## Mapa de transformación

### VALOR ORIGINAL → DESTINO

#### → VERIFICADO

- `VERIFICADO` (y ~15 variantes con typos: BERIFICADO, CERIFICADO, VARIFICADO, VEERIFICADO, VERFICADO, etc.)
- `RETIRADO O VERIFICADO` (y variantes: RATIRADO O VERIFICADO, RETIRADO O VERFICADO, etc.)
- `RETIRADO`
- `VERIFICAR RETIRO`

#### → DATCORR

- `DATCORR` (y variantes: DATCOR, DATOCRR, DARCORR, etc.)
- `ARCHIVADO`, `ARCHIVO`, `ARCHVIO`, `CAPITAL`
- `-` (guión)
- `NULL` / vacío
- `SOLO CONSULTA` (previamente movido a `observaciones`)
- Códigos de ubicación física en pediatrico (previamente movidos a `observaciones`)
- Basura: `PUTA`, `NO ESTABA`, `INEXISTENTE`, etc.

## Proceso de normalización

### En desarrollo/pruebas locales

```bash
psql -U postgres -d datcorr -f scripts/normalizar_estados.sql
```

### En producción (después de cada importación de datos originales)

1. Copiar los archivos originales a la base de datos `datcorr`
2. Ejecutar el script de normalización:

```bash
psql -U <usuario> -d datcorr -f scripts/normalizar_estados.sql
```

3. Verificar que no queden valores anómalos con las consultas de verificación al final del script
4. El resultado debe mostrar solo `VERIFICADO` y `DATCORR` en todos los organismos

## Verificación manual

```sql
-- Verificar valores no canónicos (debe dar 0 filas)
SELECT schemaname, estado, COUNT(*)
FROM (
    SELECT 'ips' AS schemaname, estado FROM ips."Datcorr_database"
    UNION ALL SELECT 'pediatrico', estado FROM pediatrico."Datcorr_database"
    UNION ALL SELECT 'igpj', estado FROM igpj."Datcorr_database"
    UNION ALL SELECT 'igpj_listado_nuevo', estado FROM igpj_listado_nuevo."Datcorr_database"
    UNION ALL SELECT 'igpj_txt_listado', estado FROM igpj_txt_listado."Datcorr_database"
    UNION ALL SELECT 'maternidad', estado FROM maternidad."Datcorr_database"
    UNION ALL SELECT 'escribania', estado FROM escribania."Datcorr_database"
) todos
WHERE estado NOT IN ('VERIFICADO', 'DATCORR')
GROUP BY schemaname, estado
ORDER BY schemaname;

-- Resumen por organismo
SELECT schemaname, COUNT(*) AS total,
       SUM(CASE WHEN estado='DATCORR' THEN 1 ELSE 0 END) AS datcorr,
       SUM(CASE WHEN estado='VERIFICADO' THEN 1 ELSE 0 END) AS verificado
FROM (...misma subconsulta...) todos
GROUP BY schemaname ORDER BY schemaname;
```

## Impacto en el código

El backend y frontend trabajan con estos 2 estados únicamente:

- **Dashboard**: `GET /dashboard/stats` ahora devuelve desglose `datcorr` y `verificado` por base
- **Reporte Inventario**: incluye columnas `datcorr` y `verificado` por organismo
- **KPIs**: total por estado
- **Frontend Dashboard**: tarjetas y tabla con colores distintivos (azul=DATCORR, verde=VERIFICADO)
