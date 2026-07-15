# Plan definitivo de reportes - DatCorr ERP

**Version:** 4.1  
**Estado:** propuesta de implementacion con compuertas de calidad  
**Regla principal:** ningun checklist puede marcarse ni puede iniciarse el siguiente hasta que las pruebas del anterior finalicen correctamente, sin regresiones.

## 1. Objetivo y limites

Implementar el modulo `/reportes` de forma incremental, segura y verificable. Debe ofrecer:

- resumen de actividad y datos documentales;
- actividad, evolucion diaria, tipos de operacion y bases;
- alertas administrativas y usuarios inactivos;
- exportacion CSV auditada;
- aislamiento estricto de datos por rol.

No forman parte de esta entrega: PDF, envios programados, dashboards personalizados, drill-down e indicadores interanuales.

## 2. Fortalezas que se conservan

| Aporte de v2.4/v3.0 | Decision definitiva |
|---|---|
| Router, servicio y frontend separados | Mantener la separacion router -> service -> repositorio/SQL y cliente -> pagina/componentes. |
| `Depends(obtener_usuario_actual)` | Autenticacion obligatoria en todos los endpoints. Nunca confiar en el ocultamiento de UI. |
| Validacion de fechas, pagina y limite | Un helper unico valida todos los filtros antes de consultar. |
| Lista blanca de schemas y tipos exportables | Identificadores SQL solo desde constantes internas; parametros de usuario siempre enlazados. |
| Indices sobre auditoria | Aplicarlos solo mediante migracion revisada, despues de medir plan de ejecucion y volumen. |
| `LEFT JOIN` para inactividad | Usar agregacion con `LEFT JOIN`, evitando subconsultas correlacionadas. |
| CSV con `StreamingResponse` y auditoria | Mantenerlo, agregando proteccion contra formula injection y limites de exportacion. |
| Fechas locales en frontend | Enviar `YYYY-MM-DD` local; parsear sin ambiguedad y usar intervalo semiabierto. |
| Alertas configurables y logging | Umbrales validados, acciones verificadas contra la base real y logs estructurados. |

## 3. Riesgos eliminados antes de codificar

| Riesgo detectado | Impacto | Correccion obligatoria |
|---|---|---|
| KPIs globales para usuarios no administradores | Filtracion de volumen de datos y usuarios | Los no administradores reciben solo sus metricas; los KPIs globales requieren permiso explicito `reportes.ver_global`. |
| `BETWEEN` con fechas `YYYY-MM-DD` | Omite eventos del ultimo dia despues de medianoche | Convertir a `[desde 00:00, hasta + 1 dia 00:00)` y consultar `fecha >= :desde AND fecha < :hasta_exclusiva`. |
| `datetime.utcnow()` sin zona | Resultados y alertas incorrectos por zona horaria | Definir zona de negocio/configuracion, usar `datetime` aware y normalizar la columna y parametros a UTC. |
| `lru_cache` sin TTL ni invalidacion distribuida | Datos obsoletos, permisos revocados aun visibles y comportamiento distinto por worker | No usar cache en MVP. Si las mediciones lo exigen, incorporar cache con TTL (Redis), clave por version de permisos y usuario, y prueba de invalidacion. |
| Retornar cero si falta un schema | Oculta un error de despliegue y falsea reportes | Validar los siete schemas en preflight. Si uno falla, responder estado parcial explicito y registrar error; nunca confundirlo con cero registros. |
| Indice generico sobre una columna no confirmada | Migracion fallida o costo de escritura/almacenamiento | Inspeccionar esquema y ejecutar `EXPLAIN (ANALYZE, BUFFERS)`; crear solo indices justificados y con plan de rollback. |
| Acciones `DELETE_LOGICO`/`LOGIN_FAILED` asumidas | Alertas inutiles o ausentes | Inventariar `SELECT DISTINCT accion` en un entorno seguro y versionar el mapa de acciones aceptadas. |
| Un unico `OR` para rol en SQL | Posible plan ineficiente y riesgo de reutilizar consulta sin alcance | Construir dos consultas o agregar el predicado de usuario solo para no administradores. |
| CSV sin saneamiento | Inyeccion de formulas al abrirlo en Excel/LibreOffice | Prefijar valores que comiencen con `=`, `+`, `-` o `@` con apostrofo; usar UTF-8 BOM, `text/csv; charset=utf-8` y nombre de archivo fijo. |
| Exportacion sin limite de filas | Consumo excesivo de memoria/BD | Limite explicito, paginacion o streaming por lotes; rechazar solicitudes que excedan el maximo definido. |
| Permiso de Sidebar acoplado a `canViewUsers` | Usuarios correctos bloqueados o privilegios indebidos | Crear/usar permiso semantico `reportes.ver`; el backend es la fuente de verdad. |
| `except Exception` convertido siempre en 500 | Un timeout o una indisponibilidad se diagnostican mal | Repropagar `HTTPException`; registrar excepcion con contexto sin PII y mapear timeout/BD a `503`. |

