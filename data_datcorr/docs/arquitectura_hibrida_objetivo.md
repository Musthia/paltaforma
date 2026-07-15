# Arquitectura hibrida objetivo

## Objetivo funcional

DatCorr debe permitir consultar, crear, editar, actualizar, desactivar/eliminar y auditar datos desde una app desktop y una app web, con capacidad de anexar mas tablas, modulos y bases sin duplicar reglas de negocio.

## Regla principal

FastAPI debe convertirse progresivamente en la fuente de verdad.

- Desktop PySide6: cliente operativo.
- Web React: cliente operativo.
- Backend FastAPI: reglas de negocio, permisos, auditoria, validaciones y acceso principal a datos.
- PostgreSQL: base central para usuarios, permisos, auditoria y datos normalizados.
- Bases/tablas anexas: deben integrarse mediante servicios/repositorios controlados, no con consultas sueltas desde pantallas.

## Fronteras recomendadas

### Frontend web

- No accede directo a base de datos.
- Consume endpoints del backend.
- Centraliza llamadas HTTP en `frontend/src/services`.
- Usa componentes/hooks solo para UI, estado y experiencia de usuario.

### Desktop

- Debe migrar gradualmente de acceso directo a base hacia consumo de API.
- Puede mantener PySide6 y sus ventanas actuales.
- Las acciones sensibles de usuarios, permisos y auditoria deben moverse primero a API.

### Backend

- Expone routers por dominio: usuarios, permisos, autenticacion, datos anexos.
- Valida permisos y niveles antes de ejecutar operaciones.
- Registra auditoria en operaciones criticas.
- Centraliza sesiones DB en una unica dependencia.

### Database

- `database/conexion.py` es la conexion base compartida.
- Los modelos viven en `database/modelos*.py`.
- Los repositorios encapsulan consultas.
- Los servicios aplican reglas de negocio.

## Patron para anexar nuevas tablas o bases

Para cada nuevo modulo:

1. Definir modelo o adaptador de datos.
2. Crear schema de entrada/salida si se expone por API.
3. Crear repositorio o consulta controlada.
4. Crear servicio con reglas de negocio.
5. Crear router FastAPI.
6. Crear cliente en web/desktop.
7. Agregar permisos y auditoria si corresponde.
8. Agregar pruebas o verificacion manual documentada.

## Orden de migracion recomendado

1. Consolidar dependencias y conexion DB.
2. Consolidar servicios backend activos y retirar servicios duplicados no usados.
3. Migrar administracion de usuarios desktop para usar API.
4. Migrar permisos desktop para usar API.
5. Definir modulo generico de datos consultables.
6. Agregar operaciones de edicion/actualizacion/eliminacion con auditoria.
7. Preparar patron para anexar futuras tablas/bases.
