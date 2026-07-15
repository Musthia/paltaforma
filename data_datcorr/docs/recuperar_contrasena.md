# Rediseñar la tabla `usuarios`

Como estamos todavía en una etapa temprana del proyecto, creo que conviene dejarla preparada para varios años.

Pensando en seguridad.

## Tabla `usuarios`

| Campo                  | Obligatorio | Descripción                  |
| ---------------------- | ----------- | ----------------------------- |
| id                     | Sí         | PK                            |
| usuario                | Sí         | Nombre de usuario único      |
| email                  | Sí         | Correo único                 |
| password_hash          | Sí         | Contraseña cifrada           |
| nombre                 | Sí         | Nombre                        |
| apellido               | Sí         | Apellido                      |
| rol_id                 | Sí         | Rol del usuario               |
| activo                 | Sí         | Usuario habilitado            |
| fecha_creacion         | Sí         | Alta                          |
| ultimo_login           | No          | Último acceso                |
| ultimo_cambio_password | Sí         | Último cambio de contraseña |

---

# Restricciones

Agregar inmediatamente.

<pre class="overflow-visible! px-0!" data-start="1237" data-end="1263"><div class="relative w-full mt-4 mb-1"><div class=""><div class="contents"><div class="relative"><div class="h-full min-h-0 min-w-0"><div class="h-full min-h-0 min-w-0"><div class="border border-token-border-light border-radius-3xl corner-superellipse/1.1 rounded-3xl"><div class="h-full w-full border-radius-3xl bg-(--code-block-surface) corner-superellipse/1.1 overflow-clip rounded-3xl [--code-block-surface:var(--bg-elevated-secondary)] dark:[--code-block-surface:var(--composer-surface-primary)] lxnfua_clipPathFallback"><div class="pointer-events-none absolute end-1.5 top-1 z-2 md:end-2 md:top-1"></div><div class="relative"><div class="pe-11 pt-3"><div class="relative z-0 flex max-w-full"><div id="code-block-viewer" dir="ltr" class="q9tKkq_viewer cm-editor z-10 light:cm-light dark:cm-light flex h-full w-full flex-col items-stretch ͼs ͼ16"><div class="cm-scroller"><pre class="cm-content q9tKkq_readonly m-0"><code><span>usuario UNIQUE</span></code></pre></div></div></div></div></div></div></div></div></div><div class=""><div class=""></div></div></div></div></div></div></pre>

<pre class="overflow-visible! px-0!" data-start="1265" data-end="1289"><div class="relative w-full mt-4 mb-1"><div class=""><div class="contents"><div class="relative"><div class="h-full min-h-0 min-w-0"><div class="h-full min-h-0 min-w-0"><div class="border border-token-border-light border-radius-3xl corner-superellipse/1.1 rounded-3xl"><div class="h-full w-full border-radius-3xl bg-(--code-block-surface) corner-superellipse/1.1 overflow-clip rounded-3xl [--code-block-surface:var(--bg-elevated-secondary)] dark:[--code-block-surface:var(--composer-surface-primary)] lxnfua_clipPathFallback"><div class="pointer-events-none absolute end-1.5 top-1 z-2 md:end-2 md:top-1"></div><div class="relative"><div class="pe-11 pt-3"><div class="relative z-0 flex max-w-full"><div id="code-block-viewer" dir="ltr" class="q9tKkq_viewer cm-editor z-10 light:cm-light dark:cm-light flex h-full w-full flex-col items-stretch ͼs ͼ16"><div class="cm-scroller"><pre class="cm-content q9tKkq_readonly m-0"><code><span>email UNIQUE</span></code></pre></div></div></div></div></div></div></div></div></div><div class=""><div class=""></div></div></div></div></div></div></pre>

No pueden existir dos usuarios con el mismo correo.

---

# El correo será obligatorio

No permitiría registrar un usuario sin correo.

---

# Validación

En el formulario de alta.

El sistema verificará.

✓ formato correcto

