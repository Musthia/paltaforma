import { useEffect, useState } from "react";
import { listarUsuarios } from "../services/usuariosService";

export const useUsuariosGrid = () => {

    const [rows, setRows] = useState([]);
    const [loading, setLoading] = useState(false);
    const [pagination, setPagination] = useState({
        page: 0,
        pageSize: 20,
        total: 0
    });

    const fetchData = async (page = 0, pageSize = 20) => {

        try {
            setLoading(true);

            const data = await listarUsuarios({
                page: page + 1,
                limit: pageSize
            });

            setRows(data.usuarios || []);
            setPagination({
                page,
                pageSize,
                total: data.total || 0
            });

        } catch (err) {
            console.error("GRID ERROR:", err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData(0, 20);
    }, []);

    return {
        rows,
        loading,
        pagination,
        fetchData
    };
};
