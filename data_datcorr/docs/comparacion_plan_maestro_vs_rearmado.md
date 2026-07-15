# Comparación: Plan Maestro vs Plan Rearmado

> Análisis de los documentos `nueva_revision_plan_maestro.md` y `revision_plan_rearmado.md`
> frente al código real del repositorio.

---

## 1. Inconsistencias detectadas

| # | Inconsistencia | `nueva_revision_plan_maestro.md` | `revision_plan_rearmado.md` | Verdad objetiva |
|---|---|---|---|---|
| I1 | **Completitud API REST** | ⚠️ Parcial — "la API no expone todos los endpoints que el escritorio necesita" | ✅ Completa — "ya tiene CRUD completo + reportes" | **Gana rearmado.** `backend/routers/database_router.py` expone list, tables, data, search, columns, create, update (PATCH), delete. La API sí cubre lo necesario. |
| I2 | **Estado repositories/** | ⚠️ Parcial — "no hay repositorio por esquema/organismo" | ❌ Código muerto — "no se importa en ningún lugar del proyecto" | **Gana rearmado.** `repositories/` es código inactivo. No es "parcial", es inexistente en ejecución. |
| I3 | **Migración SQLite** | ✅ ~80% — "Auth tables OK, Fases 1-3 completadas" | ⚠️ Sobreestimado — "7 migrate_*.py, 7 bases_g/*.db, is_sqlite() siguen presentes" | **Gana rearmado.** Las migraciones no se ejecutaron. Los archivos legacy persisten. `is_sqlite()` sigue en `core/database_router.py:37`. |
| I4 | **Prioridad #1** | "Crear endpoints FastAPI" | "Migrar escritorio a API existente" (los endpoints ya existen) | **Gana rearmado.** Invertir en crear endpoints cuando ya existen es desperdicio. |
| I5 | **Doble stack** | No mencionado | Sección completa con tabla comparativa | **Gana rearmado por detection.** El dual-stack (raíz vs backend/) es un hallazgo clave que la revisión previa omitió. |

---

## 2. Fortalezas de cada documento

### `nueva_revision_plan_maestro.md`

| Fortaleza | Detalle |
|---|---|
| F1. Concisión | Una tabla de 13 líneas + 3 brechas + 5 acciones. Lectura rápida. |
| F2. Priorización clara | Acciones numeradas 1-5. Sin ambigüedad de orden. |
| F3. Identifica el problema crítico | "Qt acceso directo a BD" marcado como CRÍTICO. |

### `revision_plan_rearmado.md`

| Fortaleza | Detalle |
|---|---|
| F4. Profundidad de análisis | 9 secciones, 7 vulnerabilidades catalogadas (V1-V7), tabla de doble stack. |
| F5. Correcciones factuales | Detecta que `repositories/` es código muerto (I2), que la API ya es completa (I1), que la migración está sobreestimada (I3). |
| F6. Plan de ejecución granular | 7 fases (A-G) con tareas específicas, criterios de aceptación y dependencias. |
| F7. Riesgos y mitigaciones | R1-R3 con mitigaciones concretas. |
| F8. Definition of Done | 6 criterios medibles de terminación. |

---

## 3. Debilidades de cada documento

### `nueva_revision_plan_maestro.md`

| Debilidad | Impacto |
|---|---|
| D1. Omite el doble stack | La fragmentación raíz vs backend/ es un problema arquitectónico real que no aborda. |
| D2. Sobreestima la API como incompleta | Lleva a proponer crear endpoints que ya existen (desperdicio). |
| D3. No detecta código muerto | `repositories/` aparece como "parcial" cuando en realidad es inservible. |
| D4. Sin plan de ejecución granular | No hay fases, dependencias, riesgos ni criterios de aceptación. |

### `revision_plan_rearmado.md`

| Debilidad | Impacto |
|---|---|
| D5. Extensión | 259 líneas vs 24 de la otra. Puede abrumar y retrasar la acción. |
| D6. Fase G (caché/offline) prematura | Incluirla ahora añde complejidad sin necesidad inmediata. |
| D7. No cuantifica esfuerzo en horas/días | Las estimaciones son relativas ("bajo", "medio"). |
| D8. Asume que el escritorio se puede migrar por completo | No considera un escenario híbrido donde ciertas operaciones pesadas sigan yendo directo a BD. |

---

## 4. Vulnerabilidades (consolidadas)

| ID | Vulnerabilidad | Severidad | Detectado por |
|---|---|---|---|
| V1 | Qt accede a PostgreSQL directo (bypassea API) | **CRÍTICA** | Ambos |
| V2 | Doble stack de lógica de negocio (raíz + backend/) | ALTA | Rearmado |
| V3 | `repositories/` es código muerto que confunde | MEDIA | Rearmado |
| V4 | Migración SQLite no terminada (archivos legacy + `is_sqlite()`) | MEDIA | Rearmado |
| V5 | `ApiClient` del escritorio insuficiente (solo GET/POST) | MEDIA | Rearmado |
| V6 | Auditoría incompleta (escritorio no audita) | BAJA | Rearmado |
| V7 | Sin validación unificada de permisos | MEDIA | Ambos |

---

## 5. Contradicciones resueltas

| Contradicción | Resolución |
|---|---|
| "Crear endpoints" vs "los endpoints ya existen" | **No crear.** Verificar cobertura de los endpoints existentes contra cada operación del escritorio. Solo crear los que falten (si los hay). |
| "Migración al 80%" vs "migración sobreestimada" | **La migración de esquemas/auth está OK. La migración de datos SQLite→PG no se ejecutó. El estado real es ~60%.** |
| "Repositories parcial" vs "repositories muerto" | **Está muerto.** No se importa en ningún módulo. No invertir en completarlo. |

---

## 6. Conclusión concreta

**El diagnóstico de `revision_plan_rearmado.md` es superior en precisión y profundidad.** Sus correcciones (I1-I5) están verificadas contra el código real.

La `nueva_revision_plan_maestro.md` sirve como resumen ejecutivo, pero contiene errores fácticos que, de seguirse, llevarían a invertir en trabajo innecesario (crear endpoints que ya existen, completar repositorios muertos).

**Recomendación:** Adoptar `revision_plan_rearmado.md` como plan director, con los ajustes indicados en la sección 7.

---

## 7. Plan de ejecución consolidado

### Fase A — Preparar el cliente API del escritorio
**Test de avance:** `test_api_client.py` pasa 8/8 métodos (get, post, put, patch, delete, listar_bases, crear_registro, refresco automático de token).

| Paso | Tarea |
|---|---|
| A.1 | Extender `core/api_client.py`: añadir `put()`, `patch()`, `delete()`, refresh automático en 401 |
| A.2 | Crear `core/api_database_client.py`: wrapper que mapea 1:1 con endpoints de `database_router.py` |
| A.3 | Crear `core/api_reportes_client.py`: wrapper para `reportes_router.py` |
| A.4 | Escribir `test_api_client.py` que ejerza todos los métodos |

### Fase B — Migrar el escritorio a consumir la API
**Test de avance:** `grep "db.router\|db.service\|db_registry" ventana_principal.py` retorna 0 coincidencias para operaciones de datos. Todas las operaciones CRUD del escritorio quedan registradas en `auditoria`.

| Paso | Tarea |
|---|---|
| B.1 | Reemplazar `TreeLoader(self.router)` por `api_database_client.listar_bases()` y `tablas()` |
| B.2 | Reemplazar búsquedas (`self.router.search`, `fetch_all`) por API |
| B.3 | Reemplazar altas (`insert`) por `api_database_client.crear()` |
| B.4 | Reemplazar ediciones (`update_by_id`) por `api_database_client.actualizar()` (PATCH) |
| B.5 | Reemplazar bajas (`delete_by_id`) por `api_database_client.eliminar()` (DELETE) |
| B.6 | Verificar que cada operación queda auditada en `auditoria` |
| B.7 | Test E2E: ejecutar 1 ciclo completo (login → cargar → buscar → editar → eliminar) vía API |

### Fase C — Unificar validación y permisos
**Test de avance:** El escritorio obtiene permisos y nivel desde `GET /auth/me` y no desde `core/access_control.py`.

| Paso | Tarea |
|---|---|
| C.1 | Verificar que `database_router.py` aplica permisos en create/update/delete |
| C.2 | Exponer endpoint `GET /auth/me` si no existe, con niveles/permisos del usuario |
| C.3 | Reemplazar llamadas a `core/access_control.py` en el escritorio por datos del endpoint |

### Fase D — Eliminar el doble stack y código muerto
**Test de avance:** `python -c "import db.router"` falla (el módulo fue retirado). `repositories/` ya no existe o fue reconvertido.

| Paso | Tarea |
|---|---|
| D.1 | Eliminar `repositories/` (código muerto, no se importa en ningún lado) |
| D.2 | Retirar `db/router.py`, `db/service.py`, `db/registry.py`, `core/data_service.py` |
| D.3 | Unificar `database/conexion.py` (raíz) y `backend/database/conexion.py` |
| D.4 | Eliminar `model/datcorr_dao_postgres.py` y `model/legacy/` |

### Fase E — Cerrar migración SQLite
**Test de avance:** `SELECT COUNT(*) FROM "escribania"."Datcorr_database"` en PG coincide con `SELECT COUNT(*) FROM Datcorr_database` en SQLite. `bases_g/` ya no existe.

| Paso | Tarea |
|---|---|
| E.1 | Ejecutar `migrate_escribania.py`, `migrate_ips.py`, `migrate_pediatrico.py`, `migrate_maternidad.py`, `migrate_igpj.py`, `migrate_igpj_listado_nuevo.py`, `migrate_igpj_txt_listado.py` |
| E.2 | Verificar conteo de filas por schema: PG vs SQLite |
| E.3 | Mover `migrate_*.py`, `migration/`, `bases_g/` a `archive/` |
| E.4 | Eliminar `is_sqlite()` de `core/database_router.py` |
| E.5 | Remover `core/database_router.py` si ya no tiene propósito |

### Fase F — Reportes en el escritorio (opcional)
**Test de avance:** El escritorio puede listar y ejecutar reportes vía API, mismos datos que `ReportesPage.jsx`.

| Paso | Tarea |
|---|---|
| F.1 | Consumir `reportes_router.py` desde el escritorio vía `api_reportes_client` |
| F.2 | Mostrar resultados en vista similar a React (DataGrid o QTableWidget) |

---

## 8. Priorización final

```
Fase A ──→ Fase B ──→ Fase C ──→ Fase D
   │                      ↑
   │                      │
   └── Fase E (paralela) ─┘
   
   Fase F (opcional, después de B)
```

| Orden | Fase | Prioridad | Esfuerzo | Test de avance |
|---|---|---|---|---|
| 1 | **A** | Alta | Bajo | `test_api_client.py` pasa 8/8 métodos |
| 2 | **E** | Media | Bajo | Conteo PG == conteo SQLite por schema |
| 3 | **B** | **Crítica** | Medio | `grep` de acceso directo a BD = 0 |
| 4 | **C** | Alta | Bajo | Escritorio obtiene permisos vía `GET /auth/me` |
| 5 | **D** | Media | Medio | `import db.router` falla |
| 6 | **F** | Baja | Bajo | Escritorio ejecuta reporte vía API |
