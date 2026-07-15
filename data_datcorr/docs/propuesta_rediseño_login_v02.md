# 📋 Propuesta de Rediseño de Login - DatCorr v02

## 🎯 Objetivo

Implementar un login institucional profesional alineado a la arquitectura existente del proyecto, mejorando UX, accesibilidad y mantenibilidad sin romper la seguridad ya implementada en backend (JWT, refresh tokens, blacklist, rate limiting, auditoría).

---

## 📊 Estado Actual del Proyecto

### Frontend
- **Framework**: React + Vite
- **State**: Zustand (`authStore.js`)
- **Routing**: React Router v6
- **HTTP**: Axios con interceptor de refresh token
- **Rutas públicas**: `/` (Login), `/forgot-password`, `/reset-password`
- **Rutas privadas**: Protegidas por `PrivateRoute.jsx`

### Backend
- **Framework**: FastAPI
- **Auth**: JWT + Refresh Token en cookie HttpOnly
- **Seguridad**: Rate limiting, blacklist de tokens, auditoría, bloqueo por intentos fallidos
- **Endpoint login**: `POST /auth/login`
- **Endpoint refresh**: `POST /auth/refresh`
- **Endpoint logout**: `POST /auth/logout`

### Problemas detectados en el plan v01
1. Código JSX mal formado (etiquetas sin cerrar, estructura rota)
2. Referencia a carpeta `components/Login.jsx` cuando está en `pages/Login.jsx`
3. Propone `opacity: 2` en CSS (inválido)
4. No considera refresh token existente ni cookie HttpOnly
5. Validaciones redundantes con backend
6. Regex de email rechaza usuarios que podrían ser correos válidos
7. Accesibilidad con referencias rotas (`aria-describedby` sin elemento destino)
8. No contempla el tema oscuro institucional actual

---

## 🎨 1. Mejoras de Diseño Visual

### A. Estructura de archivos

```
frontend/src/pages/Login.jsx
frontend/src/pages/Login.css
```

### B. Paleta de colores (manteniendo tema oscuro institucional)

| Categoría | Color | Uso |
|-----------|-------|-----|
| Fondo | `#0f172a` | Pantalla de fondo |
| Tarjeta | `rgba(255, 255, 255, 0.95)` | Fondo tarjeta (modo claro) |
| Texto principal | `#1e293b` | Títulos |
| Texto secundario | `#334155` | Labels |
| Acento | `#2563eb` | Inputs focus |
| Botón | `#1e40af` | Botón primary |
| Botón hover | `#1d4ed8` | Hover |
| Error | `#ef4444` | Mensajes de error |
| Éxito | `#22c55e` | Mensajes de éxito |

### C. Glass Card mejorado

```css
.glass-card {
  position: relative;
  z-index: 1;
  width: 360px;
  max-width: 90vw;
  padding: 40px;
  background: rgba(255, 255, 255, 0.95);
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: 20px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
  color: #1e293b;
  transition: transform 0.2s ease;
}

.glass-card:hover {
  transform: translateY(-2px);
}
```

### D. Slideshow de fondo

```css
.slideshow-slide {
  position: absolute;
  inset: 0;
  background-size: cover;
  background-position: center;
  opacity: 0;
  animation: crossfade 25s ease-in-out infinite;
  z-index: 0;
}

.slideshow-slide:nth-child(1) { 
  background-image: linear-gradient(rgba(0,0,0,0.55), rgba(0,0,0,0.55)), url("/images/login/bg.webp"); 
}
.slideshow-slide:nth-child(2) { 
  background-image: linear-gradient(rgba(0,0,0,0.55), rgba(0,0,0,0.55)), url("/images/login/dta_center.webp"); 
  animation-delay: 5s; 
}
.slideshow-slide:nth-child(3) { 
  background-image: linear-gradient(rgba(0,0,0,0.55), rgba(0,0,0,0.55)), url("/images/login/bandera_edificio.webp"); 
  animation-delay: 10s; 
}
.slideshow-slide:nth-child(4) { 
  background-image: linear-gradient(rgba(0,0,0,0.55), rgba(0,0,0,0.55)), url("/images/login/archivos.webp"); 
  animation-delay: 15s; 
}
.slideshow-slide:nth-child(5) { 
  background-image: linear-gradient(rgba(0,0,0,0.55), rgba(0,0,0,0.55)), url("/images/login/archiveros.webp"); 
  animation-delay: 20s; 
}

@keyframes crossfade {
  0%, 100% { opacity: 0.4; }
  5%       { opacity: 1; }
  20%      { opacity: 1; }
  25%      { opacity: 0.4; }
}

@media (prefers-reduced-motion: reduce) {
  .slideshow-slide {
    animation: none;
    opacity: 0.4;
  }
}
```