## 4. Contrato funcional y de seguridad

### 4.1 Roles

Definir en un unico modulo la politica, probada como matriz:

| Capacidad | `reportes.ver` | `reportes.ver_global` / superusuario o nivel >= 10 |
|---|---:|---:|
| Entrar a `/reportes` | Si | Si |
| KPIs | Solo propios | Globales |
| Actividad, evolucion y operaciones | Solo `usuario_actual` | Todos |
| Bases documentales | No, salvo que se defina metrica propia sin datos globales | Si |
| Usuarios inactivos y alertas | No (`403`) | Si |
| Exportar | Solo datos que ya puede consultar | Si, dentro de su alcance |

La comprobacion se ejecuta en el backend para cada endpoint y para cada tipo de exportacion. La UI solo refleja esta politica.

### 4.2 Filtros comunes

- `desde` y `hasta`: `YYYY-MM-DD`, obligatorios para actividad/evolucion/tipos/exportaciones temporales.
- Rango maximo: 365 dias.
- `limite`: 1 a 100; `pagina`: minimo 1.
- `dias`: 1 a 365; `ventana_horas`: 1 a 720; umbrales: enteros positivos con maximo acordado.
- Las fechas se parsean una sola vez con Pydantic/FastAPI. Si `desde > hasta`, responder `400`.
- Todas las listas paginadas devuelven `{items, pagina, limite, total}`. El total se calcula bajo el mismo alcance de permisos.

### 4.3 Endpoints MVP

| Endpoint | Acceso | Resultado |
|---|---|---|
| `GET /reportes/kpis` | propio/global segun politica | KPIs coherentes con el alcance del usuario. |
| `GET /reportes/actividad-usuarios` | propio/global | lista paginada de operaciones por usuario. |
| `GET /reportes/evolucion-diaria` | propio/global | serie diaria, incluyendo dias sin actividad si UI lo requiere. |
| `GET /reportes/tipos-operacion` | propio/global | distribucion por accion. |
| `GET /reportes/actividad-bases` | global | conteos por schema y estado por fuente. |
| `GET /reportes/usuarios-inactivos` | global | usuarios activos sin auditoria en `dias`. |
| `GET /reportes/alertas` | global | alertas con regla, severidad, valor y ventana. |
| `GET /reportes/exportar` | mismo alcance que el reporte | CSV del tipo permitido y evento `REPORTE_EXPORT` auditado. |

Usar modelos Pydantic de respuesta para impedir contratos inconsistentes. `SCHEMAS` y `TIPOS_EXPORTABLES` son constantes privadas; no aceptar schema libre por query string.

## 5. Diseno tecnico

### Backend

Archivos previstos:

- `backend/services/reportes_service.py`: politica de alcance, validaciones compartidas, consultas y transformacion de resultados.
- `backend/routers/reportes_router.py`: parametros tipados, autorizacion, modelos de respuesta y mapeo de errores.
- `backend/main.py`: registro del router.
- Migracion SQL versionada: indices aprobados y, si existe, permiso `reportes.ver` / `reportes.ver_global`.

Las consultas usan SQL parametrizado. Los nombres de schema solo se interpolan desde la tupla constante `SCHEMAS`. No se pasan sesiones de BD ni objetos de usuario a caches.

Para errores: conservar `401`, `403` y validaciones `400/422`; registrar los inesperados con `logger.exception`; devolver `503` para fallo de BD/timeout y `500` para error interno. No devolver SQL, trazas ni detalles sensibles.

### Rendimiento y consistencia