<pre class="overflow-visible! px-0!" data-start="1599" data-end="1630"><div class="relative w-full mt-4 mb-1"><div class=""><div class="contents"><div class="relative"><div class="h-full min-h-0 min-w-0"><div class="h-full min-h-0 min-w-0"><div class="border border-token-border-light border-radius-3xl corner-superellipse/1.1 rounded-3xl"><div class="h-full w-full border-radius-3xl bg-(--code-block-surface) corner-superellipse/1.1 overflow-clip rounded-3xl [--code-block-surface:var(--bg-elevated-secondary)] dark:[--code-block-surface:var(--composer-surface-primary)] lxnfua_clipPathFallback"><div class="pointer-events-none absolute end-1.5 top-1 z-2 md:end-2 md:top-1"></div><div class="relative"><div class="pe-11 pt-3"><div class="relative z-0 flex max-w-full"><div id="code-block-viewer" dir="ltr" class="q9tKkq_viewer cm-editor z-10 light:cm-light dark:cm-light flex h-full w-full flex-col items-stretch ͼs ͼ16"><div class="cm-scroller"><pre class="cm-content q9tKkq_readonly m-0"><code><span>usuario@empresa.com</span></code></pre></div></div></div></div></div></div></div></div></div><div class=""><div class=""></div></div></div></div></div></div></pre>

✓ que no exista.

---

# ¿Modificar la contraseña?

Cuando el usuario cambie la contraseña.

Actualizaríamos.

<pre class="overflow-visible! px-0!" data-start="1743" data-end="1777"><div class="relative w-full mt-4 mb-1"><div class=""><div class="contents"><div class="relative"><div class="h-full min-h-0 min-w-0"><div class="h-full min-h-0 min-w-0"><div class="border border-token-border-light border-radius-3xl corner-superellipse/1.1 rounded-3xl"><div class="h-full w-full border-radius-3xl bg-(--code-block-surface) corner-superellipse/1.1 overflow-clip rounded-3xl [--code-block-surface:var(--bg-elevated-secondary)] dark:[--code-block-surface:var(--composer-surface-primary)] lxnfua_clipPathFallback"><div class="pointer-events-none absolute end-1.5 top-1 z-2 md:end-2 md:top-1"></div><div class="relative"><div class="pe-11 pt-3"><div class="relative z-0 flex max-w-full"><div id="code-block-viewer" dir="ltr" class="q9tKkq_viewer cm-editor z-10 light:cm-light dark:cm-light flex h-full w-full flex-col items-stretch ͼs ͼ16"><div class="cm-scroller"><pre class="cm-content q9tKkq_readonly m-0"><code><span>ultimo_cambio_password</span></code></pre></div></div></div></div></div></div></div></div></div><div class=""><div class=""></div></div></div></div></div></div></pre>

Eso servirá más adelante para políticas como:

> cambiar contraseña cada 90 días.

---

# Recuperación

La tabla `usuarios` NO debería guardar tokens.

Los tokens vivirán en otra tabla.

<pre class="overflow-visible! px-0!" data-start="1966" data-end="1999"><div class="relative w-full mt-4 mb-1"><div class=""><div class="contents"><div class="relative"><div class="h-full min-h-0 min-w-0"><div class="h-full min-h-0 min-w-0"><div class="border border-token-border-light border-radius-3xl corner-superellipse/1.1 rounded-3xl"><div class="h-full w-full border-radius-3xl bg-(--code-block-surface) corner-superellipse/1.1 overflow-clip rounded-3xl [--code-block-surface:var(--bg-elevated-secondary)] dark:[--code-block-surface:var(--composer-surface-primary)] lxnfua_clipPathFallback"><div class="pointer-events-none absolute end-1.5 top-1 z-2 md:end-2 md:top-1"></div><div class="relative"><div class="pe-11 pt-3"><div class="relative z-0 flex max-w-full"><div id="code-block-viewer" dir="ltr" class="q9tKkq_viewer cm-editor z-10 light:cm-light dark:cm-light flex h-full w-full flex-col items-stretch ͼs ͼ16"><div class="cm-scroller"><pre class="cm-content q9tKkq_readonly m-0"><code><span>password_reset_tokens</span></code></pre></div></div></div></div></div></div></div></div></div><div class=""><div class=""></div></div></div></div></div></div></pre>

