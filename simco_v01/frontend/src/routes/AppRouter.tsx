import { BrowserRouter, Routes, Route } from "react-router-dom";
import Login from "../pages/Login";
import MainLayout from "../layout/MainLayout";

import { TabProvider } from "../tabs/TabContext";

export default function AppRouter() {
    return (
        <BrowserRouter>
            <Routes>
                <Route path="/" element={<Login />} />

                <Route element={<TabProvider><MainLayout /></TabProvider>}>
                    <Route path="/dashboard" element={null} />
                    <Route path="/solicitudes" element={null} />
                    <Route path="/respuestas" element={null} />
                    <Route path="/usuarios" element={null} />
                    <Route path="/auditoria" element={null} />
                </Route>
            </Routes>
        </BrowserRouter>
    );
}