1. Medir primero la cardinalidad y consultas reales.
2. Crear solamente indices aprobados, preferentemente mediante migracion. Para tablas grandes, planificar indice concurrente fuera de una transaccion si PostgreSQL/operacion lo permite.
3. Usar el intervalo semiabierto para preservar el uso del indice de `fecha`.
4. El conteo de cada base se ejecuta de manera controlada. La respuesta informa `estado: ok|error`; no sustituye fallas por cero.
5. Establecer timeout de consulta y limite de exportacion. Cualquier cache futura debe tener TTL, metricas, invalidacion y clave de alcance.

### Frontend

- `frontend/src/services/reportesService.js`: un cliente por endpoint y descarga como `blob`.
- `frontend/src/pages/ReportesPage.jsx`: estado de filtros, carga, vacio, error y permisos.
- `frontend/src/components/ReportesTabs.jsx`: resumen, actividad, operaciones, bases y alertas; componentes sin logica de autorizacion.
- `frontend/src/router/AppRouter.jsx` y `frontend/src/layouts/Sidebar.jsx`: ruta e item condicionados por `reportes.ver`.

El selector usa `value={fecha.toLocaleDateString("en-CA")}` y construye fechas con `new Date(valor + "T12:00:00")`. No usar `toISOString()` para serializar fechas locales.

## 6. Alertas y exportacion

Antes de activar reglas, documentar en codigo y pruebas las acciones auditadas reales. Las reglas iniciales son:

- borrados masivos: acciones verificadas, umbral y ventana configurables;
- logins fallidos: solo si la accion existe en auditoria;
- usuarios inactivos: endpoint separado, sin duplicar alerta.

Cada alerta incluye `regla`, `severidad`, `usuario` cuando aplique, `valor`, `ventana_horas` y `detalle`. Los logs usan campos estructurados, sin volcar detalles sensibles.

El exportador reutiliza exactamente la funcion de servicio y el alcance del endpoint de lectura. Antes de transmitir el archivo registra una auditoria transaccional `REPORTE_EXPORT` con usuario, tipo, filtros validados y resultado. Si la auditoria falla, no se entrega la exportacion. Las celdas se sanitizan contra formulas y los datos vacios generan un CSV valido con cabecera conocida.

## 7. Checklist secuencial con compuertas obligatorias

**Procedimiento para cada etapa:** ejecutar sus pruebas, guardar evidencia (comando, resultado y fecha) en el PR o ticket, corregir todo fallo y repetir. Solo entonces marcarla y comenzar la siguiente. Si una comprobacion posterior revela una regresion, volver a la etapa afectada y bloquear las siguientes.

### Etapa 0 - Descubrimiento y linea base

- [ ] Confirmar estructura real de `usuarios`, `auditoria`, permisos, los siete schemas y `Datcorr_database` en entorno no productivo.
- [ ] Inventariar valores reales de `public.auditoria.accion` y zonas horarias/tipo de `fecha`.
- [ ] Confirmar el mecanismo existente de autenticacion, rol y permiso; no asumir nombres de campos.
- [ ] Ejecutar pruebas actuales de backend y frontend y registrar que pasan antes de modificar codigo.
- [ ] Medir `EXPLAIN (ANALYZE, BUFFERS)` de las consultas candidatas con datos representativos.

**Compuerta:** estructuras, acciones y permisos documentados; linea base verde; no hay SQL ni frontend nuevo antes de aprobarla.

### Etapa 1 - Contrato, autorizacion y migraciones

- [ ] Definir modelos Pydantic de filtros y respuestas, matriz de permisos y semantica propio/global.
- [ ] Implementar helper unico de fechas, intervalo semiabierto y validaciones de limites.
- [ ] Crear migracion reversible para permisos e indices estrictamente necesarios; no usar el placeholder `"schema"`.
- [ ] Probar migracion en copia/entorno de prueba y repetir `EXPLAIN` para verificar mejora sin regresion relevante de escritura.
- [ ] Pruebas unitarias: formato invalido, fechas invertidas, 366 dias, limites/pagina/dias/umbrales invalidos.

**Compuerta:** pruebas unitarias verdes y migracion validada con rollback ensayado. Si el indice no mejora la consulta, no se incorpora.

### Etapa 2 - Servicio de consultas seguro

