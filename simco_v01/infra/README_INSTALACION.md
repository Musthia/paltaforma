
# SiMCo - Instalación de Desarrollo

## Requisitos

* Python 3.13
* PostgreSQL 17
* NodeJS LTS
* Git

## Clonar proyecto

git clone REPOSITORIO

## Backend

cd backend

python -m venv venv

venv\Scripts\activate

pip install -r ..\infra\requirements_backend.txt

## Crear usuario PostgreSQL

Ejecutar create_user.sql

## Crear base PostgreSQL

Ejecutar create_database.sql

## Configurar .env

DATABASE_URL=postgresql://simco_user:Simco2026@localhost:5432/simco

## Ejecutar backend

uvicorn app.main:app --reload

## Frontend

cd frontend

npm install

npm run dev

## URLs

Backend:
http://localhost:8000

Swagger:
http://localhost:8000/docs

Frontend:
http://localhost:5173
