import type { CSSProperties } from "react";

export default function Acerca() {
  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <h1 style={styles.title}>Acerca de</h1>

        <section style={styles.section}>
          <h2 style={styles.sectionTitle}>SiMCo</h2>
          <p style={styles.text}>
            <strong>SiMCo</strong> (Sistema de Manejo de Consultas) es una plataforma
            diseñada para la gestión, trasabilidad y control de solicitudes y
            consultas. Permite a los usuarios crear solicitudes, adjuntar
            archivos, dar trasabilidad al estado, y recibir respuestas de forma
            organizada. Incluye roles diferenciados (oficina, depósito,
            consulta), notificaciones en tiempo real, auditoría de actividades y
            un sistema de búsqueda avanzada.
          </p>
        </section>

        <section style={styles.section}>
          <h2 style={styles.sectionTitle}>DATCORR S.A.</h2>
          <p style={styles.text}>
            <em>— DATCORR S.A. es una empresa de 
              servicios de informática y tecnología 
              con sede en la ciudad de Corrientes. 
              Fundada en 2012, su actividad principal 
              abarca el desarrollo de software, 
              la gestión informática 
              y la tecnología aplicada. —</em>
          </p>
          <p style={styles.text}>
            <strong>Razón Social:</strong> <em>(Datcorr)</em>
          </p>
          <p style={styles.text}>
            <strong>Dirección:</strong> <em>(SAN MARTIN 1270
                              CORRIENTES 
                              3400-CORRIENTES)</em>
          </p>
          <p style={styles.text}>
            <strong>Teléfono:</strong> <em>(+54-379-4996116)</em>
          </p>
          <p style={styles.text}>
            <strong>Correo:</strong> <em>(fabioeduardo304@hotmail.com)</em>
          </p>
        </section>

        <section style={styles.section}>
          <h2 style={styles.sectionTitle}>Versión</h2>
          <p style={styles.text}>v1.0.0</p>
        </section>
      </div>
    </div>
  );
}

const styles: Record<string, CSSProperties> = {
  container: {
    display: "flex",
    justifyContent: "center",
    padding: "40px 20px",
  },
  card: {
    maxWidth: 640,
    width: "100%",
    background: "#fff",
    borderRadius: 12,
    padding: "32px 40px",
    boxShadow: "0 2px 12px rgba(0,0,0,0.08)",
    border: "1px solid #e5e7eb",
  },
  title: {
    margin: "0 0 24px",
    fontSize: 24,
    fontWeight: 700,
    color: "#111827",
  },
  section: {
    marginBottom: 24,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: 600,
    color: "#374151",
    margin: "0 0 8px",
    paddingBottom: 6,
    borderBottom: "1px solid #e5e7eb",
  },
  text: {
    fontSize: 14,
    lineHeight: 1.7,
    color: "#4b5563",
    margin: "4px 0",
  },
};
