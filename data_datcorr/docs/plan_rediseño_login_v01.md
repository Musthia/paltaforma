
📋 Plan de Rediseño de Login - Documentación Oficial v02
🎯 Objetivo
Implementar un login institucional, profesional y accesible que mantenga la experiencia de usuario fluida y funcional, con mejoras en diseño, seguridad y usabilidad.

📦 Requisitos Previos
🔹 A. Dependencias del Proyecto
Asegúrate de tener instaladas las siguientes dependencias:

bash

npm install react-router-dom
npm install zustand
npm install axios
🔹 B. Estructura de Archivos Actual
text

src/
├── api/
│   └── axiosClient.js
├── auth/
│   └── authStore.js
├── components/
│   └── Login.jsx
├── Login.css
├── index.html
└── public/
    └── images/
        └── login/
            ├── bg.webp
            ├── dta_center.webp
            ├── bandera_edificio.webp
            ├── archivos.webp
            └── archiveros.webp
🎨 1. Mejoras de Diseño Visual (Institucional & Profesional)
🔹 A. Estilo de Tarjeta (Glass Card)
Elemento	Anterior	Mejorada	Razon
Fondo	rgba(255,255,255,0.12)	rgba(255,255,255,0.95)	Mejora legibilidad
Borde	rgba(255,255,255,0.18)	rgba(0,0,0,0.08)	Borde más sutil
Sombra	0 8px 32px rgba(0,0,0,0.3)	0 10px 40px rgba(0,0,0,0.15)	Sombra más suave
Color Texto	#f1f5f9	#1e293b	Mayor contraste
Interacción	Sin transición	transform 0.2s	Mejor feedback visual
🔹 B. Pantalla de Fondo (Slideshow)
Elemento	Anterior	Mejorada	Razon
Opacidad	opacity: 2	opacity: 0.4	Mejor visibilidad
Animación	crossfade 20s	crossfade 25s	Más suave
Animación Keyframes	0%, 100% { opacity: 0 }	0%, 100% { opacity: 0.4 }	Mejor visibilidad
Accesibilidad	prefers-reduced-motion	prefers-reduced-motion	Accesibilidad
🔹 C. Paleta de Colores Institucionales
Categoría	Color	Uso
Fondo	#0f172a	Pantalla de fondo
Fondo Tarjeta	#f8fafc	Tarjeta glass
Texto Principal	#1e293b	Títulos
Texto Secundario	#334155	Labels
Acento Primario	#2563eb	Inputs focus
Acento Botón	#1e40af	Botón
Acento Hover	#1d4ed8	Hover
Error	#ef4444	Mensajes de error
Éxito	#22c55e	Mensajes de éxito
🖥️ 2. Mejoras de Experiencia de Usuario (UX)
🔹 A. Validaciones en Tiempo Real
jsx

const handleLogin = async (e) => {
  e.preventDefault();

  // Validaciones básicas
  if (!usuario.trim()) {
    setError("Por favor ingresa tu usuario.");
    return;
  }

  if (!password.trim()) {
    setError("Por favor ingresa tu contraseña.");
    return;
  }

  if (usuario.length < 3) {
    setError("El usuario debe tener al menos 3 caracteres.");
    return;
  }

  if (password.length < 8) {
    setError("La contraseña debe tener al menos 8 caracteres.");
    return;
  }

  // Validación de correo electrónico (opcional)
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (emailRegex.test(usuario)) {
    setError("El usuario no parece ser un correo válido.");
    return;
  }

  setError("");
  setLoading(true);
  try {
    const res = await api.post("/auth/login", { usuario, password });
    setTokens(res.data.token);
    navigate("/dashboard");
  } catch (err) {
    // Manejo de errores
    const errorMsg = err.response?.data?.message ||
                     err.response?.data?.errors?.[0]?.message ||
                     "Usuario o contraseña incorrectos.";
    setError(errorMsg);
  } finally {
    setLoading(false);
  }
};
🔹 B. Accesibilidad (A11y)
jsx

<div className="login-page" role="main" tabIndex={0}>
  <form 
    className="glass-card" 
    onSubmit={handleLogin} 
    noValidate
    aria-label="Formulario de inicio de sesión"
  >
    <h2>DatCorr</h2>


    {/* Contraseña */}


      
      <input
        id="password-input"
        name="password"
        type="password"
        placeholder="contraseña"
        autoComplete="current-password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        aria-required="true"
        aria-invalid={error ? "true" : "false"}
        aria-describedby="password-error"
        required
      />
      {error && 
      <span>Conexión cifrada (TLS)</span>
      
  );
}
🎯 4. Mejoras de Código y Mantenimiento
🔹 A. Separación de Concerns
Archivo	Contenido
Login.css	Estilos visuales
Login.jsx	Lógica de aplicación
api/axiosClient.js	Client de API
auth/authStore.js	Gestión de autenticación
🔹 B. Componente de Login Mejorado
jsx

import { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import api from "../api/axiosClient";
import { useAuthStore } from "../auth/authStore";
import "./Login.css";

export default function Login() {
  const navigate = useNavigate();
  const { tokens } = useAuthStore();

  const [usuario, setUsuario] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  // Verificar autenticación previa
  useEffect(() => {
    if (tokens) {
      navigate("/dashboard", { replace: true });
    }
  }, [tokens, navigate]);

  const handleLogin = async (e) => {
    e.preventDefault();

    setError("");
    setLoading(true);

    try {
      const res = await api.post("/auth/login", { usuario, password });
      setTokens(res.data.token);
      navigate("/dashboard");
    } catch (err) {
      const errorMsg = err.response?.data?.message ||
                      err.response?.data?.errors?.[0]?.message ||
                      "Usuario o contraseña incorrectos.";
      setError(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  return (
    


      {[1, 2, 3, 4, 5].map((i) => (
        <div key={i} className="slideshow-slide" />
      ))}

    <form className="glass-card" onSubmit={handleLogin} noValidate>

## DatCorr


    <label htmlFor="usuario-input">Usuario</label>
        <input
          id="usuario-input"
          name="usuario"
          type="text"
          placeholder="usuario"
          autoComplete="username"
          value={usuario}
          onChange={(e) => setUsuario(e.target.value)}
          aria-required="true"
        />

    <label htmlFor="password-input">Contraseña</label>
        <input
          id="password-input"
          name="password"
          type="password"
          placeholder="contraseña"
          autoComplete="current-password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          aria-required="true"
          aria-invalid={error ? "true" : "false"}
        />

    {error && (


        )}

    <button type="submit" disabled={loading} aria-busy={loading}>
          {loading ? "Ingresando…" : "Ingresar"}

    <div style={{ marginTop: 10, textAlign: "center" }}>
          <Link to="/forgot-password" style={{ fontSize: "0.85rem" }}>
            ¿Olvidaste tu contraseña?
        

    


          <span>Conexión cifrada (TLS)</span>
