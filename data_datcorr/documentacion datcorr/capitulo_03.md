
# CAPÍTULO 3

# Arquitectura del Backend

---

# 3.1 Objetivo del Backend

El Backend constituye el núcleo del sistema.

Toda la lógica de negocio deberá ejecutarse aquí.

Ni la aplicación de escritorio ni la aplicación web accederán directamente a PostgreSQL.

Toda operación pasará obligatoriamente por FastAPI.

Esto garantiza:

* una única lógica de negocio;
* una única validación;
* una única capa de seguridad;
* una única forma de acceder a los datos.

En otras palabras:

```
Qt
        \
         \
          ---> FastAPI ---> PostgreSQL
         /
React ---/
```

---

# 3.2 Responsabilidades

El Backend será responsable de:

* autenticación
* autorización
* gestión de usuarios
* gestión de permisos
* consultas
* reportes
* auditoría
* movimientos
* exportaciones
* mantenimiento
* logs

Nunca deberá contener código de interfaz gráfica.

Nunca deberá depender de Qt.

Nunca deberá depender de React.

Será completamente independiente.

---

# 3.3 Arquitectura por capas

El Backend seguirá una arquitectura multicapa.

```
Routers
    │
    ▼
Services
    │
    ▼
Repositories
    │
    ▼
Models
    │
    ▼
PostgreSQL
```

Cada capa tendrá una responsabilidad específica.

---

# 3.4 Routers

Los Routers representan la API pública.

Ejemplo:

```
GET /usuarios

POST /usuarios

PATCH /usuarios/{id}

DELETE /usuarios/{id}

GET /consultas

POST /consultas

GET /reportes

POST /reportes
```

Los Routers solamente deberán:

* recibir solicitudes HTTP
* validar datos de entrada
* invocar Services
* devolver respuestas

Nunca contendrán lógica de negocio.

Nunca accederán directamente a la base.

---

# 3.5 Services

Los Services contienen toda la lógica del sistema.

Ejemplo:

```
crear_usuario()

actualizar_usuario()

eliminar_usuario()

buscar_expediente()

registrar_movimiento()

generar_reporte()
```

Aquí se implementan:

* validaciones
* reglas del negocio
* permisos
* auditoría
* consistencia de datos

Los Services son utilizados por:

* React
* Qt

De esta forma ambos clientes ejecutan exactamente la misma lógica.

---

# 3.6 Repositories

Los Repositories encapsulan el acceso a PostgreSQL.

Ejemplo:

```
UsuariosRepository

PermisosRepository

EscribaniaRepository

IpsRepository

IgpjRepository

MaternidadRepository

PediatricoRepository
```

Los Repositories solamente deben conocer SQLAlchemy.

No deben conocer:

* HTTP
* Qt
* React

Su responsabilidad consiste únicamente en:

* consultar
* insertar
* actualizar
* eliminar

---

# 3.7 Models

Los Models representan las tablas PostgreSQL.

Ejemplo:

```
Usuario

Permiso

RefreshToken

TokenBlacklist

Auditoria

Escribania

Ips

Igpj

Maternidad

Pediatrico
```

Cada modelo representa exactamente una tabla.

Los modelos nunca contienen lógica de negocio.

---

# 3.8 Schemas

Los Schemas Pydantic representan los objetos intercambiados por la API.

Ejemplo:

```
UsuarioCreate

UsuarioUpdate

UsuarioResponse

LoginRequest

LoginResponse

ReporteRequest

ReporteResponse
```

Los Schemas son independientes de SQLAlchemy.

Su única función es validar información.

---

# 3.9 Seguridad

Toda petición pasará por JWT.

```
Cliente

↓

Authorization Bearer

↓

JWT

↓

FastAPI

↓

Permisos

↓

Service

↓

Repository
```

Si el token es inválido:

```
401 Unauthorized
```

Si no posee permisos:

```
403 Forbidden
```

Toda la seguridad se implementará en el Backend.

Nunca en React.

Nunca en Qt.

---

# 3.10 Auditoría

Cada operación importante generará un registro.

Ejemplos:

```
LOGIN

LOGOUT

CREATE

UPDATE

DELETE

EXPORT

IMPORT

REPORT

SEARCH
```

Toda auditoría será automática.

Ningún cliente decidirá cuándo registrar eventos.

---

# 3.11 Manejo de Errores

Los errores serán centralizados.

Ejemplo:

```
404

Usuario inexistente
```

```
409

Usuario duplicado
```

```
401

Token inválido
```

```
403

Permisos insuficientes
```

```
500

Error interno
```

La API siempre devolverá respuestas consistentes.

---

# 3.12 Organización del proyecto

```
backend/

    app/

        api/

            routes/

        services/

        repositories/

        security/

        schemas/

        database/

            modelos/

        core/

        utils/

        reports/

        migrations/

        logs/

        config/

main.py
```

Esta organización permite escalar el sistema durante muchos años sin necesidad de reorganizar el código.

---

# 3.13 Flujo completo de una operación

Ejemplo:

Actualizar un expediente.

```
Qt

↓

PATCH /escribania/15

↓

Router

↓

Service

↓

Repository

↓

SQLAlchemy

↓

PostgreSQL

↓

Repository

↓

Service

↓

Auditoría

↓

Response

↓

Qt
```

React seguirá exactamente el mismo flujo.

---

# 3.14 Principios fundamentales

Todo el Backend se construirá siguiendo estos principios:

• Una única lógica de negocio.

• Una única autenticación.

• Un único sistema de permisos.

• Una única auditoría.

• Una única base de datos.

• Un único Backend.

• Clientes completamente desacoplados.

Este enfoque garantiza que cualquier mejora realizada en el Backend beneficie automáticamente tanto a la aplicación de escritorio como a la aplicación web, evitando duplicación de código y reduciendo significativamente los costos de mantenimiento a largo plazo.
