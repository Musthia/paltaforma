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
            const res = await api.post("/auth/login", { usuario, password });
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
        <div className="login-page">
            <div className="login-container" role="main" aria-label="Página de acceso al sistema">

                <section className="login-brand" aria-label="Información institucional">
                    <div className="brand-content">
                        <div className="brand-logo" aria-hidden="true">D</div>
                        <h1 className="brand-title">DatCorr</h1>
                        <p className="brand-description">
                            Digitalización, archivo y custodia segura de documentos institucionales.
                        </p>
                        <div className="brand-metrics" aria-label="Información del sistema">
                            <div className="metric-item">
                                <div className="metric-text">
                                    <span className="metric-value">160.000+</span>
                                    <span className="metric-label">Registros documentales</span>
                                </div>
                            </div>
                            <div className="metric-item">
                                <div className="metric-text">
                                    <span className="metric-value">12</span>
                                    <span className="metric-label">Usuarios del sistema</span>
                                </div>
                            </div>
                        </div>
                        <div className="brand-footer">
                            <span className="status-dot" aria-hidden="true"></span>
                            <span className="status-text">Sistema operativo</span>
                        </div>
                    </div>
                </section>

                <section className="login-form-panel" aria-label="Formulario de inicio de sesión">
                    <div className="form-wrapper">

                        <header className="form-header">
                            <h2 className="form-title">Iniciar sesión</h2>
                            <p className="form-subtitle">Ingrese sus credenciales de acceso</p>
                        </header>

                        {error && (
                            <div className="form-error" role="alert" aria-live="polite">
                                <span className="form-error-icon" aria-hidden="true">&#9888;</span>
                                {error}
                            </div>
                        )}

                        <form onSubmit={handleLogin} noValidate>

                            <div className="form-group">
                                <label htmlFor="usuario-input" className="form-label">Usuario</label>
                                <input
                                    id="usuario-input"
                                    name="usuario"
                                    type="text"
                                    className="form-input"
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
                                <label htmlFor="password-input" className="form-label">Contraseña</label>
                                <div className="password-wrapper">
                                    <input
                                        id="password-input"
                                        name="password"
                                        type={showPassword ? "text" : "password"}
                                        className="form-input"
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

                            <button
                                type="submit"
                                className="login-button"
                                disabled={loading || !usuario.trim() || !password.trim()}
                            >
                                {loading ? <span className="spinner" aria-hidden="true" /> : null}
                                {loading ? "Ingresando\u2026" : "Acceder al sistema"}
                            </button>

                        </form>

                        <div className="form-links">
                            <Link to="/forgot-password" className="form-link">
                                ¿Olvidó su contraseña?
                            </Link>
                        </div>

                        <footer className="trust-footer">
                            <span>Conexión cifrada (TLS)</span>
                            <span>&bull;</span>
                            <span>Datos protegidos</span>
                        </footer>

                    </div>
                </section>

            </div>
        </div>
    );
}
