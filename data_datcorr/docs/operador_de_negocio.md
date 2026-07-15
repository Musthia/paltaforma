# INVENTARIO OFICIAL N°4

## Operaciones de negocio de DatCorr

Este inventario ya no describe carpetas ni ventanas.

Describe:

* Qué hace realmente el sistema.
* Qué operaciones existen.
* Qué operaciones deben migrarse a Web.
* Qué operaciones deben conservarse en Desktop.
* Qué operaciones compartirán Backend.

---

# MÓDULO 1

## Autenticación

### Operaciones

* Login
* Logout
* Refresh Token
* Control JWT
* Control Blacklist
* Auditoría de sesiones

### Estado

Backend Web:

✔ Implementado

Desktop:

✔ Consume API

---

# MÓDULO 2

## Selección de Organismo

### Operación

Usuario selecciona:

* IGPJ
* IPS
* MATERNIDAD
* PEDIATRICO
* ESCRIBANIA
* futuras bases

### Resultado

Carga:

* plantilla correspondiente
* búsquedas correspondientes
* estructura correspondiente

### Estado

Desktop:

✔ Implementado

Web:

✘ Pendiente

---

# MÓDULO 3

## Consulta de Registros

### Operación principal del sistema

Flujo:

1. Seleccionar base
2. Escribir criterio
3. Buscar
4. Mostrar resultados

---

## Campos principales de búsqueda

### IGPJ

Campo principal:

denominacion

Búsqueda real:

todos los campos

---

### IPS

Campo principal:

n_lote

Búsqueda real:

todos los campos

---

### MATERNIDAD

Campo principal:

documento

Búsqueda real:

todos los campos

---

### PEDIATRICO

Campo principal:

hh_cc

Búsqueda real:

todos los campos

---

### ESCRIBANIA

Campo principal:

nombre_apellido

Búsqueda real:

todos los campos

---

### Estado

Desktop:

✔ Implementado

Web:

✘ Pendiente

---

# MÓDULO 4

## Visualización Completa

Botón:

"Base de datos completa"

### Operación

Carga todos los registros

en TreeView

con paginación visual

(según capacidad actual)

### Estado

Desktop:

✔ Implementado

Web:

✘ Pendiente

---

# MÓDULO 5

## Alta de Registros

### Operación

Seleccionar organismo

↓

Abrir plantilla

↓

Completar campos

↓

Guardar

---

### Campos automáticos

No editables:

* id
* registro

registro = fecha y hora sistema

---

### Estado

Desktop:

✔ Implementado

Web:

✘ Pendiente

---

# MÓDULO 6

## Edición de Registros

### Operación

Buscar

↓

Abrir registro

↓

Modificar

↓

Guardar

---

Uso frecuente:

actualización de estado

---

### Estado

Desktop:

✔ Implementado

Web:

✘ Pendiente

---

# MÓDULO 7

## Eliminación de Registros

### Operación

Seleccionar registro

↓

Eliminar

---

### Estado

Desktop:

✔ Implementado

Web:

✘ Pendiente

---

# MÓDULO 8

## Administración de Usuarios

Ventana:

ventana_usuarios.py

### Operaciones

* Crear usuario
* Editar usuario
* Activar usuario
* Desactivar usuario
* Gestionar permisos

---

### Estado

Desktop:

✔ Implementado

Backend:

✔ Implementado

Web:

✔ Parcialmente implementado

---

# MÓDULO 9

## Auditoría

Actualmente registra:

* Login
* Logout
* Refresh
* Revocación JWT
* Blacklist
* Operaciones de usuarios

---

### Estado

Backend:

✔ Implementado

Web:

✔ Implementado

Desktop:

consume backend

---

# MÓDULO 10

## Seguridad JWT

Incluye:

* Access Token
* Refresh Token
* Blacklist
* Middleware Global
* Revocación
* Reuse Detection (en desarrollo)

---

### Estado

Backend:

✔ Muy avanzado

---

# OPERACIONES MÁS IMPORTANTES DEL NEGOCIO

Según lo que explicaste, el uso real del sistema es:

| Operación               | Frecuencia |
| ------------------------ | ---------- |
| Consulta de registros    | Muy alta   |
| Actualización de estado | Muy alta   |
| Alta de registros        | Alta       |
| Edición de registros    | Media      |
| Gestión usuarios        | Baja       |
| Eliminación             | Baja       |

---

# CONCLUSIÓN DEL INVENTARIO

Ya tenemos identificados:

1. Arquitectura Desktop.
2. Arquitectura Backend.
3. Esquema PostgreSQL.
4. Esquema de bases documentales.
5. Flujo real de trabajo.
