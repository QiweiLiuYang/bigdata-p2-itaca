import os, json, logging, psycopg2, psycopg2.extras, hashlib
from datetime import date
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ingesta_itaca_db")

TABLAS = {
    "alumnos": ["anyo", "nia", "sexo", "nacionalidad", "provincia", "municipio", "ensenanza", "curso", "grupo", "turno", "linea", "modalidad", "repite", "estado_matricula", "tipo_matricula", "fecha_matricula", "fecha_ingreso_centro"],
    "cursos": ["anyo", "codigo", "nombre_cas", "nombre_val", "abreviatura", "ensenanza", "padre"],
    "calificaciones": ["anyo", "evaluacion", "alumno", "ensenanza", "curso", "contenido", "bloque_contenido", "nota_numerica", "tipo_nota"],
    "contenidos": ["anyo", "codigo", "nombre_cas", "nombre_val", "ensenanza", "curso"]
}

def conectar():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST"), port=os.getenv("POSTGRES_PORT"),
        dbname=os.getenv("POSTGRES_DB"), user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )


def anonimizar_nia(nia: str) -> str:
    return hashlib.sha256(str(nia).encode()).hexdigest()[:10]


def extraer_tabla(conexion, tabla:str) -> list[dict]:
    with conexion.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(f"SELECT {', '.join(TABLAS[tabla])} FROM {tabla}")
        registros = []
        for fila in cur.fetchall():
            if tabla == "alumnos":
                fila["nia"] = anonimizar_nia(fila["nia"])
            if tabla == "calificaciones":
                fila["alumno"] = anonimizar_nia(fila["alumno"])
            registros.append(dict(fila))
        return registros


def guardar(datos: list[dict], nombre: str) -> None:
    fecha = date.today().isoformat()
    ruta = f"data/raw/{nombre}_{fecha}.json"
    os.makedirs("data/raw", exist_ok=True)
    with open(ruta, "w", encoding="UTF-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2, default=str)
    logger.info("Guardados %d registros en %s", len(datos), ruta)


if __name__ == "__main__":
    conexion = None
    try:
        conexion = conectar()
        for tabla in TABLAS:
            guardar(extraer_tabla(conexion, tabla), tabla)
    except Exception:
        logger.exception("La ingesta ha fallado")
        raise SystemExit(1)
    finally:
        if conexion:
            conexion.close()