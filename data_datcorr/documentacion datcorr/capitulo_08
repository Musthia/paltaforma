# Capítulo 8

# Arquitectura de la Capa Repository

---

# Objetivo

La capa Repository será la única responsable de comunicarse con PostgreSQL.

Ningún Service, Router, ventana Qt o componente React podrá ejecutar consultas SQL directamente.

Toda operación sobre la base deberá realizarse mediante un Repository.

---

# Filosofía

La arquitectura seguirá el patrón Repository.

```text
Qt

↓

FastAPI

↓

Service

↓

Repository

↓

SQLAlchemy

↓

PostgreSQL
```

Cada capa conoce únicamente la inmediatamente inferior.

---

# Responsabilidades

Un Repository será responsable de:

• consultar registros

• insertar registros

• modificar registros

• eliminar registros (cuando corresponda)

• ejecutar búsquedas

• manejar transacciones

• encapsular SQLAlchemy

Nada más.

---

# Lo que NO debe hacer

Un Repository nunca deberá

• validar permisos

• validar reglas de negocio

• decidir si una operación está permitida

• mostrar mensajes

• registrar eventos de interfaz

Todo eso pertenece al Service.

---

# Separación de responsabilidades

```text
Repository

↓

Acceso a datos

-------------------

Service

↓

Reglas de negocio

-------------------

Router

↓

HTTP

-------------------

Qt / React

↓

Interfaz
```

Cada capa tiene una única responsabilidad.

---

# Organización

```text
repositories/

    base_repository.py

    usuarios_repository.py

    permisos_repository.py

    auditoria_repository.py

    refresh_tokens_repository.py

    token_blacklist_repository.py

    escribania_repository.py

    ips_repository.py

    igpj_repository.py

    maternidad_repository.py

    pediatrico_repository.py
```

Un Repository por entidad.

---

# BaseRepository

Todos heredarán de BaseRepository.

```text
BaseRepository

        ↑

UsuariosRepository

PermisosRepository

EscribaniaRepository

IPSRepository

IGPJRepository

...
```

---

# Funciones comunes

BaseRepository concentrará toda la lógica compartida.

Ejemplo

```python
class BaseRepository:

    def __init__(self, session):
        self.session = session

    def commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()

    def close(self):
        self.session.close()
```

Los repositorios concretos reutilizarán estos métodos.

---

# Inyección de sesión

La sesión nunca será creada dentro del Repository.

Incorrecto

```python
SessionLocal()
```

Correcto

```python
repo = UsuariosRepository(db)
```

donde

```python
db = Depends(get_db)
```

Esto garantiza una única transacción por petición.

---

# Un Repository = Un Modelo

Ejemplo

```text
UsuariosRepository

↓

Usuario
```

```text
EscribaniaRepository

↓

Escribania
```

Nunca un Repository manipulará múltiples modelos sin una razón justificada.

---

# Métodos mínimos

Cada Repository deberá implementar como mínimo

```text
get_by_id()

get_all()

create()

update()

delete()

search()
```

Según la necesidad podrán agregarse otros métodos especializados.

---

# Búsquedas

Las búsquedas complejas pertenecerán al Repository.

Ejemplo

```python
buscar_por_texto()
```

```python
buscar_por_documento()
```

```python
buscar_por_caja()
```

No deberán construirse consultas SQL desde los Services.

---

# Consultas dinámicas

Para organismos con estructuras diferentes se implementará una búsqueda dinámica.

Ejemplo

```python
search(texto)
```

El Repository decidirá internamente sobre qué columnas consultar.

Así el Service nunca necesitará conocer la estructura de la tabla.

---

# Retorno de datos

Los Repository devolverán objetos SQLAlchemy.

Ejemplo

```python
Usuario
```

```python
Escribania
```

No devolverán JSON.

No devolverán diccionarios.

La transformación será responsabilidad del Service.

---

# Transacciones

Cada operación crítica utilizará transacciones.

```python
try:

    ...

    session.commit()

except:

    session.rollback()
```

Nunca dejar transacciones abiertas.

---

# Manejo de errores

Los Repository capturarán únicamente errores relacionados con la base.

Ejemplo

```text
IntegrityError

OperationalError

ProgrammingError
```

No capturarán errores de lógica de negocio.

---

# Logging

Cada operación importante deberá registrarse.

Ejemplo

```text
LISTAR

BUSCAR

INSERTAR

ACTUALIZAR

ELIMINAR
```

Esto facilitará el diagnóstico de problemas.

---

# Reutilización

Los métodos deberán ser reutilizables.

Ejemplo

```python
buscar_por_id()
```

Será utilizado por

Qt

React

FastAPI

Servicios internos

sin modificaciones.

---

# Especialización

Cada organismo podrá implementar búsquedas propias.

Ejemplo

Escribanía

```python
buscar_por_legajo()
```

IPS

```python
buscar_por_expediente()
```

IGPJ

```python
buscar_por_documento()
```

La lógica quedará encapsulada.

---

# Repository Factory (Futuro)

Para evitar múltiples condicionales se implementará una fábrica de repositorios.

Ejemplo

```python
RepositoryFactory.get("escribania")
```

retorna

```python
EscribaniaRepository
```

Esto permitirá seleccionar el Repository adecuado de forma dinámica.

---

# Ejemplo completo

```text
Usuario escribe

↓

React

↓

POST

↓

FastAPI

↓

UsuariosService

↓

UsuariosRepository

↓

SQLAlchemy

↓

PostgreSQL
```

Ninguna otra capa conocerá SQLAlchemy.

---

# Ventajas

✔ Código desacoplado.

✔ Fácil mantenimiento.

✔ Fácil reemplazo de la base.

✔ Consultas centralizadas.

✔ Reutilización máxima.

✔ Fácil testing.

✔ Mejor rendimiento.

✔ Escalable.

✔ Compatible con Qt y React.

---

# Convenciones

Todos los Repository deberán mantener la misma estructura.

```python
get_by_id()

get_all()

search()

create()

update()

delete()
```

Esto facilita enormemente el mantenimiento.

---

# Integración con Services

El Service será el único consumidor del Repository.

Ejemplo

```python
UsuariosService

↓

UsuariosRepository
```

Nunca

```text
Qt

↓

Repository
```

ni

```text
React

↓

Repository
```

---

# Resultado Final

La capa Repository constituye el punto único de acceso a PostgreSQL. Encapsula completamente SQLAlchemy, centraliza las consultas, garantiza el manejo correcto de sesiones y transacciones, y proporciona una interfaz uniforme para todos los Services. Gracias a esta arquitectura, tanto la aplicación Qt como la aplicación React utilizan exactamente el mismo mecanismo de acceso a datos, manteniendo un sistema consistente, desacoplado y preparado para crecer.