Así la tabla de usuarios permanece limpia.

---

# Entonces la arquitectura queda

<pre class="overflow-visible! px-0!" data-start="2084" data-end="2104"><div class="relative w-full mt-4 mb-1"><div class=""><div class="contents"><div class="relative"><div class="h-full min-h-0 min-w-0"><div class="h-full min-h-0 min-w-0"><div class="border border-token-border-light border-radius-3xl corner-superellipse/1.1 rounded-3xl"><div class="h-full w-full border-radius-3xl bg-(--code-block-surface) corner-superellipse/1.1 overflow-clip rounded-3xl [--code-block-surface:var(--bg-elevated-secondary)] dark:[--code-block-surface:var(--composer-surface-primary)] lxnfua_clipPathFallback"><div class="pointer-events-none absolute end-1.5 top-1 z-2 md:end-2 md:top-1"></div><div class="relative"><div class="pe-11 pt-3"><div class="relative z-0 flex max-w-full"><div id="code-block-viewer" dir="ltr" class="q9tKkq_viewer cm-editor z-10 light:cm-light dark:cm-light flex h-full w-full flex-col items-stretch ͼs ͼ16"><div class="cm-scroller"><pre class="cm-content q9tKkq_readonly m-0"><code><span>usuarios</span></code></pre></div></div></div></div></div></div></div></div></div><div class=""><div class=""></div></div></div></div></div></div></pre>

↓

Información permanente.

---

<pre class="overflow-visible! px-0!" data-start="2139" data-end="2172"><div class="relative w-full mt-4 mb-1"><div class=""><div class="contents"><div class="relative"><div class="h-full min-h-0 min-w-0"><div class="h-full min-h-0 min-w-0"><div class="border border-token-border-light border-radius-3xl corner-superellipse/1.1 rounded-3xl"><div class="h-full w-full border-radius-3xl bg-(--code-block-surface) corner-superellipse/1.1 overflow-clip rounded-3xl [--code-block-surface:var(--bg-elevated-secondary)] dark:[--code-block-surface:var(--composer-surface-primary)] lxnfua_clipPathFallback"><div class="pointer-events-none absolute end-1.5 top-1 z-2 md:end-2 md:top-1"></div><div class="relative"><div class="pe-11 pt-3"><div class="relative z-0 flex max-w-full"><div id="code-block-viewer" dir="ltr" class="q9tKkq_viewer cm-editor z-10 light:cm-light dark:cm-light flex h-full w-full flex-col items-stretch ͼs ͼ16"><div class="cm-scroller"><pre class="cm-content q9tKkq_readonly m-0"><code><span>password_reset_tokens</span></code></pre></div></div></div></div></div></div></div></div></div><div class=""><div class=""></div></div></div></div></div></div></pre>

↓

Información temporal.

---

# SQL

Si hoy tu tabla tiene solamente.

<pre class="overflow-visible! px-0!" data-start="2246" data-end="2288"><div class="relative w-full mt-4 mb-1"><div class=""><div class="contents"><div class="relative"><div class="h-full min-h-0 min-w-0"><div class="h-full min-h-0 min-w-0"><div class="border border-token-border-light border-radius-3xl corner-superellipse/1.1 rounded-3xl"><div class="h-full w-full border-radius-3xl bg-(--code-block-surface) corner-superellipse/1.1 overflow-clip rounded-3xl [--code-block-surface:var(--bg-elevated-secondary)] dark:[--code-block-surface:var(--composer-surface-primary)] lxnfua_clipPathFallback"><div class="pointer-events-none absolute end-1.5 top-1 z-2 md:end-2 md:top-1"></div><div class="relative"><div class="pe-11 pt-3"><div class="relative z-0 flex max-w-full"><div id="code-block-viewer" dir="ltr" class="q9tKkq_viewer cm-editor z-10 light:cm-light dark:cm-light flex h-full w-full flex-col items-stretch ͼs ͼ16"><div class="cm-scroller"><pre class="cm-content q9tKkq_readonly m-0"><code><span>usuario

