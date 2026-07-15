# Revisión: Rediseño Pantalla de Login "Transparencia Institucional"

> Análisis de practicidad, fortalezas, debilidades y vulnerabilidades de
> `docs/propuesta_login_rediseno.md`, contrastado contra el código real del
> proyecto (`frontend/src/pages/Login.jsx`, `frontend/src/auth/authStore.js`).

---

## 1. Veredicto rápido

| Dimensión                     | Evaluación                                                    |
| ------------------------------ | -------------------------------------------------------------- |
| Concepto visual                | ✅ Bueno, coherente con el target gobierno/salud               |
| Practicidad de implementación | ✅ Bajo esfuerzo (~2 h), modular                               |
| Accesibilidad (WCAG)           | ❌**Contradictoria** (texto oscuro sobre vidrio oscuro)  |
| Seguridad                      | ⚠️ Ignora fallas reales del`Login.jsx` actual              |
| Riesgo legal/compliance        | ⚠️ Sellos ISO/RGPD sin certificación = publicidad engañosa |

**Conclusión:** El rediseño es recomendable *como capa visual*, pero **no debe
implementarse sin antes corregir las fallas funcionales y de seguridad del login
existente** y sin resolver la contradicción de contraste. La afirmación de la
propuesta "no tocar la lógica de autenticación" es, en la práctica, un riesgo: el
login actual tiene bugs que un rediseño no arregla.

---

## 2. Verificación de practicidad

### Lo que SÍ es práctico

- **Costo bajo:** 1 componente + 1 CSS + imágenes locales. Sin nuevas dependencias.
- **Mantenible:** imágenes en `public/images/login/`, sin tocar código.
- **Responsive:** el patrón centrado + `background-size: cover` funciona en móvil.
- **Degradación elegante:** `backdrop-filter` con fallback de fondo sólido (`#0f172a`).
- **Accesibilidad de movimiento:** considera `prefers-reduced-motion: reduce`.
- **Rendimiento razonable:** WebP ~250 KB + preload, sin carrusel.

### Lo que NO es tan práctico como dice

- **"Pasa WCAG AA en todos los casos"** — FALSO (ver §4). Es la afirmación más
  peligrosa del documento: se usa como justificación sin verificar.
- **Imagen como fondo (no `<img>`)** — no se puede aplicar `loading="lazy"` ni
  `alt`, y el `<picture>`/preload que sugiere es para `<img>`, no para
  `background-image`. La recomendación técnica está mal dirigida al caso real.
- **Hotlink a Unsplash** (línea 120) — si se usa la URL directa en vez de
  descargar, crea dependencia externa, posible tracking y rotura si Unsplash
  cambia la ruta. El plan dice "descargar", pero la URL genérica tienta a hacer
  lo contrario.

---

## 3. Fortalezas

1. Identidad corporativa coherente con el sector (gobierno/salud/legal).
2. Glassmorphism bien acotado (sobre overlay oscuro, no sobre fondo cargado).
3. Paleta definida y documentada (facilita QA y mantenimiento).
4. Plan de implementación por fases con tiempos realistas.
5. Matriz de riesgos con mitigaciones concretas.
6. Sensibilidad por `prefers-reduced-motion` y fallback de navegadores antiguos.
7. Separa claramente lo visual de la lógica (buena intención, mal ejecutada — ver §5).

---

## 4. Debilidades (críticas)

### 4.1 Contradicción de contraste (falla de accesibilidad real)

La propuesta combina:

- Fondo del vidrio: `rgba(255,255,255,0.12)` → vidrio **oscuro/transparente**.
- Imagen con overlay `rgba(0,0,0,0.55)` → fondo **oscuro**.
- Texto etiquetas/inputs: azul oscuro `#0a1f44`.