- [ ] Implementar constantes internas de schemas/tipos y consultas parametrizadas.
- [ ] Implementar el alcance separado de administrador y usuario comun para evitar datos globales.
- [ ] Implementar KPIs, actividad, evolucion, tipos y bases con respuestas tipadas y estados parciales explicitos.
- [ ] Implementar limites de timeout y manejo `400/401/403/503/500` sin filtracion de detalles.
- [ ] Pruebas unitarias de servicio con BD de prueba: datos propios, ajenos, sin datos, schema fallido y timeout simulado.

**Compuerta:** cobertura de todas las ramas de alcance y errores esperados; todas las pruebas verdes; comparacion manual de resultados contra SQL de referencia.

### Etapa 3 - Router y pruebas de integracion API

- [ ] Exponer los cinco endpoints de lectura y registrar router en la aplicacion.
- [ ] Añadir usuarios inactivos y alertas tras validar acciones reales.
- [ ] Verificar modelos de respuesta, paginacion y `total` para cada endpoint.
- [ ] Pruebas de integracion autenticadas para `401`, `403`, usuario comun, administrador y superusuario.
- [ ] Pruebas de no regresion de rutas existentes y arranque de aplicacion.

**Compuerta:** suite API verde; un usuario comun no puede obtener, inferir ni exportar datos de otro usuario; administrador obtiene solo lo autorizado.

### Etapa 4 - Exportacion segura y auditable

- [ ] Implementar CSV por lotes/streaming con limite validado y encabezados estables.
- [ ] Sanitizar celdas que empiezan por `=`, `+`, `-` o `@`; definir codificacion UTF-8 BOM.
- [ ] Reutilizar filtros, servicio y politica de autorizacion; prohibir tipos fuera de lista.
- [ ] Registrar `REPORTE_EXPORT` de manera transaccional antes de enviar el archivo.
- [ ] Pruebas: CSV vacio, tildes, caracteres de formula, tipo invalido, intento no autorizado y fallo de auditoria.

**Compuerta:** descarga correcta y auditable; no existe via de exportacion que evada permisos ni entregue CSV inseguro.

### Etapa 5 - Frontend y experiencia de usuario

- [ ] Instalar `recharts` con lockfile revisado y sin actualizar dependencias no relacionadas.
- [ ] Implementar servicio, tabs, filtros locales correctos, estados de carga/vacio/error y descarga de blob.
- [ ] Mostrar u ocultar tabs segun `reportes.ver`/`reportes.ver_global`, sin sustituir la autorizacion backend.
- [ ] Verificar manualmente en zona horaria local que el ultimo dia del rango aparece completo.
- [ ] Pruebas de componentes: carga correcta, error, lista vacia, rango invalido y controles restringidos.

**Compuerta:** build/lint/tests de frontend verdes; navegacion existente intacta; la UI representa fielmente las respuestas y permisos de API.

### Etapa 6 - Aceptacion integral, rendimiento y despliegue

- [ ] Ejecutar suite completa backend + frontend + integracion desde una copia de datos representativa.
- [ ] Probar matriz de roles completa y cada exportacion permitida/prohibida.
- [ ] Medir latencia, consultas, timeout y consumo de exportacion bajo carga acordada; comparar con linea base.
- [ ] Revisar logs/auditoria: no contienen secretos ni PII innecesaria; cada exportacion queda trazada.
- [ ] Preparar plan de despliegue gradual, monitoreo y rollback de migracion/feature flag.

**Compuerta final:** evidencia de todas las etapas adjunta, cero fallos criticos o altos abiertos, rollback probado y aprobacion funcional. Recién entonces habilitar `/reportes` en produccion.

## 8. Criterios de aceptacion finales

1. Todos los endpoints requieren autenticacion y aplican el alcance de servidor.
2. Los filtros invalidos devuelven errores controlados y ninguna fecha pierde datos del dia final.
3. Usuarios no privilegiados no acceden ni infieren metricas globales, alertas, inactivos o exportaciones ajenas.
4. Consultas y exportaciones son acotadas, observables y no degradan las funciones existentes.
5. Los schemas fallidos se señalan como tales; nunca se reportan como conteo cero.
6. CSV es legible, seguro frente a formulas y deja auditoria consistente.
7. Build, lint, unitarias, integracion, pruebas de rol y pruebas manuales de aceptacion estan en verde antes de cada avance y antes del despliegue.