password

rol

activo</span></code></pre></div></div></div></div></div></div></div></div></div><div class=""><div class=""></div></div></div></div></div></div></pre>

Agregar primero.

<pre class="overflow-visible! px-0!" data-start="2313" data-end="2382"><div class="relative w-full mt-4 mb-1"><div class=""><div class="contents"><div class="border border-token-border-light border-radius-3xl corner-superellipse/1.1 rounded-3xl"><div class="relative h-full w-full border-radius-3xl bg-(--code-block-surface) corner-superellipse/1.1 overflow-clip rounded-3xl [--code-block-surface:var(--bg-elevated-secondary)] dark:[--code-block-surface:var(--composer-surface-primary)] lxnfua_clipPathFallback"><div class="pointer-events-none absolute inset-x-4 top-12 bottom-4"><div class="pointer-events-none sticky z-40 shrink-0 z-1!"><div class="sticky bg-token-border-light"></div></div></div><div class="relative"><div class="h-full min-h-0 min-w-0"><div class="h-full min-h-0 min-w-0"><div class=""><div class="relative"><div class=""><div class="relative z-0 flex max-w-full"><div id="code-block-viewer" dir="ltr" class="q9tKkq_viewer cm-editor z-10 light:cm-light dark:cm-light flex h-full w-full flex-col items-stretch ͼs ͼ16"><div class="cm-scroller"><pre class="cm-content q9tKkq_readonly m-0"><code><span class="ͼv">ALTER</span><span></span><span class="ͼv">TABLE</span><span> public.usuarios
</span><span class="ͼv">ADD</span><span></span><span class="ͼv">COLUMN</span><span> email </span><span class="ͼ11">VARCHAR</span><span>(</span><span class="ͼy">255</span><span>);</span></code></pre></div></div></div></div></div></div></div></div><div class=""><div class=""></div></div></div></div></div></div></div></div></pre>

Luego.

<pre class="overflow-visible! px-0!" data-start="2392" data-end="2480"><div class="relative w-full mt-4 mb-1"><div class=""><div class="contents"><div class="border border-token-border-light border-radius-3xl corner-superellipse/1.1 rounded-3xl"><div class="relative h-full w-full border-radius-3xl bg-(--code-block-surface) corner-superellipse/1.1 overflow-clip rounded-3xl [--code-block-surface:var(--bg-elevated-secondary)] dark:[--code-block-surface:var(--composer-surface-primary)] lxnfua_clipPathFallback"><div class="pointer-events-none absolute inset-x-4 top-12 bottom-4"><div class="pointer-events-none sticky z-40 shrink-0 z-1!"><div class="sticky bg-token-border-light"></div></div></div><div class="relative"><div class="h-full min-h-0 min-w-0"><div class="h-full min-h-0 min-w-0"><div class=""><div class="relative"><div class=""><div class="relative z-0 flex max-w-full"><div id="code-block-viewer" dir="ltr" class="q9tKkq_viewer cm-editor z-10 light:cm-light dark:cm-light flex h-full w-full flex-col items-stretch ͼs ͼ16"><div class="cm-scroller"><pre class="cm-content q9tKkq_readonly m-0"><code><span class="ͼv">UPDATE</span><span> public.usuarios
</span><span class="ͼv">SET</span><span> email</span><span class="ͼv">=</span><span class="ͼz">'pendiente@empresa.com'</span><span>
</span><span class="ͼv">WHERE</span><span> email </span><span class="ͼv">IS</span><span></span><span class="ͼy">NULL</span><span>;</span></code></pre></div></div></div></div></div></div></div></div><div class=""><div class=""></div></div></div></div></div></div></div></div></pre>

