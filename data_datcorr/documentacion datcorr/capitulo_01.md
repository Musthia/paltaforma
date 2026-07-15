
# DATCORR

## Documento Maestro de Arquitectura del Sistema

# Capítulo 1 – Introducción

---

# 1.1 Objetivo General

DATCORR (Sistema Integral de Gestión Documental) es una plataforma destinada a la administración integral de documentación física y digital perteneciente a distintos organismos, permitiendo registrar, localizar, consultar, administrar y auditar expedientes, legajos, cajas y demás unidades documentales almacenadas.

El sistema busca reemplazar procedimientos manuales por una solución centralizada, segura, escalable y completamente auditable, capaz de operar simultáneamente desde aplicaciones de escritorio y aplicaciones web utilizando una única base de datos y una única lógica de negocio.

El objetivo principal consiste en garantizar que toda la información documental pueda ser localizada, administrada y consultada de forma rápida, segura y consistente desde cualquier cliente autorizado.

---

# 1.2 Alcance del Sistema

DATCORR fue diseñado para administrar múltiples organismos dentro de una misma plataforma.

Cada organismo posee su propio conjunto de datos, completamente independiente del resto, manteniendo sin embargo una arquitectura común y compartiendo el mismo motor de funcionamiento.

Entre los organismos actualmente contemplados se encuentran:

* Escribanía
* IPS
* IGPJ
* Pediátrico
* Maternidad

La arquitectura permite incorporar nuevos organismos sin modificar el funcionamiento del sistema, simplemente agregando un nuevo esquema en PostgreSQL y los componentes de acceso correspondientes.

El sistema contempla, entre otras, las siguientes funcionalidades:

* Administración de usuarios.
* Administración de permisos.
* Gestión documental.
* Consultas generales.
* Consultas avanzadas.
* Inventario documental.
* Administración de préstamos.
* Registro de movimientos.
* Auditoría completa.
* Reportes.
* Exportación de información.
* Administración mediante aplicación de escritorio.
* Administración mediante aplicación web.

---

# 1.3 Problema que Resuelve

En numerosos organismos públicos y privados, la documentación continúa administrándose mediante registros dispersos, planillas, archivos físicos y sistemas independientes.

Esta situación genera inconvenientes tales como:

* Dificultad para localizar documentación.
* Duplicación de información.
* Falta de trazabilidad.
* Pérdida de historial.
* Escasa auditoría.
* Procesos manuales lentos.
* Dependencia de conocimiento humano.
* Inconsistencia entre distintos sistemas.

DATCORR unifica toda la información documental en una única plataforma centralizada, eliminando duplicidades y garantizando consistencia en todos los procesos.

---

# 1.4 Filosofía del Proyecto

DATCORR se construye bajo un conjunto de principios arquitectónicos que gobiernan todas las decisiones de diseño.

## Una única fuente de verdad

Toda la información oficial reside exclusivamente en PostgreSQL.

No existen bases de datos locales utilizadas para almacenar información operativa.

## Un único Backend

Toda la lógica del negocio reside exclusivamente en FastAPI.

Ningún cliente implementa reglas de negocio propias.

## Clientes livianos

Las aplicaciones cliente (Qt y React) solamente presentan información y envían solicitudes al backend.

Nunca realizan operaciones directas sobre la base de datos.

## Separación de responsabilidades

Cada componente posee una responsabilidad claramente definida.

* Interfaces
* Servicios
* Repositories
* Base de datos

Cada capa conoce únicamente la inmediatamente inferior.

## Escalabilidad

Toda funcionalidad nueva deberá poder incorporarse sin modificar la arquitectura existente.

---

# 1.5 Arquitectura General

DATCORR adopta una arquitectura cliente-servidor multicapa.

La plataforma está compuesta por cuatro niveles claramente diferenciados:

## Cliente Desktop

Aplicación desarrollada con Qt (PySide6).

Orientada a operadores internos que requieren máxima productividad y acceso intensivo a información.

## Cliente Web

Aplicación desarrollada con React.

Permite acceder al sistema desde cualquier ubicación utilizando un navegador.

## Backend

Desarrollado con FastAPI.

Concentra absolutamente toda la lógica del negocio, autenticación, autorización, auditoría y acceso a datos.

## Base de Datos

PostgreSQL constituye la única fuente oficial de información.

Cada organismo es representado mediante un esquema independiente.

---

# 1.6 Principios de Diseño

Toda implementación del sistema deberá respetar los siguientes principios:

* Una única fuente de verdad.
* Un único backend.
* Clientes sin lógica de negocio.
* Auditoría completa.
* Reutilización de componentes.
* Separación estricta de responsabilidades.
* Seguridad por defecto.
* Escalabilidad.
* Modularidad.
* Bajo acoplamiento.
* Alta cohesión.

---

# 1.7 Tecnologías

Actualmente el sistema utiliza las siguientes tecnologías:

## Backend

* Python
* FastAPI
* SQLAlchemy
* PostgreSQL
* JWT
* Passlib
* Alembic (previsto)

## Desktop

* PySide6
* Qt Designer

## Web

* React
* TypeScript
* Vite
* Axios

## Base de Datos

* PostgreSQL

## Control de versiones

* Git
* GitHub

---

# 1.8 Organización General del Proyecto

La arquitectura lógica del proyecto se organiza en módulos independientes.

Cada módulo implementa una única responsabilidad.

Los principales módulos son:

* Autenticación.
* Usuarios.
* Permisos.
* Auditoría.
* Consultas.
* Inventario.
* Reportes.
* Configuración.
* Organismos documentales.
* Exportación.

Esta organización permite incorporar nuevas funcionalidades sin afectar los módulos existentes.

---

# 1.9 Flujo General de una Operación

Toda operación realizada por un usuario sigue el mismo recorrido lógico:

1. El usuario interactúa con la interfaz (Qt o React).
2. La interfaz envía una solicitud al Backend.
3. El Backend valida autenticación y permisos.
4. El Servicio correspondiente aplica las reglas de negocio.
5. El Repository accede a PostgreSQL.
6. PostgreSQL devuelve la información.
7. El Backend registra la auditoría.
8. La respuesta retorna al cliente.

Este flujo garantiza consistencia entre todos los clientes y asegura que ninguna operación pueda ejecutarse omitiendo las reglas de negocio.

---

# 1.10 Evolución Prevista

La arquitectura de DATCORR fue concebida para permitir su crecimiento durante muchos años.

Entre las funcionalidades previstas se encuentran:

* Incorporación de nuevos organismos.
* Gestión documental digital.
* Firma digital.
* Integración con servicios externos.
* API pública controlada.
* Aplicación móvil.
* Paneles estadísticos.
* Reportes inteligentes.
* Automatización de procesos.
* Notificaciones.
* Integración con sistemas institucionales.

Todas estas mejoras podrán incorporarse sin alterar la arquitectura fundamental del sistema.
