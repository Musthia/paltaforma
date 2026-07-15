## Lo que realmente es DatCorr

DatCorr no es un CRUD de usuarios.

DatCorr es un:

**Sistema de Gestión Documental Multi-Organismo**

con:

* múltiples repositorios documentales independientes
* estructura específica por organismo
* consultas transversales
* carga documental
* actualización de estados
* administración de usuarios
* auditoría
* trazabilidad

---

# Arquitectura funcional real

## Nivel 1 — Acceso

### Login

Ventana:

* inicio_sesion.py

Funciones:

* autenticación
* validación usuario
* apertura sistema

---

## Nivel 2 — Navegación Principal

### AplicacionPrincipal

Centro operativo del sistema.

Contiene:

### Selector de base

IGPJ

IPS

MATERNIDAD

PEDIATRICO

ESCRIBANIA

IGPJ LISTADO

etc.

---

### Campo búsqueda

Permite:

* buscar por cualquier campo
* localizar registro
* devolver coincidencias

Resultado:

* TreeView
* o mensaje "No encontrado"

---

### Base completa

Carga:

* todos los registros
* en TreeView

Uso:

* consulta masiva
* navegación documental

---

### Carga de datos

Abre:

Selector Base

↓

Plantilla correspondiente

↓

Nuevo registro

---

### Administración usuarios

Abre:

ventana_usuarios.py

---

# Nivel 3 — Gestión documental

Cada organismo tiene:

### DAO propio

Ejemplo:

datcorr_dao_igpj.py

datcorr_dao_ips.py

etc.

---

### Plantilla propia

Ejemplo:

plantilla_IGPJ.py

plantilla_IPS.py

etc.

---

### Base propia

Ejemplo:

IGPJ.db

IPS.db

etc.

---

# Operaciones disponibles

Todas las bases poseen:

## Consulta

Buscar registro

---

## Alta

Crear nuevo registro

---

## Edición

Modificar registro existente

Especialmente:

* estado
* observaciones
* datos documentales

---

## Eliminación

Eliminar registro

(hoy física o lógica según implementación)

---

# Flujo principal del usuario

Esto es importantísimo.

No es:

> Alta → Consulta

Sino:

> Consulta → Actualización

Porque el flujo real es:

1 Buscar documento

↓

2 Existe

↓

3 Actualizar estado

↓

4 Guardar

---

Y en segundo lugar:

1 Nuevo expediente

↓

2 Alta

↓

3 Guardar

---

Eso significa que la funcionalidad más usada es:

### Consulta + Actualización

y no la carga.

Eso impacta directamente en el diseño web.

---

# Modelo UI real

Actualmente:

QTabWidget

recibe pestañas dinámicas.

Ejemplos:

Consulta IGPJ

Alta IGPJ

Consulta IPS

Alta IPS

Consulta Pediátrico

etc.

---

Equivale en web a:

## Tabs dinámicos

o

## Módulos cargados por ruta

Ejemplo:

<pre class="overflow-visible! px-0!" data-start="2671" data-end="2760"><div class="relative w-full mt-4 mb-1"><div class=""><div class="relative"><div class="h-full min-h-0 min-w-0"><div class="h-full min-h-0 min-w-0"><div class="border border-token-border-light border-radius-3xl corner-superellipse/1.1 rounded-3xl"><div class="h-full w-full border-radius-3xl bg-token-bg-elevated-secondary corner-superellipse/1.1 overflow-clip rounded-3xl lxnfua_clipPathFallback"><div class="pointer-events-none absolute end-1.5 top-1 z-2 md:end-2 md:top-1"></div><div class="relative"><div class="pe-11 pt-3"><div class="relative z-0 flex max-w-full"><div id="code-block-viewer" dir="ltr" class="q9tKkq_viewer cm-editor z-10 light:cm-light dark:cm-light flex h-full w-full flex-col items-stretch ͼs ͼ16"><div class="cm-scroller"><pre class="cm-content q9tKkq_readonly m-0"><code><span>/igpj/buscar</span><br/><br/><span>/igpj/nuevo</span><br/><br/><span>/igpj/editar</span><br/><br/><span>/ips/buscar</span><br/><br/><span>/ips/nuevo</span><br/><br/><span>/ips/editar</span></code></pre></div></div></div></div></div></div></div></div></div><div class=""><div class=""></div></div></div></div></div></pre>

---

# Restricciones del sistema

Campos automáticos:

* ID
* Registro
* Fecha/Hora

Se generan automáticamente.

Usuario:

NO los edita.

Solo los consulta.

---

# Inventario funcional consolidado

Hoy DatCorr tiene:

### Seguridad

✅ Login

✅ JWT

✅ Refresh

✅ Blacklist

✅ Middleware

✅ Auditoría

---

### Usuarios

✅ Alta

✅ Edición

✅ Activación

✅ Desactivación

✅ Permisos

---

### Gestión documental

✅ Consulta

✅ Alta

✅ Edición

✅ Eliminación

---

### Organismos

✅ ESCRIBANIA

✅ IGPJ

✅ IGPJ LISTADO

✅ IGPJ LISTADO NUEVO

✅ IPS

✅ MATERNIDAD

✅ PEDIATRICO

---

### Bases futuras

Preparado para crecer
