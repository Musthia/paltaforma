# Arquitectura Plataforma DATCORR v1.0

## 1. Visión

DATCORR será una **plataforma modular**. No existirán sistemas independientes; existirán módulos que comparten un mismo núcleo.

---

# 2. Objetivos

- Un único inicio de sesión.
- Un único sistema de permisos.
- Una única auditoría.
- Una sola lógica de negocio por servicio.
- Incorporar nuevos módulos sin rediseñar la plataforma.

---

# 3. Arquitectura

```
Clientes
├── DATCORR Escritorio (PySide6)
├── DATCORR Web (React)
└── SIMCO Web (React)

            │

      API Gateway

            │

Servicios Compartidos
├── Identity
├── Usuarios
├── Roles
├── Permisos
├── Auditoría
├── Configuración
├── Notificaciones
├── Reportes
└── Sincronización

            │

Módulos
├── DATCORR
└── SIMCO

            │

Bases de Datos
├── platform
├── datcorr
└── simco
```

---

# 4. Responsabilidades

## Platform
- Autenticación (JWT).
- Usuarios.
- Roles.
- Permisos.
- Auditoría.
- Configuración.
- API común.

## DATCORR
- Expedientes.
- Cajas.
- Búsquedas.
- Movimientos.
- Reportes documentales.

## SIMCO
- Solicitudes.
- Respuestas.
- Seguimiento.
- Trazabilidad.

---

# 5. Modelo híbrido DATCORR

## Nodo Maestro (Local)
- Base oficial.
- Escritura.
- Validaciones.
- Auditoría.
- Sincronización.

## Nodo Público (Nube)
- Acceso web.
- API pública.
- Réplica.
- Consultas.
- Escrituras permitidas únicamente reenviando la operación al Nodo Maestro.
- Si el Nodo Maestro no responde: modo solo lectura.

---

# 6. Reglas de arquitectura

1. Existe una única fuente de verdad.
2. Ningún cliente accede directamente a PostgreSQL.
3. Toda operación pasa por la API.
4. La lógica de negocio existe una sola vez.
5. Los módulos son independientes.
6. Los servicios compartidos nunca contienen lógica específica de un módulo.
7. Cada módulo mantiene su propia base de datos.

---

# 7. Integración de nuevos módulos

Nuevo módulo:
1. Crear base de datos.
2. Registrar módulo.
3. Definir permisos.
4. Consumir servicios comunes.
5. Publicar API.

No modificar módulos existentes.

---

# 8. Seguridad

- HTTPS obligatorio.
- JWT + Refresh Token.
- Permisos por módulo y acción.
- Auditoría de operaciones.
- Backups automáticos.
- Registro de eventos de seguridad.

---

# 9. Evolución prevista

v1.0
- DATCORR
- SIMCO

v2.0
- Inventario
- Digitalización
- Mesa de Entradas

v3.0
- Firma Digital
- Aplicación móvil
- Integraciones externas

---

# 10. Principios

- Plataforma antes que aplicación.
- Servicios antes que duplicación.
- Escalabilidad antes que rapidez.
- Seguridad antes que comodidad.
- Simplicidad antes que complejidad.