---

## 🖥️ 2. Mejoras de Experiencia de Usuario (UX)

### A. Componente Login mejorado

```jsx
import { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import api from "../api/axiosClient";
import { useAuthStore } from "../auth/authStore";
import "./Login.css";

export default function Login() {
    const navigate = useNavigate();
    const setTokens = useAuthStore((s) => s.setTokens);

    const [usuario, setUsuario] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);
    const [showPassword, setShowPassword] = useState(false);

    useEffect(() => {
        if (useAuthStore.getState().accessToken) {
            navigate("/dashboard", { replace: true });
        }
    }, [navigate]);

    const handleLogin = async (e) => {
        e.preventDefault();
        setError("");
        setLoading(true);

        try {
            const res = await api.post("/auth/login", { 
                usuario, 
                password 
            });
            setTokens(res.data.token);
            navigate("/dashboard", { replace: true });
        } catch (err) {
            const mensaje = err.response?.data?.detail 
                || err.response?.data?.mensaje 
                || "Usuario o contraseña incorrectos.";
            setError(mensaje);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="login-page" role="main">
            {[1, 2, 3, 4, 5].map((i) => (
                <div key={i} className="slideshow-slide" />
            ))}

            <form className="glass-card" onSubmit={handleLogin} noValidate>
                <div className="login-header">
                    <h1>DatCorr</h1>
                    <p className="login-subtitle">Sistema de Gestión Documental</p>
                </div>

                <div className="form-group">
                    <label htmlFor="usuario-input">Usuario</label>
                    <input
                        id="usuario-input"
                        name="usuario"
                        type="text"
                        placeholder="Ingrese su usuario"
                        autoComplete="username"
                        value={usuario}
                        onChange={(e) => setUsuario(e.target.value)}
                        required
                        aria-required="true"
                        disabled={loading}
                    />
                </div>

                <div className="form-group">
                    <label htmlFor="password-input">Contraseña</label>
                    <div className="password-wrapper">
                        <input
                            id="password-input"
                            name="password"
                            type={showPassword ? "text" : "password"}
                            placeholder="Ingrese su contraseña"
                            autoComplete="current-password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                            aria-required="true"
                            aria-invalid={!!error}
                            disabled={loading}
                        />
                        <button
                            type="button"
                            className="toggle-password"
                            onClick={() => setShowPassword(!showPassword)}
                            aria-label={showPassword ? "Ocultar contraseña" : "Mostrar contraseña"}
                        >
                            {showPassword ? "👁️" : "👁️‍🗨️"}
                        </button>
                    </div>
                </div>

                {error && (
                    <div className="login-error" role="alert" aria-live="polite">
                        {error}
                    </div>
                )}

                <button 
                    type="submit" 
                    disabled={loading || !usuario.trim() || !password.trim()}
                    className="login-button"
                >
                    {loading ? (
                        <span className="spinner" aria-hidden="true" />
                    ) : null}
                    {loading ? "Ingresando…" : "Ingresar"}
                </button>

                <div className="login-links">
                    <Link to="/forgot-password" className="forgot-link">
                        ¿Olvidaste tu contraseña?
                    </Link>
                </div>

                <div className="trust-footer">
                    <span>Conexión cifrada (TLS)</span>
                    <span>•</span>
                    <span>Datos protegidos</span>
                </div>
            </form>
        </div>
    );
}
```

### B. CSS complementario

```css
.login-page {
  position: relative;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #0f172a;
  overflow: hidden;
}

.login-header {
  text-align: center;
  margin-bottom: 32px;
}

.login-header h1 {
  margin: 0;
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
}

.login-subtitle {
  margin: 8px 0 0;
  font-size: 14px;
  color: #64748b;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  font-size: 14px;
  font-weight: 500;
  color: #334155;
}

.form-group input {
  width: 100%;
  padding: 12px 14px;
  border: 1px solid #cbd5e1;
  border-radius: 10px;
  background: #ffffff;
  color: #1e293b;
  font-size: 15px;
  box-sizing: border-box;
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.form-group input:focus {
  border-color: #2563eb;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

.form-group input::placeholder {
  color: #94a3b8;
}

.password-wrapper {
  position: relative;
}

.password-wrapper input {
  padding-right: 44px;
}

.toggle-password {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  cursor: pointer;
  font-size: 16px;
  padding: 4px;
  opacity: 0.6;
  transition: opacity 0.2s;
}

.toggle-password:hover {
  opacity: 1;
}

.login-button {
  width: 100%;
  padding: 14px;
  border: none;
  border-radius: 10px;
  background: #1e40af;
  color: #ffffff;
  font-weight: 600;
  font-size: 15px;
  cursor: pointer;
  transition: background 0.2s, transform 0.1s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.login-button:hover:not(:disabled) {
  background: #1d4ed8;
}

.login-button:active:not(:disabled) {
  transform: scale(0.98);
}

.login-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: #ffffff;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.login-links {
  margin-top: 16px;
  text-align: center;
}

.forgot-link {
  font-size: 14px;
  color: #2563eb;
  text-decoration: none;
}

.forgot-link:hover {
  text-decoration: underline;
}

.login-error {
  color: #ef4444;
  font-size: 13px;
  padding: 10px 12px;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 8px;
  margin-bottom: 16px;
  text-align: center;
}

.trust-footer {
  margin-top: 24px;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: #94a3b8;
}
```

