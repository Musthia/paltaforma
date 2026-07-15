
from pathlib import Path

text = """# Arquitectura de Seguridad v1.0

## Objetivo

Definir un único modelo de seguridad para toda la plataforma DATCORR.

---

# 1. Principios

- Un solo inicio de sesión.
- Una única identidad por usuario.
- Mínimo privilegio.
- Toda acción queda auditada.
- Ningún cliente accede directamente a PostgreSQL.

---

# 2. Componentes

## Identity Service

Responsable de:

- Login
- Logout
- JWT
- Refresh Token
- Recuperación de contraseña
- Gestión de sesiones

## Security Service

Responsable de:

- Roles
- Permisos
- Validación de acceso
- Bloqueo de usuarios
- Políticas de contraseña

## Audit Service

Registra:

- Inicio y cierre de sesión
- Altas, bajas y modificaciones
- Consultas críticas
- Errores
- Intentos fallidos
- Eventos de sincronización

---

# 3. Autenticación

Cliente (Qt / React)
    ↓
API Gateway
    ↓
Identity Service
    ↓
JWT + Refresh Token

El cliente nunca almacena contraseñas.

---

# 4. Autorización

Cada petición verifica:

1. Usuario válido.
2. Token vigente.
3. Rol.
4. Permiso del módulo.
5. Acción permitida.

Ejemplo:

SIMCO

- Crear solicitud
- Responder
- Consultar

DATCORR

- Buscar
- Modificar
- Administrar

---

# 5. Roles

- Administrador Plataforma
- Administrador Módulo
- Supervisor
- Operador
- Consulta

Los permisos se asignan por módulo.

---

# 6. Auditoría

Registrar:

- Usuario
- Fecha y hora
- IP
- Cliente (Web/Escritorio)
- Módulo
- Acción
- Resultado

Nunca eliminar registros de auditoría.

---

# 7. Seguridad de comunicaciones

- HTTPS obligatorio.
- TLS entre Nodo Público y Nodo Maestro.
- API autenticada.
- Sin acceso directo desde Internet a PostgreSQL.

---

# 8. Protección de datos

- Backups automáticos.
- Restauración probada.
- Contraseñas con hash seguro.
- Secretos fuera del código (.env o gestor de secretos).

---

# 9. Reglas obligatorias

1. PostgreSQL nunca expuesto.
2. Todo acceso pasa por la API.
3. Toda modificación queda auditada.
4. Permisos centralizados en Platform.
5. La seguridad pertenece a Platform, no a los módulos.

---

# 10. Objetivo final

Un usuario inicia sesión una sola vez y accede únicamente a los módulos y acciones autorizados, con trazabilidad completa de todas las operaciones.
"""
path="/mnt/data/Arquitectura_Seguridad_v1.0.md"
Path(path).write_text(text,encoding="utf-8")
print(path)
