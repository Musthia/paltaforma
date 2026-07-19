# ── Etapa 1: Build frontend DATCORR ──
FROM node:20 AS datcorr-frontend
WORKDIR /app/data_datcorr/frontend
COPY data_datcorr/frontend/package*.json ./
RUN npm ci
COPY data_datcorr/frontend/ ./
RUN npm run build

# ── Etapa 2: Build frontend SIMCO ──
FROM node:20 AS simco-frontend
WORKDIR /app/simco_v01/frontend
COPY simco_v01/frontend/package*.json ./
RUN npm ci
COPY simco_v01/frontend/ ./
RUN npm run build

# ── Etapa 3: Backend Python ──
FROM python:3.13-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc postgresql-client && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY platformcore/ ./platformcore/
COPY simco_v01/backend/ ./simco_v01/backend/
COPY data_datcorr/ ./data_datcorr/

COPY --from=datcorr-frontend /app/data_datcorr/frontend/dist ./data_datcorr/frontend/dist
COPY --from=simco-frontend /app/simco_v01/frontend/dist ./simco_v01/frontend/dist

COPY requirements-web.txt .
RUN pip install --no-cache-dir -r requirements-web.txt

RUN apt-get purge -y --auto-remove gcc && rm -rf /var/lib/apt/lists/*

ENV DB_ENGINE=postgres
ENV PLATFORM_DB_ENGINE=postgres
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

WORKDIR /app/data_datcorr
CMD ["sh", "-c", "uvicorn backend.main_unificado:app --host 0.0.0.0 --port ${PORT:-8000}"]
