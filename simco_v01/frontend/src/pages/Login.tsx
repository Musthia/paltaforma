import { useEffect, useState } from "react";
import type { CSSProperties } from "react";
import { useNavigate } from "react-router-dom";
import { loginRequest, refreshTokenRequest } from "../api/auth";
import { getAccessToken, getRefreshToken, setTokens, isTokenExpired } from "../auth/token";

export default function Login() {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");

    const navigate = useNavigate();

    useEffect(() => {
        const access = getAccessToken();
        if (access && !isTokenExpired(access)) {
            navigate("/dashboard", { replace: true });
            return;
        }
        const refresh = getRefreshToken();
        if (refresh) {
            refreshTokenRequest(refresh)
                .then((data) => {
                    setTokens(data.access_token, data.refresh_token);
                    navigate("/dashboard", { replace: true });
                })
                .catch(() => {});
        }
    }, [navigate]);

    const handleLogin = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();

        try {
            const data = await loginRequest(username, password);

            setTokens(
                data.access_token,
                data.refresh_token
            );

            navigate("/dashboard");
        } catch (error) {
            console.error(error);
            alert("Error de login");
        }
    };

    return (
        <div style={styles.container}>
            <form
                style={styles.form}
                onSubmit={handleLogin}
            >
                <div style={styles.titleContainer}>
                    <h1 style={styles.title}>SiMCo</h1>

                    <p style={styles.subtitle}>
                        (Sistema de Manejo de Consultas)
                    </p>

                    <h3 style={styles.loginText}>Login</h3>
                </div>

                <input
                    style={styles.input}
                    type="text"
                    placeholder="Usuario"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                />

                <input
                    style={styles.input}
                    type="password"
                    placeholder="Contraseña"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                />

                <button
                    type="submit"
                    style={styles.button}
                >
                    Iniciar sesión
                </button>
            </form>
        </div>
    );
}

<img src="/logo.png" alt="SIGE" />
const styles: Record<string, CSSProperties> = {
    container: {
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        minHeight: "100vh",
        backgroundColor: "#313133",
    },

    form: {
        display: "flex",
        flexDirection: "column",
        gap: "12px",
        width: "320px",
        padding: "30px",
        backgroundColor: "#3c3c4d",
        borderRadius: "10px",
        boxShadow: "0 4px 15px rgba(0,0,0,0.3)",
    },

    titleContainer: {
        textAlign: "center",
        color: "white",
        marginBottom: "15px",
    },

    title: {
        margin: 0,
        fontSize: "32px",
        fontWeight: "bold",
    },

    subtitle: {
        margin: "5px 0",
        fontSize: "14px",
        opacity: 0.8,
    },

    loginText: {
        margin: 0,
        fontSize: "18px",
    },

    input: {
        padding: "10px",
        borderRadius: "5px",
        border: "1px solid #444",
        fontSize: "14px",
    },

    button: {
        padding: "10px",
        border: "none",
        borderRadius: "5px",
        backgroundColor: "#4f46e5",
        color: "#ffffff",
        fontWeight: "bold",
        cursor: "pointer",
    },
};