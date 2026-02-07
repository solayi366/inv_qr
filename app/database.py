import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import urllib

# --- CONFIGURACIÓN DE BASE DE DATOS ---

# Si estas variables de entorno existen (en AWS), las usa. 
# Si no, usa tus valores locales por defecto.
SERVER = os.getenv('DB_SERVER', '06TEC02') 
DATABASE = os.getenv('DB_NAME', 'inv_qr') 
USERNAME = os.getenv('DB_USER', '') 
PASSWORD = os.getenv('DB_PASSWORD', '')

if USERNAME and PASSWORD:
    # CONEXIÓN NUBE (SQL Authentication)
    params = urllib.parse.quote_plus(
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={SERVER};"
        f"DATABASE={DATABASE};"
        f"UID={USERNAME};"
        f"PWD={PASSWORD};"
    )
else:
    # CONEXIÓN LOCAL (Windows Authentication)
    params = urllib.parse.quote_plus(
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={SERVER};"
        f"DATABASE={DATABASE};"
        f"Trusted_Connection=yes;"
    )

SQLALCHEMY_DATABASE_URL = f"mssql+pyodbc:///?odbc_connect={params}"

# Crear el motor
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Crear sesión
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()