from setuptools import setup, find_packages

setup(
    name="platformcore",
    version="0.1.0",
    packages=find_packages(include=["platformcore", "platformcore.*"]),
    install_requires=[
        "fastapi>=0.128.0",
        "uvicorn>=0.39.0",
        "pydantic>=2.13.0",
        "SQLAlchemy>=2.0.0",
        "psycopg2-binary>=2.9.0",
        "passlib>=1.7.4",
        "bcrypt>=4.0.0",
        "python-jose>=3.5.0",
        "python-dotenv>=1.2.0",
        "starlette>=0.49.0",
    ],
)
