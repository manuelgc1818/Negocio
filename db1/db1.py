import mysql.connector
from faker import Faker
from datetime import datetime, timedelta
from decimal import Decimal
import random

# ============================================================
# PROVIDERS DE FAKER UTILIZADOS
# ============================================================
#
# 1. Address: fake.city(), fake.state(), fake.postcode()
# 2. Lorem: fake.word(), fake.sentence(), fake.paragraph()
# 3. Random: fake.random_int(), fake.random_element()
# 4. DateTime: fake.date_time_between()
# 5. Geo: fake.latitude(), fake.longitude()
# 6. Person: fake.name(), fake.first_name(), fake.last_name()
# 7. File: fake.file_name(), fake.file_path()
# 8. Internet: fake.url(), fake.email()
# 9. UUID: fake.uuid4()
# 10. Company: fake.company(), fake.company_suffix()
# 11. Color: fake.color_name()
# 12. PhoneNumber: fake.phone_number()
#
# Nota: algunos providers están disponibles en Faker en español
# y otros pueden generar resultados en inglés. Los métodos
# utilizados son los providers y métodos de Faker.
#
# ============================================================
# CONFIGURACIÓN DE LA BASE DE DATOS
# ============================================================

config = {
    "user": "root",
    "password": "admin1234",
    "host": "127.0.0.1",
    "port": 3306,
    "database": "bd1",
}

fake = Faker("es_ES")
random.seed()

cnx = None

# Listas para guardar las claves primarias generadas
municipio_ids = []
zona_ids = []
categoria_ids = []
incidencia_ids = []
equipo_ids = []
trabajador_ids = []
asignacion_ids = []

estados = ["Pendiente", "En proceso", "Resuelta"]

# ============================================================
# CONEXIÓN CON MYSQL
# ============================================================

