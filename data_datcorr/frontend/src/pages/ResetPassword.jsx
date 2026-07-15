import { useState } from "react";
import { useSearchParams, Link } from "react-router-dom";
import api from "../api/axiosClient";
import "./Login.css";

export default function ResetPassword() {
    const [searchParams] = useSearchParams();
    const token = searchParams.get("token") || "";

    const [password, setPassword] = useState("");
    const [confirm, setConfirm] = useState("");
    const [error, setError] = useState("");
    const [success, setSuccess] = useState(false);
    const [loading, setLoading] = useState(false);
    const [showPassword, setShowPassword] = useState(false);
    const [showConfirm, setShowConfirm] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError("");

        if (password !== confirm) {
            setError("Las contraseñas no coinciden.");
            return;
        }
        if (password.length < 6) {
            setError("La contraseña debe tener al menos 6 caracteres.");
            return;
        }

        setLoading(true);
        try {
            await api.post("/auth/reset-password", { token, nueva_password: password });
            setSuccess(true);
        } catch (err) {
            setError(err.response?.data?.detail || "Token inválido o expirado.");
        } finally {
            setLoading(false);
        }
    };

    if (!token) {
        return (
            <div className="login-page" role="main">
                {[1, 2, 3, 4, 5].map((i) => (
                    <div key={i} className="slideshow-slide" />
                ))}
                <div className="glass-card" style={{ textAlign: "center" }}>
                    <div className="login-header">
                        <h1>Enlace inválido</h1>
                        <p className="login-subtitle">El enlace no contiene un token de recuperación.</p>
                    </div>
                    <Link to="/forgot-password" className="forgot-link">Solicitar nuevo</Link>
                    <div className="trust-footer">
                        <span>Conexión cifrada (TLS)</span>
                        <span>&bull;</span>
                        <span>Datos protegidos</span>
                    </div>
                </div>
            </div>
        );
    }

    if (success) {
        return (
            <div className="login-page" role="main">
                {[1, 2, 3, 4, 5].map((i) => (
                    <div key={i} className="slideshow-slide" />
                ))}
                <div className="glass-card" style={{ textAlign: "center" }}>
                    <div className="login-header">
                        <h1>Contraseña actualizada</h1>
                        <p className="login-subtitle">Ya podés iniciar sesión con tu nueva contraseña.</p>
                    </div>
                    <Link to="/" className="forgot-link">Ir al inicio</Link>
                    <div className="trust-footer">
                        <span>Conexión cifrada (TLS)</span>
                        <span>&bull;</span>
                        <span>Datos protegidos</span>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="login-page" role="main">
            {[1, 2, 3, 4, 5].map((i) => (
                <div key={i} className="slideshow-slide" />
            ))}

            <form className="glass-card" onSubmit={handleSubmit} noValidate>
                <div className="login-header">
                    <h1>Nueva contraseña</h1>
                    <p className="login-subtitle">Ingresá tu nueva contraseña</p>
                </div>

                <div className="form-group">
                    <label htmlFor="pw-input">Nueva contraseña</label>
                    <div className="password-wrapper">
                        <input
                            id="pw-input"
                            name="password"
                            type={showPassword ? "text" : "password"}
                            placeholder="mín. 6 caracteres"
                            autoComplete="new-password"
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

                <div className="form-group">
                    <label htmlFor="confirm-input">Confirmar contraseña</label>
                    <div className="password-wrapper">
                        <input
                            id="confirm-input"
                            name="confirm"
                            type={showConfirm ? "text" : "password"}
                            placeholder="repetir contraseña"
                            autoComplete="new-password"
                            value={confirm}
                            onChange={(e) => setConfirm(e.target.value)}
                            required
                            aria-required="true"
                            aria-invalid={!!error}
                            disabled={loading}
                        />
                        <button
                            type="button"
                            className="toggle-password"
                            onClick={() => setShowConfirm(!showConfirm)}
                            aria-label={showConfirm ? "Ocultar contraseña" : "Mostrar contraseña"}
                        >
                            {showConfirm ? "\u{1F441}" : "\u{1F441}\u200D\u{1F5E8}\uFE0F"}
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
                    disabled={loading || !password.trim() || !confirm.trim()}
                    className="login-button"
                >
                    {loading ? (
                        <span className="spinner" aria-hidden="true" />
                    ) : null}
                    {loading ? "Actualizando\u2026" : "Actualizar contraseña"}
                </button>

                <div className="login-links">
                    <Link to="/" className="forgot-link">Volver al inicio</Link>
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
