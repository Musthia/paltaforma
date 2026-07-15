# ── 1. Construir frontend ──
FROM node:20 AS frontend
WORKDIR /app
COPY frontend/package*.json ./frontend/
RUN cd frontend && npm ci
COPY frontend/ ./frontend/
RUN cd frontend && npm run build

# ── 2. Backend ──
FROM python:3.13-slim
WORKDIR /app

# Copiar frontend compilado
COPY --from=frontend /app/frontend/dist ./frontend/dist

# Dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ ./backend/

# Puerto dinámico (Railway asigna $PORT)
EXPOSE 8000

# Inicio (el seed se ejecuta dentro del lifespan de la app)
CMD ["sh", "-c", "cd backend && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
