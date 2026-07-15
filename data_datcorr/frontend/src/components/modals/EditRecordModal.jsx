import { useState, useEffect } from "react";
import {
    Drawer,
    Box,
    Typography,
    Button,
    TextField,
} from "@mui/material";
import { actualizarRegistro } from "../../services/databaseService";

export default function EditRecordModal({
    open,
    onClose,
    onSaved,
    base,
    idRegistro,
    columnas,
    valores,
}) {
    const [form, setForm] = useState({});
    const [saving, setSaving] = useState(false);

    useEffect(() => {
        if (open && columnas && valores) {
            const initial = {};
            columnas.forEach((col, i) => {
                initial[col] = valores[i] != null ? String(valores[i]) : "";
            });
            setForm(initial);
        }
    }, [open, columnas, valores]);

    const handleChange = (e) => {
        setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));
    };

    const handleSave = async () => {
        setSaving(true);
        try {
            const data = {};
            columnas.forEach((col) => {
                if (!col.toLowerCase().startsWith("id_datcorr")) {
                    data[col] = form[col];
                }
            });
            await actualizarRegistro(base, idRegistro, data);
            onSaved();
        } catch (err) {
            console.error("Error actualizando registro:", err);
        } finally {
            setSaving(false);
        }
    };

    const columnasEditables = columnas.filter(
        (col) => !col.toLowerCase().startsWith("id_datcorr") && col.toLowerCase() !== "registro"
    );

    return (
        <Drawer anchor="right" open={open} onClose={onClose}>
            <Box sx={{ width: 450, p: 3 }}>
                <Typography variant="h6" gutterBottom>
                    Editar Registro - {base}
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    ID: {idRegistro}
                </Typography>

                {columnasEditables.map((col) => (
                    <TextField
                        key={col}
                        margin="dense"
                        label={col}
                        name={col}
                        fullWidth
                        size="small"
                        value={form[col] || ""}
                        onChange={handleChange}
                        InputProps={{
                            readOnly: false,
                        }}
                    />
                ))}

                <Box sx={{ mt: 3, display: "flex", gap: 2 }}>
                    <Button variant="contained" onClick={handleSave} disabled={saving}>
                        {saving ? "Guardando..." : "Guardar cambios"}
                    </Button>
                    <Button variant="outlined" onClick={onClose}>
                        Cancelar
                    </Button>
                </Box>
            </Box>
        </Drawer>
    );
}
