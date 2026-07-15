
# SIMCO

## Crear entorno virtual

python -m venv venv

## Activar

venv\Scripts\activate

## Instalar dependencias

pip install -r requirements.txt

## Configurar .env

DB_HOST=localhost
DB_PORT=5432
DB_NAME=simco
DB_USER=postgres
DB_PASSWORD=xxxxx

## Ejecutar

uvicorn app.main:app --reload