Resultado: **texto azul oscuro (#0a1f44) sobre un vidrio oscuro sobre foto
oscurecida** → contraste muy por debajo de WCAG AA (ratio estimado < 2:1;
AA exige 4.5:1 para texto normal, 3:1 para grande). La propia propuesta se
contradice: en la línea 11 dice "texto azul oscuro … buena relación de
contraste", y en la paleta repite lo mismo, pero con esos valores es imposible.

**Corrección obligatoria:** sobre vidrio oscuro el texto debe ser **claro**
(blanco / `#f1f5f9`). El azul oscuro solo sirve si el vidrio es **claro**
(`rgba(255,255,255,0.85+)`), lo que rompe el look "glass" sobre foto. Hay que
elegir uno de los dos y medir con un chequeador de contraste.

### 4.2 Sellos de confianza sin certificación (riesgo legal/compliance)

Mostrar "ISO 27001" y "RGPD" como cumplidos cuando `datcor.md` solo lista
controles implementados (JWT, blacklist, auditoría) — no certificaciones
auditadas — es **publicidad engañosa**. En sector gubernamental/salud esto puede
ser objeto de sanción y erosiona la credibilidad que el diseño intenta construir.

**Corrección:** usar sellos genéricos ("Conexión cifrada TLS", "Datos
protegidos") o mostrar certificaciones **solo si existen y son verificables**.
Nunca afirmar cumplimiento regulatorio sin respaldo.

### 4.3 Asume que la lógica actual está bien

La propuesta dice "no tocar la lógica de autenticación". Pero el `Login.jsx`
real tiene fallas que un rediseño visual deja intactas (ver §5). Implementar solo
lo visual perpetúa bugs de usabilidad y seguridad.

---

## 5. Vulnerabilidades de seguridad

### 5.1 En el código actual (`Login.jsx`) — NO cubiertas por la propuesta

| # | Problema                                                                                                                                        | Impacto                                                                            | Severidad           |
| - | ----------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- | ------------------- |
| 1 | **Sin `try/catch` en `handleLogin`** — si el login falla, `res.data.token` lanza excepción y la app crashea en blanco.            | UX rota + posible fuga de error en consola.                                        | Media               |
| 2 | **Sin estado de carga / botón no se deshabilita** — doble envío de credenciales en red lenta.                                          | Reintentos, posible lock de cuenta.                                                | Media               |
| 3 | **Inputs sin `id`/`htmlFor`, sin `autoComplete`** — el navegador no puede gestionar credenciales ni gestores de contraseña.       | Usabilidad y adopción de MFA débil.                                              | Baja                |
| 4 | **Sin mensaje de error al usuario** — falla silenciosa (el `styles.error` existe pero no se usa).                                      | Los atacantes no distinguen usuario de password, pero el usuario queda confundido. | Baja                |
| 5 | **Tokens en `sessionStorage`** — mejor que `localStorage`, pero **vulnerable a XSS**. Cualquier script inyectado lee el token. | Secuestro de sesión.                                                              | Alta (contexto XSS) |
| 6 | **Sin `label` accesibles** — los `input` no tienen etiqueta asociada.                                                                | Incumplimiento de accesibilidad + Autofill deficiente.                             | Baja                |

### 5.2 En la propuesta (riesgos introducidos o ignorados)

| #  | Problema                                                                                                                                                                                                  | Impacto                                       | Severidad  |
| -- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------- | ---------- |
| 7  | **Hotlink a Unsplash** (URL genérica) — si no se descarga, dependencia externa + tracking de terceros + posible rotura.                                                                           | Privacidad / disponibilidad.                  | Baja-Media |
| 8  | **Imagen de fondo vía CSS**, no `<img>` — no hay `alt`, no hay preload eficaz, no hay control de carga. La recomendación `<picture>` no aplica a `background-image`.                     | Accesibilidad / rendimiento mal justificados. | Baja       |
| 9  | **Sellos de compliance falsos** (§4.2) — afirmar ISO 27001 / RGPD sin certificar.                                                                                                                 | Riesgo legal y reputacional.                  | Media      |
| 10 | **Animación `slowZoom` infinita** — aunque respeta `prefers-reduced-motion`, si se olvida ese media query causa mareo/migraña.                                                               | Accesibilidad.                                | Baja       |
| 11 | **CSP / cabeceras** — la propuesta no menciona una política de `Content-Security-Policy` que restrinja la carga de imágenes solo al origen propio, lo que refuerza el riesgo de hotlink (§9). | Seguridad de capa.                            | Baja       |

**Nota:** El login usa JWT bearer (vía `axiosClient`) y refresh con blacklist
según `datcor.md`; eso está bien en backend. El riesgo principal en frontend es
XSS → robo de token en `sessionStorage` (punto 5).

---

## 6. Conclusión

La propuesta **"Transparencia Institucional" es válida y recomendable como
rediseño visual**, con dos condiciones innegociables:

1. **Corregir el contraste** (texto claro sobre vidrio oscuro) antes de
   afirmar conformidad WCAG. La afirmación actual de "AA en todos los casos" es
   incorrecta.
2. **No usar sellos de certificación falsos.** Reemplazar ISO 27001 / RGPD por
   mensajes genéricos de seguridad o certificaciones reales.

Además, **el rediseño debe acompañarse de las correcciones funcionales del
`Login.jsx`** (manejo de errores, estado de carga, labels/autocomplete, mensaje
de error). Dejar la lógica "intacta" perpetúa bugs de usabilidad y la superficie
XSS sobre `sessionStorage`.

**Riesgo del rediseño solo:** Bajo (visual). **Riesgo si se ignora lo anterior:**
Medio-Alto (legal + usabilidad + XSS latentes).

---

## 7. Forma de implementarlo (recomendada)

### 7.1 Estructura

```
frontend/src/pages/Login.jsx      ← se REESCRIBE (visual + correcciones)
frontend/src/pages/Login.css       ← nuevo: glass + fondo + responsive
frontend/public/images/login/      ← bg.webp + bg.jpg (descargadas, no hotlink)
```

### 7.2 `Login.css` (contraste corregido: texto CLARO sobre vidrio oscuro)

```css
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #0f172a;            /* fallback sólido */
  background-image:
    linear-gradient(rgba(0,0,0,0.55), rgba(0,0,0,0.55)),
    url("/images/login/bg.webp");
  background-size: cover;
  background-position: center;
  background-attachment: fixed;
}

.login-page::before {                   /* slowZoom sin afectar layout */
  content: "";
  position: absolute; inset: 0;
  background: inherit;
  animation: slowZoom 45s ease-in-out infinite;
  z-index: -1;
}

@keyframes slowZoom {
  0%, 100% { transform: scale(1); }
  50%      { transform: scale(1.03); }
}

@media (prefers-reduced-motion: reduce) {
  .login-page::before { animation: none; }
}

.glass-card {
  width: 320px;
  max-width: 90vw;
  padding: 32px;
  background: rgba(255, 255, 255, 0.12);   /* vidrio oscuro */
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.18);
  border-radius: 20px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  color: #f1f5f9;                          /* TEXTO CLARO (corrige AA) */
}

.glass-card label {
  display: block;
  margin-bottom: 6px;
  font-size: 14px;
  color: #e2e8f0;
}

.glass-card input {
  width: 100%;
  padding: 10px 12px;
  margin-bottom: 16px;
  border: 1px solid rgba(255,255,255,0.25);
  border-radius: 8px;
  background: rgba(255,255,255,0.08);
  color: #f8fafc;                          /* texto del input claro */
  font-size: 15px;
}

.glass-card input::placeholder { color: #94a3b8; }

.glass-card button {
  width: 100%;
  padding: 12px;
  border: none;
  border-radius: 8px;
  background: #0a1f44;                      /* azul corporativo oscuro */
  color: #ffffff;
  font-weight: 600;
  cursor: pointer;
}

.glass-card button:hover:not(:disabled) { background: #1e3a5f; }
.glass-card button:disabled { opacity: 0.6; cursor: not-allowed; }

.login-error { color: #fca5a5; font-size: 13px; margin-bottom: 12px; }

.trust-footer {
  margin-top: 20px;
  display: flex;
  gap: 14px;
  font-size: 12px;
  color: rgba(255,255,255,0.6);
}
```

### 7.3 `Login.jsx` (rediseño + correcciones de seguridad/usabilidad)

```jsx
import { useState } from "react";
import api from "../api/axiosClient";
import { useNavigate } from "react-router-dom";
import { useAuthStore } from "../auth/authStore";
import "./Login.css";

export default function Login() {
  const navigate = useNavigate();
  const setTokens = useAuthStore((s) => s.setTokens);

  const [usuario, setUsuario] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const res = await api.post("/auth/login", { usuario, password });
      setTokens(res.data.token, res.data.refresh_token);
      navigate("/dashboard");
    } catch (err) {
      // Mensaje genérico: no revela si el usuario existe (anti-enumeration)
      setError("Usuario o contraseña incorrectos.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-page">
      <form className="glass-card" onSubmit={handleLogin}>
        <h2>DatCorr</h2>

        <label htmlFor="usuario">Usuario</label>
        <input
          id="usuario"
          name="usuario"
          type="text"
          autoComplete="username"
          value={usuario}
          onChange={(e) => setUsuario(e.target.value)}
        />

        <label htmlFor="password">Contraseña</label>
        <input
          id="password"
          name="password"
          type="password"
          autoComplete="current-password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />

        {error && <div className="login-error">{error}</div>}

        <button type="submit" disabled={loading}>
          {loading ? "Ingresando…" : "Ingresar"}
        </button>

        <div className="trust-footer">
          <span>Conexión cifrada (TLS)</span>
          <span>Datos protegidos</span>
        </div>
      </form>
    </div>
  );
}
```

### 7.4 Checklist de QA (aplicar antes de merge)

- [ ] Contraste medido con chequeador (texto claro ≥ 4.5:1 sobre vidrio).
- [ ] `prefers-reduced-motion` desactiva `slowZoom`.
- [ ] Login fallido muestra error genérico y NO crashea.
- [ ] Botón se deshabilita durante el envío (sin doble submit).
- [ ] Imagen descargada localmente (sin hotlink a Unsplash).
- [ ] No hay sellos ISO/RGPD falsos.
- [ ] Prueba en Chrome / Firefox / Edge + fallback de color sólido.

### 7.5 Recomendaciones de seguridad adicionales (fuera del alcance visual)

- Añadir `Content-Security-Policy` que restrinja `img-src` al origen propio.
- Mitigar riesgo XSS sobre `sessionStorage`: sanitizar toda salida, evitar
  `dangerouslySetInnerHTML`, y considerar cookies `HttpOnly` + SameSite para el
  token si se migra el esquema de auth.
- Implementar rate-limiting y bloqueo de cuenta en el backend (`/auth/login`).
- Habilitar autocomplete correcto para facilitar gestores de contraseña / MFA.
