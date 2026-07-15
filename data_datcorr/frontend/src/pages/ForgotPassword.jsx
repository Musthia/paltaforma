import { useState } from "react";
import { Link } from "react-router-dom";
import api from "../api/axiosClient";
import "./Login.css";

export default function ForgotPassword() {
    const [email, setEmail] = useState("");
    const [sent, setSent] = useState(false);
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError("");
        setLoading(true);
        try {
            await api.post("/auth/forgot-password", { email });
            setSent(true);
        } catch {
            setError("Error al procesar la solicitud.");
        } finally {
            setLoading(false);
        }
    };

    if (sent) {
        return (
            <div className="login-page" role="main">
                {[1, 2, 3, 4, 5].map((i) => (
                    <div key={i} className="slideshow-slide" />
                ))}
                <div className="glass-card" style={{ textAlign: "center" }}>
                    <div className="login-header">
                        <h1>Revisa tu correo</h1>
                        <p className="login-subtitle">Si el correo existe, recibirás instrucciones para restablecer tu contraseña.</p>
                    </div>
                    <Link to="/" className="forgot-link">Volver al inicio</Link>
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
                    <h1>Recuperar contraseña</h1>
                    <p className="login-subtitle">Ingresá tu correo electrónico</p>
                </div>

                <div className="form-group">
                    <label htmlFor="email-input">Correo electrónico</label>
                    <input
                        id="email-input"
                        name="email"
                        type="email"
                        placeholder="correo@empresa.com"
                        autoComplete="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        required
                        aria-required="true"
                        disabled={loading}
                    />
                </div>

                {error && (
                    <div className="login-error" role="alert" aria-live="polite">
                        {error}
                    </div>
                )}

                <button
                    type="submit"
                    disabled={loading || !email.trim()}
                    className="login-button"
                >
                    {loading ? (
                        <span className="spinner" aria-hidden="true" />
                    ) : null}
                    {loading ? "Enviando\u2026" : "Enviar"}
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
