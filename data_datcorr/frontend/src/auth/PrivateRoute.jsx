import { Navigate } from "react-router-dom";
import { useAuthStore } from "./authStore";

export default function PrivateRoute({ children }) {

    const token = useAuthStore((s) => s.accessToken);

    if (!token) {
        return <Navigate to="/" replace />;
    }

    return children;
}