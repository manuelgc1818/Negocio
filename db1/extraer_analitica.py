
import mysql.connector
import json
from datetime import datetime, date
from decimal import Decimal


# Conversor para manejar fechas y decimales en JSON
def convertir_tipos(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()

    if isinstance(obj, Decimal):
        return float(obj)

    raise TypeError(f"Tipo {type(obj)} no es serializable en JSON")


# Configuración de conexión a MySQL en Docker
config_base = {
    "user": "root",
    "password": "admin1234",
    "host": "127.0.0.1",
    "port": 3306,
    "database": "bd1"
}


def generar_json_bd1():
    conexion = None
    cursor = None

    try:
        conexion = mysql.connector.connect(**config_base)
        cursor = conexion.cursor(dictionary=True)

        # Consulta analítica de incidencias y costes municipales
        query = """
            SELECT
                m.nombre AS municipio,
                m.provincia,
                c.nombre AS categoria_incidencia,
                COUNT(DISTINCT i.id_incidencia) AS total_incidencias,
                COUNT(DISTINCT CASE
                    WHEN i.estado = 'RESUELTA'
                    THEN i.id_incidencia
                END) AS incidencias_resueltas,
                COUNT(DISTINCT CASE
                    WHEN i.estado != 'RESUELTA'
                    THEN i.id_incidencia
                END) AS incidencias_pendientes,
                ROUND(AVG(act.coste_estimado), 2)
                    AS coste_medio_actuaciones,
                ROUND(SUM(act.coste_estimado), 2)
                    AS coste_total_actuaciones
            FROM INCIDENCIA i
            INNER JOIN CATEGORIA c
                ON i.id_categoria = c.id_categoria
            INNER JOIN ZONA z
                ON i.id_zona = z.id_zona
            INNER JOIN MUNICIPIO m
                ON z.id_municipio = m.id_municipio
            LEFT JOIN ASIGNACION a
                ON i.id_incidencia = a.id_incidencia
            LEFT JOIN ACTUACION act
                ON a.id_asignacion = act.id_asignacion
            GROUP BY
                m.nombre,
                m.provincia,
                c.nombre
            ORDER BY coste_total_actuaciones DESC;
        """

        cursor.execute(query)
        resultados = cursor.fetchall()

        estructura_json = {
            "metadata": {
                "base_datos": "bd1",
                "objetivo": (
                    "Análisis de impacto económico y volumen "
                    "de incidencias por municipio"
                ),
                "fecha_extraccion": datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            },
            "resumen_analitico": resultados
        }

        # Guardar los resultados en un archivo JSON
        with open(
            "analitica_bd1_incidencias.json",
            "w",
            encoding="utf-8"
        ) as archivo:
            json.dump(
                estructura_json,
                archivo,
                indent=4,
                ensure_ascii=False,
                default=convertir_tipos
            )

        print(
            "Archivo 'analitica_bd1_incidencias.json' "
            "generado correctamente."
        )

    except mysql.connector.Error as error:
        print(f"Error de conexión o consulta MySQL: {error}")

    except (OSError, TypeError, ValueError) as error:
        print(f"Error al generar el JSON: {error}")

    finally:
        if cursor is not None:
            cursor.close()

        if conexion is not None and conexion.is_connected():
            conexion.close()


if __name__ == "__main__":
    generar_json_bd1()
