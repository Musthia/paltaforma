# DATCORR_ARCHITECTURE_V1

## Proyecto

DATCORR

Sistema de gestión documental y administrativa con doble plataforma:

* Aplicación Desktop (PySide6 + SQLite)
* Aplicación Web (FastAPI + PostgreSQL)

Objetivo final:

Migrar progresivamente las bases documentales SQLite a PostgreSQL manteniendo compatibilidad entre Desktop y Web.

---

# Arquitectura General

DATCORR

├── Desktop (PySide6)

├── Backend API (FastAPI)

├── PostgreSQL

├── SQLite Legacy

└── Futuro Sistema Unificado

---

# Estructura Principal

## Desktop

C:

base_datcorr.py

ventana_principal.py

utils.py

requirements.txt

.env

### Carpetas

controller/

model/

ui/

ventanas/

img/

bases_g/

utils/

---

# Bases SQLite

Ubicación:

bases_g/

## Bases Activas

### ESCRIBANIA.db

Tabla:

Datcorr_database

Registros:

682

Campos:

id_Datcorr_database

estado

ingreso

egreso

observaciones

caja

localidad

legajo

nombre_apellido

timbrado_fiscal

registro

---

### IGPJ.db

Tabla:

Datcorr_database

Registros:

36439

Campos:

id_Datcorr_database

denominacion

departamento

expediente

estado

caratula

ingreso

egreso

observaciones

caja

registro

---

### IGPJ TXT LISTADO.db

Tabla:

Datcorr_database

Registros:

30050

---

### IGPJ_LISTADO_NUEVO.db

Tabla:

Datcorr_database

Registros:

1630

---

### IPS.db

Tabla:

Datcorr_database

Registros:

22048

---

### MATERNIDAD.db

Tabla:

Datcorr_database

Registros:

29836

---

### PEDIATRICO.db

Tabla:

Datcorr_database

Registros:

35175

---

## Observación Arquitectónica

Todas las bases utilizan una tabla principal denominada:

Datcorr_database

La estructura interna varía según cada organismo.

No existe actualmente una base maestra documental.

Cada base opera de manera independiente.

---

# Backend Web

Ubicación:

backend/

## Estructura

backend

├── core

├── database

├── middleware

├── routers

├── schemas

├── security

├── services

└── main.py

---

# Core

## logger.py

Sistema centralizado de logs.

## exceptions.py

Excepciones personalizadas.

## handlers.py

Manejadores globales.

---

# Routers

## auth_router.py

Login

Logout

JWT

Refresh

## usuarios_router.py

CRUD Usuarios

Permisos

Roles

## admin_router.py

Funciones administrativas

---

# Security

## jwt_manager.py

Generación de:

Access Token

Refresh Token

JTI

Expiración

## jwt_bearer.py

Autenticación JWT

## permissions.py

Control de permisos

---

# Middleware

## jwt_middleware.py

Funciones:

Validación JWT

Detección de JWT inválido

Detección de JWT revocado

Bloqueo global

Inyección de usuario en request.state

Auditoría automática

---

# Servicios

## auth_service.py

Login

Logout

Refresh

## blacklist_service.py

Revocación JWT

Blacklist global

## auditoria_service.py

Registro centralizado

## usuarios_service.py

Gestión usuarios

---

# PostgreSQL

Base:

datcorr

---

## Tabla usuarios

Campos:

id

usuario

password_hash

nombre

apellido

rol

nivel_seguridad

activo

es_superusuario

fecha_creacion

fecha_actualizacion

---

## Tabla permisos

Campos:

id

codigo

descripcion

---

## Tabla usuarios_permisos

Campos:

id

usuario_id

permiso_id

---

## Tabla refresh_tokens

Campos:

id

usuario_id

refresh_token

token_jti

ip_address

user_agent

created_at

expires_at

revoked

---

## Tabla token_blacklist

Campos:

id

jti

usuario

motivo

revoked_at

activo

---

## Tabla auditoria

Campos:

id

fecha

usuario

accion

tabla

registro_id

detalle

endpoint

token_jti

ip

ip_address

user_agent

---

# Seguridad Implementada

## Autenticación

JWT Access Token

JWT Refresh Token

Refresh Rotation

Refresh Revocation

Logout Seguro

Blacklist Global

Middleware Global JWT

---

## Auditoría

LOGIN_SUCCESS

LOGIN_FAILED

LOGOUT_SUCCESS

LOGOUT_FAILED

TOKEN_REVOKED

TOKEN_REVOKED_GLOBAL

TOKEN_INVALID

---

## Permisos

Roles

Permisos específicos

Superusuarios

Nivel de seguridad

---

# Objetivo de Migración

Estado actual:

SQLite → Operativo

PostgreSQL → Usuarios y Seguridad

Estado objetivo:

PostgreSQL:

Usuarios

Permisos

Auditoría

Documentos

Movimientos

Organismos

Búsquedas

Reportes

Desktop y Web utilizando la misma API.

---

# Próximas Fases

FASE 7

Inventario funcional completo

FASE 8

Modelo documental unificado PostgreSQL

FASE 9

Migración progresiva SQLite → PostgreSQL

FASE 10

Cliente Desktop consumiendo API REST

FASE 11

Convivencia Desktop + Web

FASE 12

Desacoplamiento definitivo de SQLite

---

Versión:

DATCORR_ARCHITECTURE_V1

Fecha:

31/05/2026
