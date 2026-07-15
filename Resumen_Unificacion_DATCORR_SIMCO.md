# Resumen y Plan de Ejecución — Unificación DATCORR + SIMCO

> Documento de síntesis de los 4 archivos de arquitectura de `plataforma/` y del inventario real de los proyectos `data_datcorr/` y `simco_v01/`. Sirve como base para implementar la unificación en una única plataforma modular.

---

## 1. Resumen de los 4 documentos de arquitectura

| Documento | Idea central |
|-----------|--------------|
| `Arquitectura_Plataforma_DATCORR_v1.0.md` | Plataforma modular: un solo núcleo (Platform) con servicios compartidos y módulos independientes (DATCORR, SIMCO). Cada módulo mantiene su propia BD. DATCORR es híbrido (Nodo Maestro local + Nodo Público nube). |
| `Arquitectura_Seguridad_v1.0.md` | Un único modelo de seguridad: Identity, Security y Audit Service. JWT + Refresh Token. Permisos por módulo y acción. Auditoría inmutable. PostgreSQL nunca expuesto. |
| `Modelo_Datos_Global_v1.0.md` | Tres bases: `platform` (identidad/seguridad/config/auditoría), `datcorr` (expedientes/cajas/movimientos) y `simco` (solicitudes/respuestas/trazabilidad). Usuarios y permisos nunca se duplican. |
| `Plan_Unificacion_DATCORR_SIMCO.md` | Hoja de ruta en 9 fases: inventario → Platform común → DATCORR módulo → SIMCO módulo → login único → API Gateway → sincronización híbrida → servicios compartidos → pruebas. |

**Principios transversales (de los 4 docs):**
1. Una sola fuente de verdad.
2. Ningún cliente accede directo a PostgreSQL; todo pasa por la API.
3. La lógica de negocio existe una sola vez.
4. Los servicios compartidos no contienen lógica específica de módulo.
5. Usuarios, roles, permisos y auditoría viven en Platform, no en los módulos.
6. Los módulos se comunican por API, nunca tocando la BD de otro módulo.

---

## 2. Estado actual real de los proyectos (lo que se encontró)

### 2.1 `data_datcorr/`
- **Cliente escritorio:** PySide6 (`ui/`, `ventanas/`, `gui/`, `aplicaciones/`).
- **Cliente web:** React + JS/JSX (`frontend/src/`: `api`, `auth`, `components`, `pages`, `router`, `services`). Usa MUI, zustand, react-router, axios, jwt-decode.
- **Backend FastAPI:** `backend/` con estructura profesional:
  - `security/` (`jwt_manager`, `jwt_bearer`, `permissions`)
  - `middleware/` (`jwt_middleware`, `rate_limit_middleware`)
  - `routers/` (`auth`, `usuarios`, `roles`, `permisos`, `admin`, `reportes`, `dashboard`, `database`)
  - `services/` (`auth_service`, `usuarios_service`, `roles_service`, `auditoria_service`, `blacklist_service`, `password_reset_service`)
  - `reportes/` (consultas + exportadores CSV/Excel/PDF)
  - `schemas/`, `core/` (logger, handlers, exceptions), `database/conexion.py`
- **Lógica de negocio legada (no web):** `services/`, `repositories/`, `model/` (DAOs por organismo: igpj, ips, maternidad, pediatrico, escribania), `utils/`, `migration/` (SQLite→PostgreSQL).
- **Datos:** SQLite (`dist/database/User_data.db`, `bases_g/`) y migración a PostgreSQL.

### 2.2 `simco_v01/`
- **Cliente web:** React + TypeScript (`frontend/src/`: `api`, `auth`, `pages`, `routes`, `tabs`, `layout`, `ws`, `utils`, `types`).
- **Backend FastAPI:** `backend/app/` con estructura limpia:
  - `core/` (`jwt`, `rbac`, `security`, `audit`, `deps`, `config`, `ws_manager`)
  - `api/routes/` (`auth`, `users`, `solicitudes`, `respuestas`, `buscar`, `notificaciones`, `messages`, `dashboard`, `ws`)
  - `models/` (`user`, `solicitud`, `respuesta`, `message`, `audit`)
  - `schemas/`, `services/`, `db/` (session, base, seed, init_db)
  - Sirve SPA compilado en producción.
- **Infra:** Dockerfile, Railway, scripts de arranque/tunnel (`iniciar_simco*.bat/.ps1`), `infra/` (SQL de creación de BD/usuario).
- **Datos:** SQLite (`sige_29062026.db`) y PostgreSQL (`test_postgres.py`, backup `.backup`).

### 2.3 Solapamiento detectado (código duplicado a extraer a Platform)
- **Autenticación/JWT:** ambos tienen `auth_service`, `jwt_manager`/`jwt.py`, `security`, `permissions`/`rbac`.
- **Usuarios/Roles/Permisos:** DATCORR (`usuarios_service`, `roles_service`, `permisos`) vs SIMCO (`user_service`, `rbac`).
- **Auditoría:** DATCORR (`auditoria_service`) vs SIMCO (`audit.py` + `audit_service`).
- **Refresh Token / Blacklist:** DATCORR (`blacklist_service`, `refresh_schema`); SIMCO implícito en `jwt`.
- **Notificaciones:** ambos lo mencionan (SIMCO tiene router `notificaciones`).
- **Recuperación de contraseña:** DATCORR (`password_reset_service`); SIMCO no visible.
- **Frontend auth:** ambos manejan JWT/refresh en `src/auth`.

