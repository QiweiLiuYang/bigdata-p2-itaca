import os
import psycopg2
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

conexion = psycopg2.connect(
    host="localhost",
    port=5432,
    dbname=os.getenv("POSTGRES_DB"),
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD"),
)

query = """
    SELECT anyo, alumno, curso, contenido, evaluacion, nota_numerica, tipo_nota
    FROM calificaciones
    WHERE anyo >= %s
"""
df = pd.read_sql(query, conexion, params=(2025,))
os.makedirs("data/raw", exist_ok=True)
df.to_csv("data/raw/salida.csv", index=False)
df.to_excel("data/raw/salida.xlsx", index=False)
conexion.close()