try:
    cnx = mysql.connector.connect(**config)

    with cnx.cursor() as cursor:

        # ====================================================
        # 1. MUNICIPIO
        # ====================================================

        print("Insertando municipios...")

        for _ in range(5):
            cursor.execute(
                """
                INSERT INTO MUNICIPIO
                    (nombre, provincia, codigo_postal)
                VALUES (%s, %s, %s)
                """,
                (
                    fake.city(),
                    fake.state(),
                    fake.postcode(),
                ),
            )

            municipio_ids.append(cursor.lastrowid)

        # ====================================================
        # 2. ZONA
        # ====================================================

        print("Insertando zonas...")

        for id_municipio in municipio_ids:
            for _ in range(2):
                cursor.execute(
                    """
                    INSERT INTO ZONA
                        (nombre, id_municipio)
                    VALUES (%s, %s)
                    """,
                    (
                        f"Zona {fake.word().capitalize()}",
                        id_municipio,
                    ),
                )

                zona_ids.append(cursor.lastrowid)

        # ====================================================
        # 3. CATEGORIA
        # ====================================================

        print("Insertando categorías...")

        categorias = [
            ("Alumbrado", "Incidencias de alumbrado público.", 4),
            ("Vías Públicas", "Problemas en calles y aceras.", 5),
            ("Limpieza", "Incidencias de limpieza urbana.", 3),
            ("Jardinería", "Mantenimiento de jardines.", 2),
            ("Seguridad", "Incidencias de seguridad urbana.", 5),
        ]

        for nombre, descripcion, prioridad in categorias:
            cursor.execute(
                """
                INSERT INTO CATEGORIA
                    (nombre, descripcion, prioridad_base)
                VALUES (%s, %s, %s)
                """,
                (nombre, descripcion, prioridad),
            )

            categoria_ids.append(cursor.lastrowid)

        # ====================================================
        # 4. INCIDENCIA
        # ====================================================

        print("Insertando incidencias...")

        for _ in range(20):
            fecha = fake.date_time_between(
                start_date="-90d",
                end_date="now",
            )

            cursor.execute(
                """
                INSERT INTO INCIDENCIA (
                    id_categoria,
                    id_zona,
                    fecha_creacion,
                    descripcion,
                    latitud,
                    longitud,
                    estado,
                    prioridad
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    random.choice(categoria_ids),
                    random.choice(zona_ids),
                    fecha,
                    fake.paragraph(nb_sentences=3),
                    Decimal(fake.latitude()).quantize(
                        Decimal("0.000001")
                    ),
                    Decimal(fake.longitude()).quantize(
                        Decimal("0.000001")
                    ),
                    random.choice(estados),
                    fake.random_int(min=1, max=5),
                ),
            )

            incidencia_ids.append(cursor.lastrowid)

        # ====================================================
        # 5. ADJUNTO
        # ====================================================

        print("Insertando adjuntos...")

        tipos_archivo = [
            ("imagen/jpeg", "jpg"),
            ("imagen/png", "png"),
            ("application/pdf", "pdf"),
        ]

        for id_incidencia in incidencia_ids:
            for _ in range(random.randint(1, 3)):
                tipo, extension = random.choice(tipos_archivo)

                # Providers utilizados:
                # UUID: fake.uuid4()
                # File: fake.file_name()

                nombre_archivo = (
                    f"{fake.uuid4()}_{fake.file_name(extension=extension)}"
                )

                cursor.execute(
                    """
                    INSERT INTO ADJUNTO (
                        id_incidencia,
                        ruta_archivo,
                        tipo_archivo,
                        fecha_subida
                    )
                    VALUES (%s, %s, %s, %s)
                    """,
                    (
                        id_incidencia,
                        f"/uploads/{nombre_archivo}",
                        tipo,
                        fake.date_time_between(
                            start_date="-90d",
                            end_date="now",
                        ),
                    ),
                )

        # ====================================================
        # 6. EQUIPO
        # ====================================================

        print("Insertando equipos...")

        especialidades = [
            "Alumbrado público",
            "Obras y mantenimiento",
            "Limpieza urbana",
            "Jardinería",
            "Seguridad urbana",
        ]

        for id_municipio in municipio_ids:
            for _ in range(2):
                especialidad = random.choice(especialidades)

                # Providers utilizados:
                # Company: fake.company()
                # Color: fake.color_name()

                nombre_equipo = (
                    f"{fake.company()} - Equipo {fake.color_name()}"
                )

                cursor.execute(
                    """
                    INSERT INTO EQUIPO (
                        nombre,
                        especialidad,
                        id_municipio
                    )
                    VALUES (%s, %s, %s)
                    """,
                    (
                        nombre_equipo[:100],
                        especialidad,
                        id_municipio,
                    ),
                )

                equipo_ids.append(cursor.lastrowid)

        # ====================================================
        # 7. TRABAJADOR
        # ====================================================

        print("Insertando trabajadores...")

        cargos = [
            "Técnico",
            "Operario",
            "Supervisor",
            "Electricista",
            "Jardinero",
            "Personal de mantenimiento",
        ]

        # Guardamos el ID del trabajador y el de su equipo
        trabajador_ids = []

        for id_equipo in equipo_ids:
            for _ in range(3):
                # Providers utilizados:
                # Person: fake.name()
                # PhoneNumber: fake.phone_number()
                # Internet: fake.email()

                nombre_trabajador = fake.name()
                telefono = fake.phone_number()
                correo = fake.email()

                # Los datos de contacto se generan para utilizar
                # más providers, pero la tabla TRABAJADOR no
                # tiene columnas para almacenarlos.

                cursor.execute(
                    """
                    INSERT INTO TRABAJADOR (
                        id_equipo,
                        nombre,
                        cargo,
                        activo
                    )
                    VALUES (%s, %s, %s, %s)
                    """,
                    (
                        id_equipo,
                        nombre_trabajador[:100],
                        random.choice(cargos),
                        random.choice([True, True, True, False]),
                    ),
                )

                trabajador_ids.append(
                    (cursor.lastrowid, id_equipo)
                )

        # ====================================================
        # 8. ASIGNACION
        # ====================================================

        print("Insertando asignaciones...")

        for id_incidencia in incidencia_ids:
            for _ in range(random.randint(1, 2)):
                id_equipo = random.choice(equipo_ids)

                fecha_asignacion = fake.date_time_between(
                    start_date="-60d",
                    end_date="now",
                )

                fecha_fin = None

                if random.choice([True, False]):
                    posible_fecha_fin = fecha_asignacion + timedelta(
                        days=random.randint(1, 10)
                    )

                    if posible_fecha_fin <= datetime.now():
                        fecha_fin = posible_fecha_fin

                # Provider Lorem: fake.sentence()

                cursor.execute(
                    """
                    INSERT INTO ASIGNACION (
                        id_incidencia,
                        id_equipo,
                        fecha_asignacion,
                        fecha_fin,
                        observaciones
                    )
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (
                        id_incidencia,
                        id_equipo,
                        fecha_asignacion,
                        fecha_fin,
                        fake.sentence(),
                    ),
                )

                asignacion_ids.append(
                    (cursor.lastrowid, id_equipo)
                )

        # ====================================================
        # 9. HISTORIAL_ESTADO
        # ====================================================

        print("Insertando historial de estados...")

        for id_incidencia in incidencia_ids:
            estado_nuevo = random.choice(
                ["En proceso", "Resuelta"]
            )

            cursor.execute(
                """
                INSERT INTO HISTORIAL_ESTADO (
                    id_incidencia,
                    estado_anterior,
                    estado_nuevo,
                    fecha_cambio,
                    observaciones
                )
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    id_incidencia,
                    "Pendiente",
                    estado_nuevo,
                    fake.date_time_between(
                        start_date="-30d",
                        end_date="now",
                    ),
                    fake.paragraph(nb_sentences=2),
                ),
            )

        # ====================================================
        # 10. ACTUACION
        # ====================================================

        print("Insertando actuaciones...")

        for id_asignacion, id_equipo in asignacion_ids:

            # Seleccionar trabajadores del equipo asignado
            trabajadores_equipo = [
                id_trabajador
                for id_trabajador, equipo_trabajador
                in trabajador_ids
                if equipo_trabajador == id_equipo
            ]

            if not trabajadores_equipo:
                continue

            for _ in range(random.randint(1, 2)):
                id_trabajador = random.choice(
                    trabajadores_equipo
                )

                fecha_actuacion = fake.date_time_between(
                    start_date="-30d",
                    end_date="now",
                )

                coste = Decimal(
                    str(round(random.uniform(50, 1500), 2))
                )

                resultado = random.choice(
                    [
                        "Completada",
                        "Parcial",
                        "Pendiente de revisión",
                    ]
                )

                cursor.execute(
                    """
                    INSERT INTO ACTUACION (
                        id_asignacion,
                        id_trabajador,
                        fecha_actuacion,
                        descripcion,
                        coste_estimado,
                        resultado
                    )
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (
                        id_asignacion,
                        id_trabajador,
                        fecha_actuacion,
                        fake.paragraph(nb_sentences=2),
                        coste,
                        resultado,
                    ),
                )

    # Confirmar todas las inserciones
    cnx.commit()

    print("\n======================================")
    print("BASE DE DATOS POBLADA CORRECTAMENTE")
    print("======================================")
    print(f"Municipios: {len(municipio_ids)}")
    print(f"Zonas: {len(zona_ids)}")
    print(f"Categorías: {len(categoria_ids)}")
    print(f"Incidencias: {len(incidencia_ids)}")
    print(f"Equipos: {len(equipo_ids)}")
    print(f"Trabajadores: {len(trabajador_ids)}")
    print(f"Asignaciones: {len(asignacion_ids)}")
    print("Adjuntos, historiales y actuaciones insertados.")

except mysql.connector.Error as err:
    if cnx is not None:
        cnx.rollback()

    print(f"Error de MySQL: {err}")

except Exception as err:
    if cnx is not None:
        cnx.rollback()

    print(f"Error inesperado: {err}")

finally:
    if cnx is not None and cnx.is_connected():
        cnx.close()
        print("Conexión cerrada.")
