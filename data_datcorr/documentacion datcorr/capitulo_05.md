
# Capítulo 5

# Arquitectura de la Aplicación de Escritorio (Qt / PySide6)

---

# Objetivo

La aplicación de escritorio continuará existiendo como cliente principal para operadores internos.

Su objetivo será ofrecer una interfaz rápida, cómoda y optimizada para el trabajo intensivo sobre grandes volúmenes de información.

Toda la lógica de negocio residirá en los Services del backend compartido.

La interfaz Qt nunca implementará reglas de negocio.

---

# Filosofía

La aplicación Qt será un cliente del sistema.

No será "el sistema".

Qt

↓

Services

↓

Repositories

↓

PostgreSQL

La interfaz únicamente:

* muestra información
* captura datos
* envía solicitudes
* recibe respuestas

Nunca decidirá cómo funciona el negocio.

---

# Organización del proyecto

```text
ui/
    dialogs/
    widgets/
    templates/
    tabs/
    main_window/

ventanas/

services/

repositories/

database/

utils/

resources/
```

Cada carpeta tendrá una responsabilidad única.

---

# Ventana Principal

La Ventana Principal actuará como contenedor.

Será responsable únicamente de:

* iniciar sesión
* mostrar menú
* administrar pestañas
* administrar barra de herramientas
* administrar barra de estado

No realizará consultas SQL.

No modificará registros.

No conocerá tablas.

---

# Flujo general

Usuario

↓

Ventana Principal

↓

Service correspondiente

↓

Repository

↓

PostgreSQL

↓

Resultado

↓

Actualizar interfaz

---

# Componentes principales

La aplicación estará dividida en módulos independientes.

Ejemplo:

* Usuarios
* Consultas
* Reportes
* Administración
* Configuración
* Auditoría

Cada módulo será completamente independiente.

---

# Ventanas

Cada ventana tendrá una única responsabilidad.

Ejemplo:

VentanaUsuarios

* listar usuarios
* abrir editor

No actualizar usuarios.

No eliminar usuarios.

Eso pertenece al Service.

---

VentanaEditarUsuario

Responsabilidad:

* mostrar datos
* capturar modificaciones

Cuando el usuario pulsa Guardar:

```text
VentanaEditarUsuario

↓

UsuarioService.actualizar_usuario()

↓

Resultado

↓

Cerrar ventana
```

Nunca ejecutará SQL.

---

# Widgets reutilizables

Se crearán componentes reutilizables.

Ejemplos:

Buscador

TablaResultados

SelectorBase

SelectorFechas

SelectorEstado

BarraAcciones

Esto evitará duplicar código.

---

# Pestañas dinámicas

La aplicación mantendrá el sistema actual de pestañas.

Cada búsqueda genera una pestaña.

Ejemplo

```text
Principal

├── Escribanía
├── IPS
├── IGPJ
├── Pediátrico
├── Reporte 1
└── Reporte 2
```

Cada pestaña será completamente independiente.

---

# Plantillas

Cada organismo tendrá su propia plantilla.

Ejemplo

```text
PlantillaEscribania

PlantillaIPS

PlantillaIGPJ

PlantillaMaternidad

PlantillaPediatrico
```

Todas heredarán de una plantilla base.

```text
BaseTemplate

↓

PlantillaEscribania

↓

PlantillaIPS

↓

PlantillaIGPJ
```

Esto permitirá reutilizar casi toda la lógica visual.

---

# Comunicación con Services

La UI nunca hablará con PostgreSQL.

Siempre utilizará Services.

Ejemplo

Incorrecto

```text
Qt

↓

SQL
```

Correcto

```text
Qt

↓

EscribaniaService.buscar()

↓

Repository

↓

PostgreSQL
```

---

# Estado de la aplicación

La Ventana Principal mantendrá únicamente información temporal.

Ejemplo

Usuario autenticado

Organismo seleccionado

Pestañas abiertas

Filtros activos

Nunca almacenará información persistente.

---

# Actualización automática

Cuando una ventana modifica información:

```text
Editar Registro

↓

Guardar

↓

Service

↓

Repository

↓

Commit

↓

Actualizar pestaña actual
```

No será necesario volver a ejecutar la búsqueda completa.

---

# Señales Qt

La comunicación entre ventanas utilizará señales.

Ejemplo

```text
registroActualizado()

↓

Ventana Principal

↓

Actualizar tabla
```

Esto desacopla completamente las ventanas.

---

# Gestión de recursos

Todos los recursos estarán centralizados.

```text
resources/

icons/

images/

fonts/

styles/

translations/
```

Nunca se utilizarán rutas absolutas.

---

# Configuración

Toda configuración estará fuera del código.

Ejemplo

```text
config/

config.ini

settings.json

.env
```

La aplicación podrá cambiar configuraciones sin recompilar.

---

# Manejo de errores

La UI nunca mostrará Tracebacks.

Los errores serán registrados mediante logging.

El usuario verá únicamente mensajes comprensibles.

Ejemplo

```text
No fue posible guardar el registro.

Consulte el administrador.
```

---

# Rendimiento

La UI nunca cargará miles de registros innecesariamente.

Se implementará:

* paginación
* carga diferida (Lazy Loading)
* actualización parcial
* búsqueda incremental

Esto permitirá trabajar con millones de registros.

---

# Seguridad

La UI nunca decidirá permisos.

Siempre preguntará al Service.

Ejemplo

```text
if validar_permiso("usuarios.editar"):
    abrir_editor()
```

Los permisos reales serán verificados nuevamente en el backend.

---

# Beneficios

✔ Interfaz limpia.

✔ Sin SQL.

✔ Sin lógica duplicada.

✔ Muy rápida.

✔ Fácil mantenimiento.

✔ Componentes reutilizables.

✔ Compatible con futuras versiones.

✔ Mismo comportamiento que la aplicación web.

---

# Resultado final

La aplicación de escritorio será un cliente especializado para operadores internos, optimizado para productividad y grandes volúmenes de información.

Toda la lógica del negocio permanecerá centralizada en la capa de Services y Repositories compartida con la aplicación web, garantizando que ambos clientes trabajen exactamente sobre las mismas reglas y la misma base de datos.
