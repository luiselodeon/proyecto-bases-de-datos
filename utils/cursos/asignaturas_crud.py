import mysql.connector

def list_asignaturas(cursor):
    cursor.execute("""
        SELECT a.idasignatura,
               a.nombre_asignatura,
               a.creditos_asignatura,
               a.horas_por_sesion,
               a.clave_asignatura,
               a.iddeptoasignatura,
               da.nombre_deptoasignatura
        FROM asignatura a
        LEFT JOIN departamentoasignatura da
               ON a.iddeptoasignatura = da.iddeptoasignatura
        ORDER BY a.idasignatura;
    """)
    return cursor.fetchall()

def get_departamentos_asignatura(cursor):
    cursor.execute("""
        SELECT iddeptoasignatura, nombre_deptoasignatura
        FROM departamentoasignatura
        ORDER BY iddeptoasignatura;
    """)
    return cursor.fetchall()

def add_asignatura(cursor, idasignatura, nombre, creditos, horas, iddepto):
    prefijo = "DEPT"
    if iddepto:
        cursor.execute("""
            SELECT nombre_deptoasignatura
            FROM departamentoasignatura
            WHERE iddeptoasignatura = %s
        """, (iddepto,))
        row = cursor.fetchone()
        if row and row["nombre_deptoasignatura"]:
            prefijo = row["nombre_deptoasignatura"][:4].upper()

    codigo = str(idasignatura)[:3]
    clave = f"{prefijo}{codigo}"

    cursor.execute("""
        INSERT INTO asignatura
            (idasignatura, nombre_asignatura, creditos_asignatura,
             horas_por_sesion, iddeptoasignatura, clave_asignatura)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (idasignatura, nombre, creditos, horas, iddepto, clave))

def get_asignatura(cursor, idasignatura):
    cursor.execute("""
        SELECT a.idasignatura,
               a.nombre_asignatura,
               a.creditos_asignatura,
               a.horas_por_sesion,
               a.iddeptoasignatura,
               a.clave_asignatura
        FROM asignatura a
        WHERE a.idasignatura = %s;
    """, (idasignatura,))
    return cursor.fetchone()

def update_asignatura(cursor, idasignatura, nombre, creditos, horas, iddepto):
    prefijo = "DEPT"
    if iddepto:
        cursor.execute("""
            SELECT nombre_deptoasignatura
            FROM departamentoasignatura
            WHERE iddeptoasignatura = %s
        """, (iddepto,))
        row = cursor.fetchone()
        if row and row["nombre_deptoasignatura"]:
            prefijo = row["nombre_deptoasignatura"][:4].upper()

    codigo = str(idasignatura)[:3]
    clave = f"{prefijo}{codigo}"

    cursor.execute("""
        UPDATE asignatura
        SET nombre_asignatura   = %s,
            creditos_asignatura = %s,
            horas_por_sesion    = %s,
            iddeptoasignatura   = %s,
            clave_asignatura    = %s
        WHERE idasignatura = %s
    """, (nombre, creditos, horas, iddepto, clave, idasignatura))

def delete_asignatura(cursor, idasignatura):
    cursor.execute(
        "DELETE FROM asignatura WHERE idasignatura = %s;",
        (idasignatura,)
    )
