import {
    Drawer,
    Box,
    Typography,
    Button,
    TextField,
    FormControl,
    InputLabel,
    Select,
    MenuItem,
    Alert,
} from "@mui/material";

import { useState, useEffect } from "react";

import {
    actualizarUsuario,
    crearUsuario
} from "../../services/usuariosService";

const extraerMensaje = (err) => {
    const data = err?.response?.data;
    if (data) {
        if (typeof data.detail === "string") {
            return data.detail;
        }
        if (data.mensaje) {
            return data.mensaje;
        }
    }
    return err?.message || "Ocurrió un error al guardar el usuario.";
};



export default function UsuarioModal({
    open,
    onClose,
    onSave,
    usuario = null
}) {

    const [form, setForm] = useState({
        usuario: "",
        password: "",
        nombre: "",
        apellido: "",
        email: "",
        rol: "",
        nivel_seguridad: ""
    });

    const [error, setError] = useState("");

    useEffect(() => {

        if (usuario) {

            setForm({
                usuario: usuario.usuario || "",
                password: "",
                nombre: usuario.nombre || "",
                apellido: usuario.apellido || "",
                email: usuario.email || "",
                rol: usuario.rol || "",
                nivel_seguridad: usuario.nivel_seguridad || ""
            });

        } else {

            setForm({
                usuario: "",
                password: "",
                nombre: "",
                apellido: "",
                email: "",
                rol: "",
                nivel_seguridad: ""
            });

        }

        setError("");

    }, [usuario]);

    const handleSave = async () => {
        try {

            const payload = {
                usuario: form.usuario,
                nombre: form.nombre,
                apellido: form.apellido,
                email: form.email,
                rol: form.rol,
                nivel_seguridad: Number(form.nivel_seguridad)
            };

            if (form.password) {
                payload.password = form.password;
            }

            if (usuario) {
                await actualizarUsuario(usuario.id, payload);
            } else {
                await crearUsuario({
                    ...payload,
                    password: form.password
                });
            }
        
            onSave();   // solo refresca grid
            onClose();  // cierra modal

        } catch (err) {
            console.error("ERROR CREANDO USUARIO:", err);
            setError(extraerMensaje(err));
        }
    };
    
    const handleChange = (e) => {

        setForm({
            ...form,
            [e.target.name]: e.target.value
        });
    };

    return (

        <Drawer anchor="right" open={open} onClose={onClose}>

            <Box sx={{ width: 400, padding: 2 }}>
            
                <Typography variant="h6">
                    {usuario ? "Editar Usuario" : "Nuevo Usuario"}
                </Typography>

                {error && (
                    <Alert
                        severity="error"
                        sx={{ mt: 1, mb: 1 }}
                        onClose={() => setError("")}
                    >
                        {error}
                    </Alert>
                )}

                <TextField
                    margin="dense"
                    label="Usuario"
                    name="usuario"
                    fullWidth
                    value={form.usuario}
                    onChange={handleChange}
                />

                <TextField
                    margin="dense"
                    label="Nombre"
                    name="nombre"
                    fullWidth
                    value={form.nombre}
                    onChange={handleChange}
                />

                <TextField
                    margin="dense"
                    label="Password"
                    name="password"
                    type="password"
                    fullWidth
                    value={form.password || ""}
                    onChange={handleChange}
                />

                <TextField
                    margin="dense"
                    label="Apellido"
                    name="apellido"
                    fullWidth
                    value={form.apellido}
                    onChange={handleChange}
                />

                <TextField
                    margin="dense"
                    label="Email"
                    name="email"
                    type="email"
                    fullWidth
                    value={form.email || ""}
                    onChange={handleChange}
                />

                <FormControl fullWidth margin="dense">
                    <InputLabel id="rol-label">Rol</InputLabel>
                    <Select
                        labelId="rol-label"
                        label="Rol"
                        name="rol"
                        value={form.rol}
                        onChange={handleChange}
                    >
                        <MenuItem value="Administrador">Administrador</MenuItem>
                        <MenuItem value="Supervisor">Supervisor</MenuItem>
                        <MenuItem value="Operador">Operador</MenuItem>
                        <MenuItem value="Consulta">Consulta</MenuItem>
                    </Select>
                </FormControl>

                <FormControl fullWidth margin="dense">
                    <InputLabel id="nivel-label">Nivel</InputLabel>
                    <Select
                        labelId="nivel-label"
                        label="Nivel"
                        name="nivel_seguridad"
                        value={form.nivel_seguridad}
                        onChange={handleChange}
                    >
                        <MenuItem value={0}>0</MenuItem>
                        <MenuItem value={1}>1</MenuItem>
                        <MenuItem value={2}>2</MenuItem>
                        <MenuItem value={3}>3</MenuItem>
                        <MenuItem value={5}>5</MenuItem>
                        <MenuItem value={10}>10</MenuItem>
                        <MenuItem value={9999}>9999</MenuItem>
                    </Select>
                </FormControl>

            <Button onClick={handleSave}>
                Guardar
            </Button>

            <Button onClick={onClose}>
                Cancelar
            </Button>

        </Box>

    </Drawer>
        );
    }
