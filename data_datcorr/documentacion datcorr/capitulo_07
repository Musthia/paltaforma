# Capítulo 7

# Arquitectura de la Base de Datos PostgreSQL

---

# Objetivo

La Base de Datos PostgreSQL constituye el núcleo del sistema.

Toda la información será almacenada en una única base de datos denominada:

```text
datcorr
```

Ningún cliente (Qt o React) accederá directamente a los datos sin pasar por FastAPI.

---

# Filosofía

Existe una única fuente de verdad.

```text
Qt Desktop

        │

        │

React Web

        │

        ▼

FastAPI

        │

        ▼

PostgreSQL
```

Toda modificación realizada desde cualquier cliente será inmediatamente visible para el resto.

---

# Principios

La arquitectura de la base deberá cumplir:

* Una sola base de datos.
* Sin duplicación de información.
* Esquemas independientes por organismo.
* Tablas comunes compartidas.
* Integridad referencial.
* Escalabilidad.
* Alto rendimiento.
* Facilidad para incorporar nuevos organismos.

---

# Base principal

```text
datcorr
```

Dentro de ella existirán múltiples esquemas.

---

# Organización por esquemas

Cada organismo será completamente independiente.

Ejemplo

```text
public

usuarios

permisos

usuarios_permisos

refresh_tokens

token_blacklist

auditoria

--------------------------------

escribania

Datcorr_database

--------------------------------

ips

Datcorr_database

--------------------------------

igpj

Datcorr_database

--------------------------------

maternidad

Datcorr_database

--------------------------------

pediatrico

Datcorr_database

--------------------------------

...
```

La incorporación de un nuevo organismo consistirá únicamente en crear un nuevo esquema.

---

# Tablas comunes

Las tablas comunes vivirán únicamente en **public**.

Ejemplo

```text
usuarios

permisos

usuarios_permisos

refresh_tokens

token_blacklist

auditoria
```

Estas tablas nunca deberán duplicarse.

---

# Esquemas de organismos

Cada organismo posee exactamente una tabla principal.

Ejemplo

```text
escribania.Datcorr_database

ips.Datcorr_database

igpj.Datcorr_database

maternidad.Datcorr_database

pediatrico.Datcorr_database
```

La estructura podrá variar según el organismo.

---

# Independencia estructural

No se obligará a que todas las tablas tengan las mismas columnas.

Ejemplo

Escribanía puede tener

```text
localidad

legajo

timbrado_fiscal
```

Mientras IPS posee

```text
expediente

documento

caratula
```

El sistema deberá adaptarse dinámicamente.

---

# Identificador principal

Cada tabla tendrá una clave primaria propia.

Ejemplo

```text
id_Datcorr_database
```

Nunca se reutilizarán IDs entre organismos.

---

# Integridad

Cada tabla tendrá:

Primary Key

Not Null cuando corresponda

Índices

Restricciones UNIQUE

Valores válidos

---

# Índices

Las búsquedas frecuentes deberán poseer índices.

Ejemplo

```text
registro

caja

documento

expediente

nombre_apellido

estado
```

Esto mejora considerablemente el rendimiento.

---

# Restricciones

Ejemplo

Usuarios

```text
usuario UNIQUE
```

Permisos

```text
(nombre UNIQUE)
```

Refresh Tokens

```text
jti UNIQUE
```

No se permitirá información duplicada.

---

# Auditoría

Toda modificación importante será registrada.

Ejemplo

```text
Usuario

Fecha

Acción

Tabla

Registro

Detalle

IP

Cliente

Resultado
```

Ninguna operación crítica quedará sin registrar.

---

# Soft Delete

Siempre que sea posible se utilizará eliminación lógica.

Ejemplo

```text
activo = FALSE
```

En lugar de

```text
DELETE
```

Esto preserva el historial.

---

# Fechas

Toda tabla importante deberá registrar

```text
fecha_creacion

fecha_actualizacion
```

Actualizadas automáticamente.

---

# Usuario responsable

Cuando corresponda

```text
usuario_creacion

usuario_modificacion
```

Permitirá conocer quién realizó cada cambio.

---

# Relaciones

Las relaciones existirán únicamente cuando sean necesarias.

Ejemplo

```text
usuarios

↓

usuarios_permisos

↓

permisos
```

No se crearán relaciones innecesarias.

---

# Versionado

La estructura será administrada mediante migraciones.

Nunca modificando manualmente la base en producción.

---

# Migraciones

Durante el desarrollo se utilizarán modelos SQLAlchemy.

La carga definitiva de datos reales se realizará únicamente al final mediante los scripts existentes.

Ejemplo

```text
migrate_escribania.py

migrate_ips.py

migrate_igpj.py

migrate_maternidad.py

migrate_pediatrico.py
```

Esto garantiza que los datos reales sean incorporados una única vez y sobre una estructura ya estable.

---

# Escalabilidad

Agregar un organismo nuevo implicará únicamente:

1.

Crear un esquema.

2.

Crear su modelo SQLAlchemy.

3.

Crear su Repository.

4.

Crear su Service.

5.

Registrar el organismo.

No será necesario modificar el resto del sistema.

---

# Independencia del Cliente

La base nunca sabrá si el dato proviene de

Qt

o

React

La única capa autorizada será FastAPI.

---

# Flujo completo

```text
Qt

↓

FastAPI

↓

Service

↓

Repository

↓

Schema PostgreSQL

↓

Tabla correspondiente

↓

Respuesta

↓

Qt
```

o bien

```text
React

↓

FastAPI

↓

Service

↓

Repository

↓

Schema PostgreSQL

↓

Tabla correspondiente

↓

Respuesta

↓

React
```

El recorrido será exactamente el mismo.

---

# Organización del código

Los modelos seguirán la estructura

```text
database/

modelos/

    usuario.py

    permiso.py

    auditoria.py

    refresh_token.py

    token_blacklist.py

    escribania.py

    ips.py

    igpj.py

    maternidad.py

    pediatrico.py

    __init__.py
```

Cada archivo contendrá únicamente un modelo.

---

# Beneficios

✔ Una sola base.

✔ Un solo origen de información.

✔ Esquemas completamente independientes.

✔ Fácil incorporación de nuevos organismos.

✔ Máximo rendimiento.

✔ Alta seguridad.

✔ Excelente mantenibilidad.

✔ Compatible con Qt y React simultáneamente.

✔ Preparada para crecimiento futuro.

---

# Resultado Final

PostgreSQL se convierte en el repositorio central del sistema. Los datos se organizan por esquemas independientes para cada organismo y por tablas comunes compartidas para autenticación, permisos y auditoría. Esta arquitectura permite que múltiples clientes trabajen de forma simultánea sobre la misma información, manteniendo integridad, rendimiento, seguridad y una elevada capacidad de expansión.