Después.

<pre class="overflow-visible! px-0!" data-start="2492" data-end="2563"><div class="relative w-full mt-4 mb-1"><div class=""><div class="contents"><div class="border border-token-border-light border-radius-3xl corner-superellipse/1.1 rounded-3xl"><div class="relative h-full w-full border-radius-3xl bg-(--code-block-surface) corner-superellipse/1.1 overflow-clip rounded-3xl [--code-block-surface:var(--bg-elevated-secondary)] dark:[--code-block-surface:var(--composer-surface-primary)] lxnfua_clipPathFallback"><div class="pointer-events-none absolute inset-x-4 top-12 bottom-4"><div class="pointer-events-none sticky z-40 shrink-0 z-1!"><div class="sticky bg-token-border-light"></div></div></div><div class="relative"><div class="h-full min-h-0 min-w-0"><div class="h-full min-h-0 min-w-0"><div class=""><div class="relative"><div class=""><div class="relative z-0 flex max-w-full"><div id="code-block-viewer" dir="ltr" class="q9tKkq_viewer cm-editor z-10 light:cm-light dark:cm-light flex h-full w-full flex-col items-stretch ͼs ͼ16"><div class="cm-scroller"><pre class="cm-content q9tKkq_readonly m-0"><code><span class="ͼv">ALTER</span><span></span><span class="ͼv">TABLE</span><span> public.usuarios
</span><span class="ͼv">ALTER</span><span></span><span class="ͼv">COLUMN</span><span> email </span><span class="ͼv">SET</span><span></span><span class="ͼv">NOT</span><span></span><span class="ͼy">NULL</span><span>;</span></code></pre></div></div></div></div></div></div></div></div><div class=""><div class=""></div></div></div></div></div></div></div></div></pre>

Y finalmente.

<pre class="overflow-visible! px-0!" data-start="2580" data-end="2670"><div class="relative w-full mt-4 mb-1"><div class=""><div class="contents"><div class="border border-token-border-light border-radius-3xl corner-superellipse/1.1 rounded-3xl"><div class="relative h-full w-full border-radius-3xl bg-(--code-block-surface) corner-superellipse/1.1 overflow-clip rounded-3xl [--code-block-surface:var(--bg-elevated-secondary)] dark:[--code-block-surface:var(--composer-surface-primary)] lxnfua_clipPathFallback"><div class="pointer-events-none absolute inset-x-4 top-12 bottom-4"><div class="pointer-events-none sticky z-40 shrink-0 z-1!"><div class="sticky bg-token-border-light"></div></div></div><div class="relative"><div class="h-full min-h-0 min-w-0"><div class="h-full min-h-0 min-w-0"><div class=""><div class="relative"><div class=""><div class="relative z-0 flex max-w-full"><div id="code-block-viewer" dir="ltr" class="q9tKkq_viewer cm-editor z-10 light:cm-light dark:cm-light flex h-full w-full flex-col items-stretch ͼs ͼ16"><div class="cm-scroller"><pre class="cm-content q9tKkq_readonly m-0"><code><span class="ͼv">ALTER</span><span></span><span class="ͼv">TABLE</span><span> public.usuarios
</span><span class="ͼv">ADD</span><span></span><span class="ͼv">CONSTRAINT</span><span> usuarios_email_unique </span><span class="ͼv">UNIQUE</span><span>(email);</span></code></pre></div></div></div></div></div></div></div></div><div class=""><div class=""></div></div></div></div></div></div></div></div></pre>

---

# Durante estos meses fuimos agregando:

* permisos,
* refresh tokens,
* blacklist,
* auditoría,
* organismos,
* roles,
* JWT,
* React,
* PySide6.

Ahora vamos a agregar:

* recuperación de contraseña,
* correos,
* políticas de seguridad.

## Propuesta de Ejecucion

**No seguir modificando la tabla `usuarios` con `ALTER TABLE` cada vez que agregamos una funcionalidad.**

