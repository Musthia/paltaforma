# INVENTARIO OFICIAL N°5

# MAPA DE MIGRACIÓN DESKTOP → WEB

Versión 1.0

Fecha: Mayo 2026

---

# ESTADO ACTUAL

## Desktop

Actualmente es el sistema operativo principal.

Contiene:

* Login
* Selección de organismos
* Consultas
* Altas
* Ediciones
* Eliminaciones
* Gestión de usuarios
* Plantillas específicas
* Navegación completa

---

## Backend

Actualmente contiene:

* FastAPI
* JWT
* Refresh Tokens
* Blacklist
* Middleware Global
* Auditoría
* Usuarios
* Permisos

---

## PostgreSQL

Actualmente contiene:

* usuarios
* permisos
* usuarios_permisos
* refresh_tokens
* token_blacklist
* auditoria

---

## SQLite

Actualmente contiene:

* IGPJ
* IPS
* PEDIATRICO
* MATERNIDAD
* ESCRIBANIA
* IGPJ_LISTADO_NUEVO

---

# OBJETIVO REAL

NO queremos:

❌ Reescribir DatCorr

Queremos:

✔ Conservar Desktop

✔ Crear versión Web

✔ Compartir Backend

✔ Compartir PostgreSQL

✔ Compartir reglas de negocio

---

# ARQUITECTURA FUTURA

<pre class="overflow-visible! px-0!" data-start="1267" data-end="1579"><div class="relative w-full mt-4 mb-1"><div class=""><div class="relative"><div class="h-full min-h-0 min-w-0"><div class="h-full min-h-0 min-w-0"><div class="border border-token-border-light border-radius-3xl corner-superellipse/1.1 rounded-3xl"><div class="h-full w-full border-radius-3xl bg-token-bg-elevated-secondary corner-superellipse/1.1 overflow-clip rounded-3xl lxnfua_clipPathFallback"><div class="pointer-events-none absolute end-1.5 top-1 z-2 md:end-2 md:top-1"></div><div class="relative"><div class="pe-11 pt-3"><div class="relative z-0 flex max-w-full"><div id="code-block-viewer" dir="ltr" class="q9tKkq_viewer cm-editor z-10 light:cm-light dark:cm-light flex h-full w-full flex-col items-stretch ͼs ͼ16"><div class="cm-scroller"><pre class="cm-content q9tKkq_readonly m-0"><code><span>               PostgreSQL</span><br/><span>                    ▲</span><br/><span>                    │</span><br/><span>                    │</span><br/><span>             FastAPI Backend</span><br/><span>                    ▲</span><br/><span>          ┌─────────┴─────────┐</span><br/><span>          │                   │</span><br/><span>          │                   │</span><br/><span>      Desktop             Web</span><br/><span>     (PySide6)          (React)</span></code></pre></div></div></div></div></div></div></div></div></div><div class=""><div class=""></div></div></div></div></div></pre>

---

# ORDEN DE MIGRACIÓN

No migraremos todo.

Migramos por impacto.

---

# FASE WEB 1

## Dashboard

Primera pantalla web.

Contendrá:

* usuario conectado
* rol
* permisos
* accesos rápidos

---

### Objetivo

Validar:

* JWT
* Refresh
* permisos

---

Es la migración más simple.

---

# FASE WEB 2

## Consulta Global

La operación más usada del sistema.

---

Pantalla:

<pre class="overflow-visible! px-0!" data-start="1959" data-end="2008"><div class="relative w-full mt-4 mb-1"><div class=""><div class="relative"><div class="h-full min-h-0 min-w-0"><div class="h-full min-h-0 min-w-0"><div class="border border-token-border-light border-radius-3xl corner-superellipse/1.1 rounded-3xl"><div class="h-full w-full border-radius-3xl bg-token-bg-elevated-secondary corner-superellipse/1.1 overflow-clip rounded-3xl lxnfua_clipPathFallback"><div class="pointer-events-none absolute end-1.5 top-1 z-2 md:end-2 md:top-1"></div><div class="relative"><div class="pe-11 pt-3"><div class="relative z-0 flex max-w-full"><div id="code-block-viewer" dir="ltr" class="q9tKkq_viewer cm-editor z-10 light:cm-light dark:cm-light flex h-full w-full flex-col items-stretch ͼs ͼ16"><div class="cm-scroller"><pre class="cm-content q9tKkq_readonly m-0"><code><span>[ Organismo ]</span><br/><br/><span>[ Buscar ]</span><br/><br/><span>Resultados</span></code></pre></div></div></div></div></div></div></div></div></div><div class=""><div class=""></div></div></div></div></div></pre>

---

Permitirá:

* IGPJ
* IPS
* MATERNIDAD
* PEDIATRICO
* ESCRIBANIA

---

### Motivo

La consulta representa aproximadamente el 70-80% del uso real.

---

# FASE WEB 3

## Edición rápida

Operación más frecuente:

Actualizar estado.

Ejemplo:

