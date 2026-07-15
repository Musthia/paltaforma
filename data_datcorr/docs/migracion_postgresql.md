# MIGRACIÓN A POSTGRESQL - DATC0RR

## 🧭 OBJETIVO GENERAL

Migrar todas las bases SQLite hacia PostgreSQL (datcorr) manteniendo estabilidad del sistema PySide6.

---

## 🟢 ESTADO ACTUAL

### Seguridad (POSTGRESQL ✔)

- usuarios
- permisos
- usuarios_permisos
- refresh_tokens
- token_blacklist
- auditoria

✔ COMPLETADO

---

## 🟡 MÓDULOS PENDIENTES (SQLite)

- Módulo 1: Catastro
- Módulo 2: (pendiente definir)
- Módulo 3: ...
- Módulo 7: ...

---

## 🧱 ESTRATEGIA

1. Crear capa repository (PostgreSQL only)
2. Migrar módulo usuarios completamente
3. Migrar módulos funcionales uno por uno
4. Eliminar SQLite progresivamente
5. Validar UI después de cada módulo

---

## 🚫 REGLAS CRÍTICAS

- Prohibido mezclar SQLite y PostgreSQL en repositorios
- Prohibido acceso directo a ORM desde ventanas
- Prohibido SQLAlchemy en services (solo repositories)
- Ventanas SOLO consumen services

---

## 🔵 PRIMERA FASE

✔ Usuarios (ya estable en PostgreSQL)
➡ será el modelo base para repositorios

---

## ⚠ RIESGOS

- Doble acceso a datos (evitar)
- Dependencias ocultas en services
- Uso directo de ORM en UI

---

## 📌 PROGRESO

- [X] Auth PostgreSQL
- [ ] Usuarios repository
- [ ] Catastro migration
- [ ] Otros módulos