Hacer una **auditoría completa del módulo de autenticación** y rediseñar definitivamente estas tablas:

* `usuarios`
* `permisos`
* `usuarios_permisos`
* `refresh_tokens`
* `token_blacklist`
* `auditoria`
* `password_reset_tokens` (nueva)

Dejarlas normalizadas, con nombres consistentes, claves foráneas, índices y preparadas para producción. Así evitaremos tener que cambiar la estructura cada vez que incorporemos una nueva característica y construiremos una base sólida para el crecimiento del sistema.

# FASE 1 — Arquitectura del módulo de autenticación

## Paso 1 — Definir los requisitos

Qué debe hacer el sistema.

### Usuarios

* Crear usuarios.
* Modificar usuarios.
* Eliminar usuarios (lógicamente).
* Bloquear usuarios.
* Desbloquear usuarios.

---

### Seguridad

* Login.
* Logout.
* Refresh Token.
* JWT.
* Blacklist.
* Recuperación de contraseña.
* Cambio de contraseña.

---

### Auditoría

Registrar:

* Inicio de sesión.
* Cierre de sesión.
* Cambio de contraseña.
* Recuperación.
* Creación de usuario.
* Modificación.
* Eliminación.
* Intentos fallidos.

---

### Permisos

* Roles.
* Permisos.
* Permisos especiales.
* Organismos autorizados.

---

### Sesiones

* Fecha inicio.
* Fecha expiración.
* Dirección IP.
* Navegador.
* Sistema Operativo.
* Aplicación utilizada.

---

Cuando esto esté aprobado pasaremos al siguiente paso.

---

# Paso 2 — Diseñar el modelo de datos

Qué tablas existirán?

Propuesta inicial.

<pre class="overflow-visible! px-0!" data-start="1900" data-end="2029"><div class="relative w-full mt-4 mb-1"><div class=""><div class="contents"><div class="relative"><div class="h-full min-h-0 min-w-0"><div class="h-full min-h-0 min-w-0"><div class="border border-token-border-light border-radius-3xl corner-superellipse/1.1 rounded-3xl"><div class="h-full w-full border-radius-3xl bg-(--code-block-surface) corner-superellipse/1.1 overflow-clip rounded-3xl [--code-block-surface:var(--bg-elevated-secondary)] dark:[--code-block-surface:var(--composer-surface-primary)] lxnfua_clipPathFallback"><div class="pointer-events-none absolute end-1.5 top-1 z-2 md:end-2 md:top-1"></div><div class="relative"><div class="pe-11 pt-3"><div class="relative z-0 flex max-w-full"><div id="code-block-viewer" dir="ltr" class="q9tKkq_viewer cm-editor z-10 light:cm-light dark:cm-light flex h-full w-full flex-col items-stretch ͼs ͼ16"><div class="cm-scroller"><pre class="cm-content q9tKkq_readonly m-0"><code><span>usuarios

roles

permisos

usuarios_roles

roles_permisos

refresh_tokens

password_reset_tokens

sesiones

auditoria</span></code></pre></div></div></div></div></div></div></div></div></div><div class=""><div class=""></div></div></div></div></div></div></pre>

Todavía no sabemos los campos.

Solo sabemos que existen.

---

# Paso 3 — Relaciones

Recién aquí construiremos el MER.

Por ejemplo.

<pre class="overflow-visible! px-0!" data-start="2167" data-end="2230"><div class="relative w-full mt-4 mb-1"><div class=""><div class="contents"><div class="relative"><div class="h-full min-h-0 min-w-0"><div class="h-full min-h-0 min-w-0"><div class="border border-token-border-light border-radius-3xl corner-superellipse/1.1 rounded-3xl"><div class="h-full w-full border-radius-3xl bg-(--code-block-surface) corner-superellipse/1.1 overflow-clip rounded-3xl [--code-block-surface:var(--bg-elevated-secondary)] dark:[--code-block-surface:var(--composer-surface-primary)] lxnfua_clipPathFallback"><div class="pointer-events-none absolute end-1.5 top-1 z-2 md:end-2 md:top-1"></div><div class="relative"><div class="pe-11 pt-3"><div class="relative z-0 flex max-w-full"><div id="code-block-viewer" dir="ltr" class="q9tKkq_viewer cm-editor z-10 light:cm-light dark:cm-light flex h-full w-full flex-col items-stretch ͼs ͼ16"><div class="cm-scroller"><pre class="cm-content q9tKkq_readonly m-0"><code><span>Usuario

