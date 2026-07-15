
# Capítulo 6

# Arquitectura de la Aplicación Web (React + Vite)

---

# Objetivo

La aplicación web será el cliente universal del sistema.

Permitirá acceder desde cualquier computadora, notebook, tablet o dispositivo autorizado mediante un navegador web.

Toda la lógica del negocio permanecerá centralizada en FastAPI.

React será únicamente la interfaz de usuario.

---

# Filosofía

La aplicación web será un cliente del sistema.

Nunca contendrá reglas de negocio.

React

↓

API REST (FastAPI)

↓

Services

↓

Repositories

↓

PostgreSQL

---

# Organización del proyecto

```text
frontend/

src/

    api/
    components/
    hooks/
    layouts/
    pages/
    routes/
    services/
    store/
    styles/
    templates/
    types/
    utils/

public/

vite.config.ts
```

Cada carpeta tendrá una única responsabilidad.

---

# Estructura de páginas

Las páginas representan únicamente vistas completas.

Ejemplo

```text
pages/

Login

Dashboard

Usuarios

Consultas

Reportes

Configuracion

Auditoria
```

Las páginas no contendrán lógica de negocio.

---

# Componentes reutilizables

Todo elemento repetido será un componente.

Ejemplo

```text
components/

BotonGuardar

BotonEliminar

TablaResultados

SelectorBase

SelectorEstado

SelectorFecha

ModalConfirmacion

Loader

Paginacion

BusquedaGlobal
```

Nunca se duplicará código.

---

# Layouts

Los Layouts administran la estructura visual.

Ejemplo

```text
MainLayout

↓

Header

Sidebar

Workspace

Footer
```

Las páginas se renderizan dentro del Workspace.

---

# Navegación

La navegación utilizará React Router.

Ejemplo

```text
/

↓

Login

↓

Dashboard

↓

Usuarios

↓

Consultas

↓

Reportes
```

Todas las rutas privadas estarán protegidas.

---

# Protección de rutas

Cada ruta verificará el JWT antes de cargar.

```text
Login

↓

JWT válido

↓

PrivateRoute

↓

Página
```

Si el token expiró

↓

Login nuevamente

---

# Comunicación con el Backend

Todo acceso se realizará mediante Axios.

Nunca directamente desde un componente.

Ejemplo

Incorrecto

```text
Componente

↓

Axios
```

Correcto

```text
Componente

↓

UsuarioService

↓

Axios

↓

FastAPI
```

---

# Organización de API

```text
api/

auth.ts

usuarios.ts

consultas.ts

reportes.ts

dashboard.ts
```

Cada archivo contendrá únicamente llamadas HTTP.

---

# Services Frontend

Los Services encapsulan llamadas a la API.

Ejemplo

```text
UsuarioService

↓

obtenerUsuarios()

crearUsuario()

editarUsuario()

eliminarUsuario()
```

Los componentes nunca conocerán URLs.

---

# Manejo del estado

El estado global contendrá únicamente información compartida.

Ejemplo

Usuario autenticado

Token

Permisos

Tema

Configuración

Organismo seleccionado

Nunca almacenará resultados enormes de consultas.

---

# Estado local

Cada componente administrará únicamente su información temporal.

Ejemplo

Formulario

Modal abierto

Página actual

Texto de búsqueda

Filtros

---

# Plantillas dinámicas

El sistema mantendrá el mismo concepto existente en Qt.

Cada organismo tendrá su propia plantilla.

Ejemplo

```text
templates/

Escribania

IPS

IGPJ

Maternidad

Pediatrico
```

Cada plantilla utilizará el mismo modelo visual que la versión de escritorio.

---

# Sistema de pestañas

La aplicación web también utilizará pestañas dinámicas.

Ejemplo

```text
Workspace

├── Escribanía

├── IPS

├── Reporte

├── Usuarios
```

Cada pestaña será independiente.

No se abrirán duplicadas.

---

# Flujo de búsqueda

Usuario

↓

Selecciona organismo

↓

Ingresa criterio

↓

Consulta API

↓

Service

↓

Repository

↓

PostgreSQL

↓

Resultados

↓

Renderizar plantilla correspondiente

---

# Paginación

Las consultas grandes nunca traerán todos los registros.

Siempre utilizarán

page

limit

offset

total

El backend devolverá únicamente la página solicitada.

---

# Filtros

Todos los filtros serán enviados al backend.

Ejemplo

Organismo

Estado

Caja

Fechas

Texto

El frontend nunca filtrará grandes cantidades de datos.

---

# Renderizado

React solamente mostrará información.

Nunca transformará reglas del negocio.

---

# Manejo de errores

Los errores del backend serán traducidos a mensajes amigables.

Ejemplo

```text
No fue posible guardar el registro.

Intente nuevamente.
```

Nunca se mostrarán errores internos del servidor.

---

# Seguridad

Toda autorización será realizada por FastAPI.

React solamente ocultará opciones visuales.

Ejemplo

Si el usuario no posee permiso para eliminar

↓

No aparece el botón

Pero igualmente

↓

FastAPI vuelve a validar el permiso.

---

# Autenticación

Proceso

```text
Login

↓

JWT

↓

Local Storage (o cookie segura)

↓

Interceptor Axios

↓

Authorization Bearer
```

Toda petición viajará autenticada.

---

# Actualización automática

Cuando un registro cambia

↓

Actualizar solamente ese registro

No volver a consultar toda la tabla.

Esto mejora notablemente el rendimiento.

---

# Diseño Responsivo

El sistema deberá funcionar correctamente en

Computadoras

Notebooks

Tablets

Pantallas grandes

No será necesario replicar toda la funcionalidad para teléfonos móviles, aunque las pantallas deberán adaptarse correctamente.

---

# Tema visual

Se utilizará un sistema de temas centralizado.

Ejemplo

Claro

Oscuro

Corporativo

Los colores nunca estarán escritos directamente en los componentes.

---

# Rendimiento

Se utilizarán

Lazy Loading

Code Splitting

Memoización

Componentes reutilizables

Carga diferida

Paginación

Virtualización cuando sea necesaria

---

# Beneficios

✔ Código organizado.

✔ Componentes reutilizables.

✔ Navegación rápida.

✔ Fácil mantenimiento.

✔ Alta escalabilidad.

✔ Misma lógica que Qt.

✔ Misma API.

✔ Misma Base de Datos.

✔ Misma Seguridad.

---

# Resultado Final

La aplicación React será un cliente web moderno, ligero y escalable que compartirá exactamente el mismo backend, las mismas reglas de negocio y la misma base de datos que la aplicación de escritorio.

Ambos clientes ofrecerán una experiencia consistente al usuario, diferenciándose únicamente por su interfaz y el entorno desde el cual son utilizados.
