import { useAuthStore } from "./authStore";

export const usePermissions = () => {

    const user = useAuthStore((s) => s.user);

    // 🔥 FALLBACK DE SEGURIDAD
    if (!user) {
        return {
            canViewUsers: false,
            canViewAuditoria: false,
            canViewReportes: false,
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

    return {

        canViewUsers: isAdmin,
        canViewAuditoria: isAdmin,
        canViewReportes: true,

        canCreateUser: isAdmin,
        canEditUser: isAdmin,
        canDeleteUser: isSuper,

        showNivelColumn: isSuper || nivel >= 5,
        showRolColumn: true
    };
};