↓

tiene

↓

Roles

↓

tienen

↓

Permisos</span></code></pre></div></div></div></div></div></div></div></div></div><div class=""><div class=""></div></div></div></div></div></div></pre>

---

# Paso 4 — Diseño físico

PostgreSQL.

Definiremos.

* índices;
* claves primarias;
* claves foráneas;
* restricciones;
* UNIQUE;
* CHECK;
* NOT NULL.

---

# Paso 5 — API

Diseño de FastAPI.

Endpoints.

<pre class="overflow-visible! px-0!" data-start="2490" data-end="2661"><div class="relative w-full mt-4 mb-1"><div class=""><div class="contents"><div class="relative"><div class="h-full min-h-0 min-w-0"><div class="h-full min-h-0 min-w-0"><div class="border border-token-border-light border-radius-3xl corner-superellipse/1.1 rounded-3xl"><div class="h-full w-full border-radius-3xl bg-(--code-block-surface) corner-superellipse/1.1 overflow-clip rounded-3xl [--code-block-surface:var(--bg-elevated-secondary)] dark:[--code-block-surface:var(--composer-surface-primary)] lxnfua_clipPathFallback"><div class="pointer-events-none absolute end-1.5 top-1 z-2 md:end-2 md:top-1"></div><div class="relative"><div class="pe-11 pt-3"><div class="relative z-0 flex max-w-full"><div id="code-block-viewer" dir="ltr" class="q9tKkq_viewer cm-editor z-10 light:cm-light dark:cm-light flex h-full w-full flex-col items-stretch ͼs ͼ16"><div class="cm-scroller"><pre class="cm-content q9tKkq_readonly m-0"><code><span>POST /login

POST /logout

POST /refresh

POST /forgot-password

POST /reset-password

GET /usuarios

POST /usuarios

PUT /usuarios/{id}

DELETE /usuarios/{id}</span></code></pre></div></div></div></div></div></div></div></div></div><div class=""><div class=""></div></div></div></div></div></div></pre>

---

# Paso 6 — React

Pantallas.

Login.

Recuperar contraseña.

Administrar usuarios.

Administrar roles.

---

# Paso 7 — PySide6

Las mismas operaciones.

Consumirá exactamente la misma API.

---

# Paso 8 — Seguridad

Aquí revisaremos.

JWT.

Cookies.

HTTPS.

CORS.

Rate Limiting.

Bloqueo por intentos.

Expiraciones.

---

# Paso 9 — Despliegue

Railway.

AWS.

Hostinger.

Backups.

SSL.

Dominio.

Correo.

---


# Arquitectura


**Datcorr** como una plataforma.

Módulos completamente independientes.

