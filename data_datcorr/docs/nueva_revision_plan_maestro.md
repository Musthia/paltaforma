
Arquitectura target: React + Qt → FastAPI → PostgreSQL

# Punto del Plan	Estado	Detalle

1	Finalizar migración a PostgreSQL	✅ ~80%	Auth tables OK. Fases 1-3 completadas (DAO genérico, plantillas refactorizadas). Pendiente: ejecutar scripts de migración SQLite→PG para datos existentes
2	Repositories por esquema	⚠️ Parcial	repositories/ tiene base + usuarios + permisos + reportes, pero NO hay repositorio por esquema/organismo. El routing dinámico está en db/router.py pero sin patrón repository.
3	Services con lógica de negocio	✅ Ok	services/ (auth, permisos, usuario), backend/services/ (database_service_web, auditoria, auth), db/service.py (wrapper router)
4	API REST completa	⚠️ Parcial	FastAPI con 6 routers: auth, admin, usuarios, database, dashboard, reportes. Cubre auth y CRUD de datos, pero la API no expone todos los endpoints que el escritorio necesita
5	Migrar React a consumir API	✅ Ok	React (frontend/) consume API vía axios. Pages: Dashboard, Database, CargaDatos, Reportes, Auditoria, Usuarios
6	Migrar Qt a consumir API (sin acceso directo a BD)	❌ Incumplido	El escritorio (base_datcorr.py:148) llama initialize_postgres() y accede a PostgreSQL directamente vía DatcorrDAOPostgres → db_registry. Usa ApiClient solo para login, NO para datos.
7	Centralizar reportes	⚠️ Parcial	Backend de reportes completo (backend/reportes/ con service, consultas, exportadores CSV/XLSX/PDF, router). React lo consume. Qt no tiene acceso a reportes vía API.
8	Implementar caché/offline	❌ No iniciado	Sin implementación
Resumen de brechas principales
CRÍTICO — Qt acceso directo a BD: El escritorio bypassea completamente el backend FastAPI para todas las operaciones de datos. Rompe el principio de "una sola fuente de datos" y "validaciones únicas".
MEDIO — Sin repositorios por esquema: No hay una capa de abstracción formal entre DatcorrDAOPostgres y cada organismo. El db/router.py es genérico pero no encapsula lógica por esquema.
BAJO — Migración SQLite pendiente: Los datos históricos en bases_g/*.db no se han migrado a PostgreSQL. Fácil de resolver ejecutando los scripts migrate_*.py.
Acciones recomendadas (priorizadas)
Prio	Acción
1	Crear endpoints FastAPI para todas las operaciones CRUD que el escritorio necesita (ya existe database_router.py con list, search, insert, update, delete — verificar cobertura)
2	Refactorizar el escritorio para usar ApiClient en lugar de DatcorrDAOPostgres directo
3	Crear repositorios por esquema (IPSRepository, EscribaniaRepository, etc.) o un repositorio genérico parametrizable
4	Ejecutar migración SQLite→PostgreSQL
5	Implementar caché/offline si es necesario
