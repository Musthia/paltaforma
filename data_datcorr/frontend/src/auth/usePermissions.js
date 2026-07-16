import { useAuthStore } from "./authStore";

export const usePermissions = () => {

    const user = useAuthStore((s) => s.user);

    // 🔥 FALLBACK DE SEGURIDAD
    if (!user) {
        return {
            canViewUsers: false,
            canViewAuditoria: false,
            canViewReportes: false,
            canAccessSimco: false,
            canCreateUser: false,
            canEditUser: false,
            canDeleteUser: false,
            showNivelColumn: false,
            showRolColumn: false
        };
    }

    const nivel = user.nivel ?? 0;
    const isSuper = user.superusuario ?? false;

    const isAdmin = isSuper || nivel >= 10;

    const role = (user.role || "").toLowerCase();
    const allowedSimcoRoles = ["administrador", "supervisor", "operador"];
    const canAccessSimco = allowedSimcoRoles.includes(role);

    return {

        canViewUsers: isAdmin,
        canViewAuditoria: isAdmin,
        canViewReportes: true,
        canAccessSimco,

        canCreateUser: isAdmin,
        canEditUser: isAdmin,
        canDeleteUser: isSuper,

        showNivelColumn: isSuper || nivel >= 5,
        showRolColumn: true
    };
};