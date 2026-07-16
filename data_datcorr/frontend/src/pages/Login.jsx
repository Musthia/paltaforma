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
                username: usuario,
                password
            });
            const role = (res.data.user?.role || "").toLowerCase();
            if (role === "consulta") {
                window.location.href = "http://localhost:8000/simco/";
            } else {
                setTokens(res.data.access_token);
                navigate("/dashboard", { replace: true });
            }
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
                            {showPassword ? "\u{1F441}" : "\u{1F441}\u200D\u{1F5E8}\uFE0F"}
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
                    {loading ? "Ingresando\u2026" : "Ingresar"}
                </button>

                <div className="login-links">
                    <Link to="/forgot-password" className="forgot-link">
                        ¿Olvidaste tu contraseña?
                    </Link>
                </div>

                <div className="trust-footer">
                    <span>Conexión cifrada (TLS)</span>
                    <span>&bull;</span>
                    <span>Datos protegidos</span>
                </div>
            </form>
        </div>
    );
}
