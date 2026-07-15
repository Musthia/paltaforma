# Capítulo 4

# Arquitectura de Persistencia y Acceso a Datos

---

# Objetivo

La persistencia será completamente centralizada sobre PostgreSQL.

Ni la aplicación de escritorio ni la aplicación web accederán directamente a la base de datos.

Toda operación deberá realizarse mediante una única capa de acceso compuesta por:

* SQLAlchemy
* Modelos ORM
* Repositories
* Services

Esta arquitectura garantiza que cualquier modificación en la base de datos afecte automáticamente a ambos clientes sin necesidad de duplicar lógica.

---

# Filosofía

La aplicación no trabaja con SQL.

La aplicación trabaja con objetos.

Ejemplo:

Qt

↓

UsuarioService

↓

UsuariosRepository

↓

SQLAlchemy

↓

PostgreSQL

Lo mismo para React:

React

↓

API FastAPI

↓

UsuarioService

↓

UsuariosRepository

↓

SQLAlchemy

↓

PostgreSQL

Es decir:

Existe un único código de acceso a datos.

---

# Organización de carpetas

database/

```
database/
│
├── conexion.py
├── session.py
├── base.py
├── modelos/
│     usuario.py
│     permiso.py
│     escribania.py
│     ips.py
│     maternidad.py
│     pediatrico.py
│     igpj.py
│
└── __init__.py
```

repositories/

```
repositories/

base_repository.py

usuarios_repository.py

permisos_repository.py

escribania_repository.py

ips_repository.py

maternidad_repository.py

igpj_repository.py

pediatrico_repository.py
```

services/

```
services/

usuario_service.py

permisos_service.py

escribania_service.py

ips_service.py

...
```

---

# BaseRepository

Todos los repositories heredan de BaseRepository.

Responsabilidades:

* abrir Session
* cerrar Session
* rollback automático
* commit
* operaciones comunes

Ejemplo

```
UsuariosRepository

↓

BaseRepository

↓

SessionLocal()

↓

PostgreSQL
```

Nunca un repository deberá abrir conexiones manualmente.

---

# Modelos ORM

Cada tabla PostgreSQL tendrá un único modelo ORM.

Ejemplo:

usuarios

↓

Usuario.py

escribania.Datcorr_database

↓

Escribania.py

ips.Datcorr_database

↓

IPS.py

maternidad.Datcorr_database

↓

Maternidad.py

No existirán modelos duplicados.

---

# Repositories

Un Repository únicamente realiza operaciones CRUD.

Ejemplo:

UsuariosRepository

```
get_by_id()

get_all()

create()

update()

delete()

buscar_por_usuario()

buscar_por_nombre()
```

No contiene reglas de negocio.

No valida permisos.

No valida usuarios.

No genera reportes.

Su única responsabilidad es acceder a PostgreSQL.

---

# Services

Los Services contienen toda la lógica del sistema.

Ejemplo:

UsuarioService

```
crear_usuario()

editar_usuario()

cambiar_password()

activar_usuario()

desactivar_usuario()
```

El Service decide:

qué Repository utilizar

qué validar

qué permisos verificar

qué errores devolver

El Repository simplemente ejecuta.

---

# Flujo completo

Ejemplo Desktop

Usuario pulsa "Guardar"

↓

VentanaEditarUsuario

↓

UsuarioService.actualizar_usuario()

↓

UsuariosRepository.update()

↓

SQLAlchemy

↓

PostgreSQL

---

Ejemplo Web

React

↓

PATCH /usuarios

↓

Router

↓

UsuarioService.actualizar_usuario()

↓

UsuariosRepository.update()

↓

SQLAlchemy

↓

PostgreSQL

El flujo es idéntico.

---

# Separación absoluta de responsabilidades

UI

Responsabilidad:

mostrar información

capturar datos

jamás consulta la base

---

Service

Responsabilidad:

lógica

reglas

validaciones

permisos

---

Repository

Responsabilidad:

CRUD

consultas

persistencia

---

Model

Responsabilidad:

mapear tablas PostgreSQL

---

Base de datos

Responsabilidad:

almacenar información

---

# Consultas dinámicas

Cada organismo posee su propio Repository.

Ejemplo:

```
EscribaniaRepository

IPSRepository

IGPJRepository

PediatricoRepository
```

Todos implementan la misma interfaz.

Ejemplo:

```
buscar()

listar()

obtener()

actualizar()

contar()
```

Esto permitirá que la UI pueda cambiar de organismo sin modificar su lógica.

---

# Session Management

Cada operación abre una Session.

```
SessionLocal()

↓

Repository

↓

commit()

↓

close()
```

Nunca habrá sesiones globales.

Nunca se compartirán sesiones entre ventanas.

Esto evita bloqueos y pérdidas de memoria.

---

# Errores

Todo Repository captura errores SQLAlchemy.

Ejemplo:

```
IntegrityError

NoResultFound

OperationalError
```

Los transforma en excepciones entendibles para el Service.

El Service decide qué mostrar al usuario.

---

# Beneficios

✔ Un único acceso a datos.

✔ Sin SQL duplicado.

✔ Sin conexiones manuales.

✔ Fácil mantenimiento.

✔ Fácil agregar nuevos organismos.

✔ Desktop y Web utilizan exactamente la misma lógica.

✔ Escalable para millones de registros.

---

# Resultado final

Toda la aplicación compartirá una única capa de persistencia.

Esto permitirá que cualquier mejora realizada en un Repository beneficie automáticamente tanto a la aplicación de escritorio como a la aplicación web, manteniendo un único código fuente para el acceso a datos y garantizando consistencia en todo el sistema.
