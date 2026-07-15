# Modelo de Datos Global v1.0

## Objetivo
Definir qué información pertenece a la plataforma y qué información pertenece a cada módulo.

---

# Base: platform

## Gestión común
- usuarios
- roles
- permisos
- usuarios_permisos
- modulos
- usuarios_modulos
- auditoria
- refresh_tokens
- token_blacklist
- configuracion
- notificaciones
- logs

Responsabilidad:
- Identidad.
- Seguridad.
- Configuración.
- Auditoría.

Nunca almacena datos funcionales de los módulos.

---

# Base: datcorr

Responsabilidad:
- Expedientes.
- Cajas.
- Movimientos.
- Organismos.
- Búsquedas.
- Reportes documentales.

Puede contener múltiples esquemas (igpj, ips, maternidad, etc.).

---

# Base: simco

Responsabilidad:
- Solicitudes.
- Respuestas.
- Seguimiento.
- Estados.
- Historial.
- Trazabilidad.

No almacena usuarios ni permisos.

---

# Relaciones

Platform
│
├── controla acceso a DATCORR
└── controla acceso a SIMCO

Los módulos consultan la plataforma para autenticar y autorizar.

---

# Principios

1. Un dato pertenece a un único módulo.
2. Usuarios y permisos nunca se duplican.
3. La auditoría es única.
4. Cada módulo puede evolucionar sin afectar a los demás.
5. La comunicación entre módulos se realiza mediante APIs, nunca accediendo directamente a otra base de datos.

---

# Evolución

Futuros módulos:
- Inventario
- Digitalización
- Mesa de Entradas
- Archivo Digital

Cada uno tendrá su propia base de datos y reutilizará los servicios de Platform.
