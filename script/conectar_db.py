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
    WHERE anyo = %s
"""

anyos = [2021, 2022, 2023, 2024, 2025]
os.makedirs("data/raw", exist_ok=True)

for anyo in anyos:
    df = pd.read_sql(query, conexion, params=(anyo,))
    df.to_csv(f"data/raw/calificaciones_{anyo}.csv", index=False)

conexion.close()