---

## 🔒 3. Consideraciones de Seguridad

### A. Validaciones

| Tipo | Responsable | Razón |
|------|-------------|-------|
| Autenticación | Backend | Ya implementado (JWT + blacklist) |
| Bloqueo por intentos | Backend | Ya implementado (5 intentos / 15 min) |
| Rate limiting | Backend | Ya implementado (5 intentos / 5 min) |
| Formato básico | Frontend | Mejorar UX sin comprometer seguridad |
| Sanitización | Backend | Ya implementado |

**No duplicar** validaciones de seguridad en frontend. El frontend debe:
- Validar campos vacíos (obligatorios)
- Mostrar feedback de carga
- Limpiar errores al reenviar

### B. Manejo de sesiones

- El refresh token se almacena en cookie HttpOnly (manejado por backend)
- El access token se guarda en `sessionStorage` (ya implementado)
- El interceptor de Axios ya maneja el refresh automáticamente
- No exponer tokens en localStorage

### C. Accesibilidad (A11y)

- Labels asociados a inputs con `htmlFor` / `id`
- `aria-required="true"` en campos obligatorios
- `aria-invalid` y `role="alert"` en errores
- `aria-busy` durante carga
- `prefers-reduced-motion` respetado en animaciones
- Contraste WCAG AA cumplido

---

## 🚀 4. Plan de Implementación por Pasos

### Paso 1: Backup y preparación
```bash
# Verificar que el proyecto compile actualmente
cd C:\data_datcorr\frontend
npm run build
```

**Éxito**: Build sin errores.

### Paso 2: Actualizar Login.css
- Corregir `opacity: 2` a `opacity: 0`
- Ajustar slideshow a 25s con delays correctos
- Actualizar glass card a fondo claro
- Agregar estilos de password wrapper, botón, error

**Éxito**: 
```bash
npm run dev
```
Verificar login carga correctamente con nuevo diseño.

### Paso 3: Actualizar Login.jsx
- Incorporar toggle de contraseña
- Mejorar manejo de errores
- Agregar spinner de carga
- Validar campos vacíos antes de enviar
- Mantener estructura de carpetas actual

**Éxito**: Login funcional con nuevas validaciones visuales.

### Paso 4: Verificar flujo completo
1. Login exitoso → redirige a `/dashboard`
2. Refresh token funciona (esperar 15 min o forzar expiración)
3. Logout limpia sesión
4. Error de credenciales muestra mensaje del backend
5. Campos vacíos bloquean envío

**Éxito**: Flujo E2E funcional.

### Paso 5: Pruebas de accesibilidad
- Navegación solo con teclado (Tab, Enter)
- Screen reader lee labels y errores
- Contraste verificado con herramientas de navegador

**Éxito**: Navegación completa sin mouse.

---

## 📝 5. Archivos Modificados

| Archivo | Cambios |
|---------|---------|
| `frontend/src/pages/Login.css` | Estilos actualizados |
| `frontend/src/pages/Login.jsx` | Componente mejorado |

---

## ⚠️ 6. Riesgos y Mitigaciones

| Riesgo | Mitigación |
|--------|------------|
| Romper login existente | Paso a paso con rollback |
| Cookies HttpOnly bloqueadas | Verificar configuración CORS y dominios |
| Refresh token no funciona | Mantener interceptor existente sin cambios |
| Build roto | Verificar en cada paso |

---

## ✅ 7. Criterios de Aceptación

- [ ] Login carga en < 2s
- [ ] Diseño responsive (mobile + desktop)
- [ ] Accesibilidad WCAG AA
- [ ] Flujo login → dashboard funcional
- [ ] Manejo de errores visible
- [ ] Refresh automático de token
- [ ] Logout limpia sesión
- [ ] No hay regresiones en seguridad
