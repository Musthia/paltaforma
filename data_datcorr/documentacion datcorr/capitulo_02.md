
# CAPÍTULO 2

# Arquitectura General del Sistema

## Objetivo

El objetivo principal del proyecto es disponer de **un único sistema**, independientemente del medio desde el cual el usuario acceda.

El sistema estará compuesto por dos clientes diferentes:

* Aplicación de escritorio (Qt/PySide6)
* Aplicación Web (React)

Ambos consumirán exactamente los mismos servicios del backend.

La lógica de negocio existirá solamente una vez.

---

# Filosofía del proyecto

El sistema debe cumplir el siguiente principio:

> **Todo dato se guarda una única vez y toda regla de negocio existe una única vez.**

Ningún cliente (Desktop o Web) debe implementar reglas de negocio propias.

Los clientes únicamente:

* muestran información;
* solicitan información;
* envían operaciones al servidor.

Toda decisión pertenece al Backend.

---

# Arquitectura General

```
                ┌───────────────────────────────┐
                │        PostgreSQL             │
                │        Base única             │
                └──────────────┬────────────────┘
                               │
                               │ SQLAlchemy
                               │
                ┌──────────────▼────────────────┐
                │        FastAPI Backend        │
                │-------------------------------│
                │ Auth                          │
                │ Usuarios                      │
                │ Permisos                      │
                │ Consultas                     │
                │ Reportes                      │
                │ Auditoría                     │
                │ Inventario                    │
                │ Estadísticas                  │
                └──────────────┬────────────────┘
                               │
                REST API       │
                               │
         ┌─────────────────────┴─────────────────────┐
         │                                           │
         │                                           │
┌────────▼──────────┐                    ┌───────────▼──────────┐
│ Cliente Desktop   │                    │ Cliente React        │
│ PySide6           │                    │ Navegador            │
└───────────────────┘                    └──────────────────────┘
```

---

# Componentes

El sistema posee únicamente tres capas.

## Capa de Datos

PostgreSQL.

Es la única fuente de verdad.

Toda la información reside allí.

Nunca existirán dos bases sincronizadas.

Nunca habrá tablas espejo.

Nunca existirán datos locales persistentes.

---

## Capa de Negocio

FastAPI.

Aquí vive absolutamente toda la lógica.

Esta capa decide:

* quién puede acceder
* quién puede modificar
* cómo se modifica
* auditoría
* permisos
* validaciones
* reglas

Toda operación pasa obligatoriamente por FastAPI.

---

## Capa Cliente

Existen dos clientes.

### Cliente Desktop

Responsable únicamente de:

* mostrar ventanas
* mostrar tablas
* capturar datos
* enviar solicitudes HTTP

No contiene reglas.

No accede directamente a PostgreSQL.

---

### Cliente React

Responsable únicamente de:

* renderizar interfaces
* consumir API REST
* mostrar resultados

No contiene lógica de negocio.

---

# Comunicación

Toda comunicación será HTTP.

Desktop:

```
Qt
↓

Services

↓

Requests

↓

FastAPI
```

React:

```
React

↓

Axios

↓

FastAPI
```

No existe comunicación directa con PostgreSQL.

---

# Capas internas del Backend

El Backend estará dividido en módulos.

```
Routers

↓

Services

↓

Repositories

↓

Models

↓

PostgreSQL
```

Cada módulo tiene una responsabilidad única.

---

## Routers

Reciben solicitudes HTTP.

No contienen lógica.

Únicamente:

* reciben datos
* validan esquemas
* llaman Services
* devuelven respuestas

---

## Services

Aquí vive la lógica del negocio.

Ejemplos:

* crear usuario
* validar permisos
* registrar auditoría
* generar reporte
* aprobar solicitud

Toda decisión pertenece a esta capa.

---

## Repositories

Únicamente hablan con PostgreSQL.

No conocen reglas.

Sólo saben:

* buscar
* insertar
* actualizar
* eliminar

---

## Models

Representan tablas.

Nunca contienen lógica.

---

# Flujo de una operación

Ejemplo:

Editar Usuario

```
Qt

↓

PATCH /usuarios/15

↓

Router

↓

UsuarioService

↓

UsuarioRepository

↓

PostgreSQL

↓

Repository

↓

Service

↓

Router

↓

Qt
```

React realiza exactamente el mismo recorrido.

---

# Ventajas

Esta arquitectura aporta:

* una única lógica
* una única base
* un único mantenimiento
* una única auditoría
* un único sistema de permisos
* clientes completamente independientes

---

# Escalabilidad

Si en el futuro aparece un tercer cliente:

* aplicación Android
* aplicación iOS
* aplicación móvil Flutter
* aplicación Electron

No será necesario modificar PostgreSQL.

No será necesario modificar la lógica.

Sólo deberá consumir la API.

---

# Beneficios a largo plazo

Esta arquitectura garantiza:

* consistencia de datos;
* ausencia de duplicación;
* menor mantenimiento;
* crecimiento controlado;
* reutilización completa del Backend;
* independencia entre interfaces;
* posibilidad de desplegar múltiples clientes simultáneamente.

Con esta estructura, el Backend se convierte en el verdadero núcleo del sistema, mientras que las interfaces de usuario pasan a ser únicamente distintas formas de interactuar con él.