---

## 3. Objetivo de la unificación
Una **plataforma modular** con:
- Un solo login (Identity Service) y un solo sistema de permisos (Security Service).
- Una única auditoría (Audit Service).
- API Gateway único; clientes (Escritorio DATCORR, Web DATCORR, Web SIMCO) sin acceso directo a BD.
- Módulos `datcorr` y `simco` con sus propias bases, reutilizando servicios de Platform.
- DATCORR conserva su arquitectura híbrida (Maestro local / Público nube).

---

## 4. Plan de ejecución (basado en las 9 fases del doc, adaptado al código real)

### Fase 0 — Inventario y mapa (preparación)
- [ ] Mapa de rutas/endpoints de ambos backends (`backend/routers` vs `backend/app/api/routes`).
- [ ] Inventario de modelos de datos (`models/` + `model/` DAOs) y esquemas.
- [ ] Lista de funciones duplicadas (auth, usuarios, roles, permisos, auditoría, notificaciones).
- **Entregable:** `Mapa_Plataforma.md` (fuente única de verdad para las fases siguientes).

### Fase 1 — Crear el núcleo Platform (servicios compartidos)
Extraer a un paquete/servicio `platform/` reutilizable por ambos:
- [ ] **Identity Service:** login, logout, JWT + Refresh Token, recuperación de contraseña (basado en `security/jwt_manager` + `auth_service` de DATCORR y `core/jwt` de SIMCO).
- [ ] **Security Service:** roles, permisos, validación de acceso, bloqueo, políticas (unificar `security/permissions` + `core/rbac`).
- [ ] **Audit Service:** registro inmutable (unificar `auditoria_service` + `core/audit`).
- [ ] **Configuración / Notificaciones / Reportes / Sincronización** como servicios comunes.
- [ ] BD `platform`: `usuarios`, `roles`, `permisos`, `usuarios_permisos`, `modulos`, `usuarios_modulos`, `auditoria`, `refresh_tokens`, `token_blacklist`, `configuracion`, `notificaciones`, `logs`.

### Fase 2 — Migrar identidad y seguridad a Platform
- [ ] Mover modelos `user`/`rol`/`permiso` de ambos proyectos a `platform`.
- [ ] Migrar datos existentes (SQLite/PG de DATCORR y SIMCO) a `platform`.
- [ ] Unificar hash de passwords (bcrypt en ambos; verificar compatibilidad).

### Fase 3 — Convertir DATCORR en módulo
- [ ] Conservar app escritorio (PySide6) y web (React JS).
- [ ] Dejar su lógica de negocio (expedientes, cajas, movimientos) en módulo `datcorr` (BD propia, múltiples esquemas).
- [ ] Reemplazar su `auth_service`/`security` locales por llamadas a Platform.
- [ ] Mantener arquitectura híbrida (Nodo Maestro / Nodo Público).

### Fase 4 — Convertir SIMCO en módulo
- [ ] Conservar backend FastAPI y frontend React TS.
- [ ] Dejar solicitudes/respuestas/trazabilidad en módulo `simco` (BD propia).
- [ ] Reemplazar `core/jwt` + `user_service` + `rbac` locales por Platform.

### Fase 5 — Login único
- [ ] Un solo endpoint de autenticación en Platform.
- [ ] Los 3 clientes (Escritorio, Web DATCORR, Web SIMCO) autentican contra Platform y reciben JWT + Refresh.
- [ ] Autorización por módulo + acción en cada petición.

### Fase 6 — API Gateway único
- [ ] Gateway que enruta a Platform y a los módulos; CORS centralizado.
- [ ] Ningún cliente conecta directo a PostgreSQL.
- [ ] Middleware JWT/rate-limit único (reusar `middleware/jwt_middleware` + `rate_limit` de DATCORR).

### Fase 7 — Sincronización híbrida DATCORR
- [ ] Nodo Maestro local (escritura/validación) y Nodo Público nube (réplica, escritura reenviada al maestro).
- [ ] Modo solo lectura automático si el maestro cae.

### Fase 8 — Servicios compartidos finales
- [ ] Reportes (reusar `backend/reportes/` de DATCORR), Correos/Notificaciones, Logs.
- [ ] Auditoría y trazabilidad únicas en `platform`.

### Fase 9 — Pruebas y cierre
- [ ] Seguridad (authz por módulo, tokens, blacklist).
- [ ] Rendimiento, recuperación (backups/restauración), sincronización híbrida, auditoría.
- [ ] Verificación de que usuarios/permisos no están duplicados.

---

## 5. Riesgos y decisiones pendientes
- **Lenguaje frontend:** DATCORR usa JS/JSX y SIMCO TS/TSX. Decidir si converger a TS o mantener ambos consumiendo el mismo Gateway.
- **Deploy:** SIMCO ya tiene Docker/Railway; DATCORR escritorio requiere distribución nativa. Definir estrategia de despliegue unificada.
- **Datos heredados:** múltiples SQLite y PG; plan de migración a `platform` + módulos.
- **Secretos:** centralizar en `.env`/gestor de secretos (ya parcial en ambos).

---

## 6. Siguiente paso recomendado
Ejecutar **Fase 0** (Mapa_Plataforma.md) para cuantificar exactamente endpoints y entidades duplicadas antes de crear el paquete `platform/`.
