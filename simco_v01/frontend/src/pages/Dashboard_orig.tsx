import { useEffect, useState } from "react";
import { getUser } from "../auth/user";

export default function Dashboard() {
  const [user, setUser] = useState<any>(null);

  useEffect(() => {
    setUser(getUser());
  }, []);

  if (!user) return <div>No autenticado</div>;

  return (
    <div>
      <h1>SiMCo Dashboard</h1>

      <p>Usuario: {user.sub}</p>
      <p>Rol: {user.role}</p>

      <hr />

      {user.role === "admin" && <AdminPanel />}
      {user.role === "oficina" && <OficinaPanel />}
      {user.role === "deposito" && <DepositoPanel />}
      {user.role === "consulta" && <ConsultaPanel />}
    </div>
  );
}

function AdminPanel() {
  return <h2>Panel ADMIN - control total</h2>;
}

function OficinaPanel() {
  return <h2>Panel OFICINA - solicitudes</h2>;
}

function DepositoPanel() {
  return <h2>Panel DEPÓSITO - archivos</h2>;
}

function ConsultaPanel() {
  return <h2>Panel CONSULTA - solo lectura</h2>;
}