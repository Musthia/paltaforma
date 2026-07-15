import { useEffect, useState } from "react";
import { listarUsuarios } from "../services/usuariosService";

export const useUsuarios = (filters = {}) => {

    const [data, setData] = useState([]);
    const [meta, setMeta] = useState({});
    const [loading, setLoading] = useState(false);

    const fetch = async () => {

        try {
            setLoading(true);

            const res = await listarUsuarios({
                page: 1,
                limit: 20,
                ...filters
            });

            setData(res.usuarios);
            setMeta(res);

        } catch (err) {
            console.error("ERP USERS ERROR:", err);
            setData([]);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetch();
    }, [JSON.stringify(filters)]);

    return {
        data,
        meta,
        loading,
        refresh: fetch
        
    };
};