<pre class="overflow-visible! px-0!" data-start="3480" data-end="3725"><div class="relative w-full mt-4 mb-1"><div class=""><div class="contents"><div class="relative"><div class="h-full min-h-0 min-w-0"><div class="h-full min-h-0 min-w-0"><div class="border border-token-border-light border-radius-3xl corner-superellipse/1.1 rounded-3xl"><div class="h-full w-full border-radius-3xl bg-(--code-block-surface) corner-superellipse/1.1 overflow-clip rounded-3xl [--code-block-surface:var(--bg-elevated-secondary)] dark:[--code-block-surface:var(--composer-surface-primary)] lxnfua_clipPathFallback"><div class="pointer-events-none absolute end-1.5 top-1 z-2 md:end-2 md:top-1"></div><div class="relative"><div class="pe-11 pt-3"><div class="relative z-0 flex max-w-full"><div id="code-block-viewer" dir="ltr" class="q9tKkq_viewer cm-editor z-10 light:cm-light dark:cm-light flex h-full w-full flex-col items-stretch ͼs ͼ16"><div class="cm-scroller"><pre class="cm-content q9tKkq_readonly m-0"><code><span>DATCORR
│
├──────── Seguridad
│
├──────── Usuarios
│
├──────── Organismos
│
├──────── Diccionario de Datos
│
├──────── Búsquedas
│
├──────── Inventario
│
├──────── Auditoría
│
├──────── Reportes
│
├──────── Configuración
│
└──────── API</span></code></pre></div></div></div></div></div></div></div></div></div><div class=""><div class=""></div></div></div></div></div></div></pre>

Cada módulo tendrá:

* su documentación;
* su modelo de datos;
* su API;
* sus servicios;
* sus permisos.

Así, cuando dentro de dos años queremos agregar un décimo organismo, una nueva funcionalidad o incluso un cliente completamente distinto, no tendremos que modificar el resto del sistema.

---

# Hoja de ruta

Seguir exactamente este orden:

### **ETAPA 1 – Análisis funcional** ✅ 

* Definir qué debe hacer el módulo de autenticación.
* Definir las reglas de negocio.
* Identificar actores y permisos.

### **ETAPA 2 – Modelo de datos conceptual**

* Entidades.
* Relaciones.
* Reglas de integridad.

### **ETAPA 3 – Modelo físico PostgreSQL**

* Tablas.
* Índices.
* Restricciones.
* Optimización.

### **ETAPA 4 – Backend (FastAPI)**

* Servicios.
* Autenticación.
* JWT.
* Recuperación de contraseña.
* Auditoría.

### **ETAPA 5 – Frontend React**

* Login.
* Gestión de usuarios.
* Recuperación de contraseña.

### **ETAPA 6 – Cliente PySide6**

* Consumirá exactamente la misma API, sin acceso directo a PostgreSQL.

---

## Hay una decisión de arquitectura que quiero tomar antes de crear la primera tabla

Creo que es la más importante de todo el módulo de seguridad.

**Un usuario puede tener acceso a varios organismos simultáneamente** .

Los permisos definiran el acceso a las funciones no a los datos en si:


Los permisos serán del tipo:

<pre class="overflow-visible! px-0!" data-start="496" data-end="700"><div class="relative w-full mt-4 mb-1"><div class=""><div class="contents"><div class="relative"><div class="h-full min-h-0 min-w-0"><div class="h-full min-h-0 min-w-0"><div class="border border-token-border-light border-radius-3xl corner-superellipse/1.1 rounded-3xl"><div class="h-full w-full border-radius-3xl bg-(--code-block-surface) corner-superellipse/1.1 overflow-clip rounded-3xl [--code-block-surface:var(--bg-elevated-secondary)] dark:[--code-block-surface:var(--composer-surface-primary)] lxnfua_clipPathFallback"><div class="pointer-events-none absolute end-1.5 top-1 z-2 md:end-2 md:top-1"></div><div class="relative"><div class="pe-11 pt-3"><div class="relative z-0 flex max-w-full"><div id="code-block-viewer" dir="ltr" class="q9tKkq_viewer cm-editor z-10 light:cm-light dark:cm-light flex h-full w-full flex-col items-stretch ͼs ͼ16"><div class="cm-scroller"><pre class="cm-content q9tKkq_readonly m-0"><code><span>Puede Buscar

Puede Crear Usuarios

Puede Modificar Usuarios

Puede Eliminar Usuarios

Puede Importar

Puede Exportar

Puede Administrar Organismos

Puede Ver Auditoría

Puede Generar Reportes</span></code></pre></div></div></div></div></div></div></div></div></div></div></div></div></div></pre>


Los  **permisos son funcionales** .

No dependen del organismo.
