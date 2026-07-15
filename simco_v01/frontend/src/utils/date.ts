export const formatDateTime = (value: string) => {
    return new Date(value).toLocaleString("es-AR");
};

export const timeAgo = (value: string | Date): string => {
    const now = Date.now();
    const then = new Date(value).getTime();
    const diffSec = Math.floor((now - then) / 1000);
    if (diffSec < 60) return "hace unos segundos";
    const diffMin = Math.floor(diffSec / 60);
    if (diffMin < 60) return `hace ${diffMin} min`;
    const diffHr = Math.floor(diffMin / 60);
    if (diffHr < 24) return `hace ${diffHr} h`;
    const diffDay = Math.floor(diffHr / 24);
    if (diffDay === 1) return "ayer";
    return `hace ${diffDay} días`;
};