<pre class="overflow-visible! px-0!" data-start="2255" data-end="2302"><div class="relative w-full mt-4 mb-1"><div class=""><div class="relative"><div class="h-full min-h-0 min-w-0"><div class="h-full min-h-0 min-w-0"><div class="border border-token-border-light border-radius-3xl corner-superellipse/1.1 rounded-3xl"><div class="h-full w-full border-radius-3xl bg-token-bg-elevated-secondary corner-superellipse/1.1 overflow-clip rounded-3xl lxnfua_clipPathFallback"><div class="pointer-events-none absolute end-1.5 top-1 z-2 md:end-2 md:top-1"></div><div class="relative"><div class="pe-11 pt-3"><div class="relative z-0 flex max-w-full"><div id="code-block-viewer" dir="ltr" class="q9tKkq_viewer cm-editor z-10 light:cm-light dark:cm-light flex h-full w-full flex-col items-stretch ͼs ͼ16"><div class="cm-scroller"><pre class="cm-content q9tKkq_readonly m-0"><code><span>ACTIVO</span><br/><span>ARCHIVADO</span><br/><span>PRESTADO</span><br/><span>ENTREGADO</span></code></pre></div></div></div></div></div></div></div></div></div><div class=""><div class=""></div></div></div></div></div></pre>

---

Esto genera valor inmediato.

---

# FASE WEB 4

## Altas

Migrar:

* Plantilla IGPJ
* Plantilla IPS
* Plantilla MATERNIDAD
* Plantilla PEDIATRICO
* Plantilla ESCRIBANIA

---

Aquí reutilizamos:

* validaciones
* permisos
* auditoría

---

# FASE WEB 5

## Administración de usuarios

Actualmente:

ventana_usuarios.py

---

Migración:

* listado
* alta
* edición
* activación
* permisos

---

# FASE WEB 6

## Reportes

Todavía no existen.

Por eso:

NO se migran.

Se diseñan directamente para Web.

---

# FASE WEB 7

## Estadísticas

Tampoco existen.

Por eso:

Se crean nativamente para Web.

Ejemplos:

* expedientes por organismo
* ingresos por mes
* egresos por mes
* registros por localidad
* registros por estado

---

# QUÉ SEGUIRÁ EN DESKTOP

Durante mucho tiempo.

---

## Carga masiva

Importaciones futuras:

Excel

CSV

TXT

---

## Herramientas administrativas

Mantenimiento

Migraciones

Correcciones

Scripts

---

## Operaciones offline

Desktop seguirá siendo útil cuando no haya conexión.

---

# QUÉ DEBE PASAR A POSTGRESQL

Prioridad máxima.

Actualmente las bases operativas están en SQLite.

---

Objetivo futuro:

<pre class="overflow-visible! px-0!" data-start="3449" data-end="3502"><div class="relative w-full mt-4 mb-1"><div class=""><div class="relative"><div class="h-full min-h-0 min-w-0"><div class="h-full min-h-0 min-w-0"><div class="border border-token-border-light border-radius-3xl corner-superellipse/1.1 rounded-3xl"><div class="h-full w-full border-radius-3xl bg-token-bg-elevated-secondary corner-superellipse/1.1 overflow-clip rounded-3xl lxnfua_clipPathFallback"><div class="pointer-events-none absolute end-1.5 top-1 z-2 md:end-2 md:top-1"></div><div class="relative"><div class="pe-11 pt-3"><div class="relative z-0 flex max-w-full"><div id="code-block-viewer" dir="ltr" class="q9tKkq_viewer cm-editor z-10 light:cm-light dark:cm-light flex h-full w-full flex-col items-stretch ͼs ͼ16"><div class="cm-scroller"><pre class="cm-content q9tKkq_readonly m-0"><code><span>IGPJ</span><br/><span>IPS</span><br/><span>PEDIATRICO</span><br/><span>MATERNIDAD</span><br/><span>ESCRIBANIA</span></code></pre></div></div></div></div></div></div></div></div></div><div class=""><div class=""></div></div></div></div></div></pre>

↓

PostgreSQL

---

Porque:

* Web lo necesita.
* Desktop también podrá usarlo.
* Se elimina duplicación.

---

# ROADMAP REALISTA

## Etapa A (actual)

✔ Backend seguridad

✔ Usuarios

✔ JWT

✔ Auditoría

---

## Etapa B

Migrar organismos a PostgreSQL

---

## Etapa C

Construir Dashboard Web

---

## Etapa D

Construir Consulta Global

---

## Etapa E

Construir Edición de Estados

---

## Etapa F

Construir Altas

---

## Etapa G

Administración Web completa

---

# CONCLUSIÓN

Después de este inventario ya tenemos identificados:

* Qué existe.
* Qué falta.
* Qué debe quedarse en Desktop.
* Qué debe pasar a Web.
* Qué debe pasar a PostgreSQL.
* En qué orden hacerlo.

Y aparece algo muy importante:

**El siguiente paso técnico más rentable ya no es seguridad.**

La seguridad está suficientemente madura para continuar.

El siguiente paso con mayor retorno es:

> **Inventario N°6 — Modelo Unificado de Datos (SQLite → PostgreSQL)**
>
