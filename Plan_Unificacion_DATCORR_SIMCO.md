# Plan de Unificación DATCORR + SIMCO

## Objetivo

Construir una única plataforma con un solo núcleo de autenticación, permisos y auditoría, manteniendo inicialmente ambos módulos y sus bases de datos independientes.

---

# 1. Auditoría de recursos existentes

## DATCORR
- Cliente escritorio (PySide6).
- Cliente Web (React).
- Backend FastAPI.
- PostgreSQL.
- Gestión documental, búsquedas y movimientos.
- Usuarios, permisos y auditoría.

## SIMCO
- Cliente Web (React).
- Backend FastAPI.
- PostgreSQL.
- Solicitudes.
- Respuestas.
- Trazabilidad.

## Recursos comunes detectados
- Usuarios.
- Roles.
- Permisos.
- JWT.
- Auditoría.
- Reportes.
- Notificaciones.
- PostgreSQL.
- FastAPI.
- React.

---

# 2. Recursos a crear

## Plataforma (Platform)

Servicios comunes:

- Autenticación.
- Usuarios.
- Roles.
- Permisos.
- Auditoría.
- Configuración.
- API Gateway.
- Sincronización.
- Notificaciones.

---

# 3. Arquitectura objetivo

Platform

- Identity Service
- Security Service
- Audit Service
- API Gateway

Módulos

- DATCORR
- SIMCO

Bases

- platform
- datcorr
- simco

---

# 4. Plan de ejecución

## Fase 1
- Inventario completo de ambos proyectos.
- Identificar código duplicado.
- Documentar APIs.
- Documentar modelos de datos.

Entregable:
Mapa completo de la plataforma.

---

## Fase 2
Crear plataforma común.

Migrar:

- Usuarios
- Roles
- Permisos
- JWT
- Refresh Tokens
- Auditoría

---

## Fase 3

Convertir DATCORR en módulo.

Mantener:

- App Escritorio
- App Web
- Arquitectura híbrida
- PostgreSQL propia

---

## Fase 4

Convertir SIMCO en módulo.

Mantener:

- Base propia
- Backend propio (integrado al núcleo)
- Funcionalidad completa

---

## Fase 5

Unificar autenticación.

Resultado:

Un solo login.

Acceso según permisos.

---

## Fase 6

API Gateway único.

Todos los clientes consumen:

Platform API

No acceso directo a bases.

---

## Fase 7

Sincronización híbrida DATCORR.

Nodo Maestro Local.

Nodo Público Cloud.

Modo consulta automática ante pérdida del maestro.

---

## Fase 8

Servicios compartidos.

- Reportes
- Correos
- Auditoría
- Logs
- Notificaciones

---

## Fase 9

Pruebas

- Seguridad
- Rendimiento
- Recuperación
- Sincronización
- Auditoría

---

## Resultado esperado

Una plataforma modular con:

- Un único login.
- Un único sistema de permisos.
- Una única auditoría.
- DATCORR híbrido.
- SIMCO web.
- Bases independientes.
- Servicios compartidos.
- Preparada para incorporar nuevos módulos sin rediseñar la arquitectura.
