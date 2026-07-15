import { BrowserRouter, Routes, Route } from "react-router-dom";

import Login from "../pages/Login";
import ForgotPassword from "../pages/ForgotPassword";
import ResetPassword from "../pages/ResetPassword";
import Dashboard from "../pages/Dashboard";
import UsuariosPage from "../pages/usuarios/UsuariosPage";
import DatabasePage from "../pages/DatabasePage";
import CargaDatosPage from "../pages/CargaDatosPage";
import AuditoriaPage from "../pages/AuditoriaPage";
import ReportesPage from "../pages/ReportesPage";

import PrivateRoute from "../auth/PrivateRoute";
import MainLayout from "../layouts/MainLayout";

export default function AppRouter() {
    return (
        <BrowserRouter>
            <Routes>

                {/* PUBLICO */}
                <Route path="/" element={<Login />} />
                <Route path="/forgot-password" element={<ForgotPassword />} />
                <Route path="/reset-password" element={<ResetPassword />} />

                {/* PRIVADO + LAYOUT ERP */}  
                <Route
                    element={
                        <PrivateRoute>
                            <MainLayout />
                        </PrivateRoute>
                    }
                >
                    <Route path="/dashboard" element={<Dashboard />} />
                    <Route path="/usuarios" element={<UsuariosPage />} />
                    <Route path="/reportes" element={<ReportesPage />} />
                    <Route path="/database" element={<DatabasePage />} />
                    <Route path="/carga-datos" element={<CargaDatosPage />} />
                    <Route path="/auditoria" element={<AuditoriaPage />} />

                {/* fallback */}
                <Route path="*" element={<Login />} />

                </Route>

            </Routes>
        </BrowserRouter>
    );
}