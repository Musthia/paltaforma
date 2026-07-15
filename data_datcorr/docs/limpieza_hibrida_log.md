# Limpieza hibrida DatCorr

## 2026-06-10 - Paso 1: correcciones de bajo riesgo

Objetivo: corregir conflictos puntuales detectados sin cambiar la arquitectura general ni retirar codigo legado todavia.

Cambios aplicados:

- Backend login: se valido `usuario_db` antes de acceder a `usuario_db.id`, evitando error cuando el usuario no existe.
- Desktop editar usuario: se corrigio el reset de password usando una variable definida `nueva_password`.
- Desktop editar usuario: se corrigio la validacion de usuario para usar `usuario_texto`.
- Desktop editar usuario: el log de actualizacion ahora muestra el texto capturado del usuario.
- Frontend usuarios: `actualizarUsuario` usa `PATCH`, alineado con el router FastAPI.
- Frontend modal usuario: al editar llama `actualizarUsuario`; al crear llama `crearUsuario`.
- Frontend modal usuario: el password queda vacio al editar y solo se envia si el operador lo completa.
- Dependencias Python: se agrego `requests`, usado por `core/api_client.py`.

Verificacion:

- OK: `python -m compileall -q backend ventanas core services database repositories`.
- OK: revision de referencias confirma `api.patch`, `actualizarUsuario`, `crearUsuario`, `nueva_password` y `usuario_texto.strip()`.
- OK: se ejecuto `npm.cmd install` dentro de `frontend`.
- OK: `npm.cmd run build`.
- Advertencia no bloqueante: Vite informa bundle mayor a 500 kB, esperable por dependencias como MUI/DataGrid. Se puede optimizar mas adelante con code splitting.
- OK: se restauro `frontend/src_old` porque su limpieza no formaba parte de este paso.

## 2026-06-10 - Paso 2: cliente API frontend unico

Objetivo: reducir duplicidad en el frontend activo sin afectar rutas ni componentes.

Cambios aplicados:

- Se elimino `frontend/src/api/api.js`.
- Se conserva `frontend/src/api/axiosClient.js` como cliente API unico del frontend activo.

Motivo:

- `api.js` y `axiosClient.js` tenian la misma responsabilidad: crear una instancia Axios con `baseURL` y token Bearer.
- La busqueda en `frontend/src` confirmo que los imports activos usan `../api/axiosClient`.

Verificacion:

- OK: `npm.cmd run build`.
- OK: no quedan referencias a `api/api` en `frontend/src`.

## 2026-06-10 - Paso 3: acceso a usuarios centralizado en frontend

Objetivo: evitar dos caminos para listar usuarios en el frontend activo.

Cambios aplicados:

- `frontend/src/hooks/useUsuariosGrid.js` dejo de importar Axios directamente.
- El grid ahora usa `listarUsuarios` desde `frontend/src/services/usuariosService.js`.

Motivo:

- `useUsuarios.js` ya usaba el servicio normalizado.
- `useUsuariosGrid.js` repetia la llamada `api.get("/usuarios")`, generando duplicidad de reglas de paginacion y normalizacion.

Verificacion:

- OK: `npm.cmd run build`.
- OK: las llamadas a `/usuarios` del frontend activo quedaron en `frontend/src/services/usuariosService.js`.
- OK: `useUsuarios.js` y `useUsuariosGrid.js` importan `listarUsuarios` desde el servicio.

## Siguiente paso recomendado

- Luego continuar con la duplicidad backend/desktop: servicios directos a BD frente a servicios API.

## 2026-06-10 - Paso 4: eliminacion de frontend legado

Objetivo: retirar el arbol frontend legado para reducir ruido y evitar imports accidentales.

Cambios aplicados:

- Se elimino `frontend/src_old`.

Motivo:

- El frontend activo vive en `frontend/src`.
- La busqueda previa confirmo que `frontend/src_old` no estaba referenciado por el codigo activo.

Verificacion:

- OK: `npm.cmd run build`.
- OK: `Test-Path frontend/src_old` devuelve `False`.

## Siguiente paso recomendado

- Continuar con la duplicidad backend/desktop: servicios directos a BD frente a servicios API.

## 2026-06-10 - Paso 5: arquitectura objetivo documentada

Objetivo: dejar una guia concreta para ordenar el proyecto hibrido sin improvisar refactors grandes.

Cambios aplicados:

- Se creo `docs/arquitectura_hibrida_objetivo.md`.

Motivo:

- El proyecto debe crecer hacia manejo de datos, consulta, edicion, actualizacion, eliminacion y anexion de nuevas tablas/bases.
- Para evitar duplicidad futura, se define FastAPI como fuente de verdad progresiva y desktop/web como clientes.

Verificacion pendiente:

- Centralizar dependencias DB del backend como primer ajuste tecnico de arquitectura.
