import mysql.connector

def list_asignaturaxcarrera(cursor):
    cursor.execute("""
        SELECT axc.idcarrera,
               c.descripcion_carrera,
               axc.idasignatura,
               a.nombre_asignatura
        FROM asignaturaxcarrera axc
        JOIN carrera c
          ON axc.idcarrera = c.idcarrera
        JOIN asignatura a
          ON axc.idasignatura = a.idasignatura
        ORDER BY c.descripcion_carrera, a.nombre_asignatura;
    """)
    return cursor.fetchall()

def get_carreras(cursor):
    cursor.execute("""
        SELECT idcarrera, descripcion_carrera
        FROM carrera
        ORDER BY idcarrera;
    """)
    return cursor.fetchall()

def get_asignaturas(cursor):
    cursor.execute("""
        SELECT idasignatura, nombre_asignatura
        FROM asignatura
        ORDER BY idasignatura;
    """)
    return cursor.fetchall()

def add_asignaturaxcarrera(cursor, idcarrera, idasignatura):
    cursor.execute("""
        INSERT INTO asignaturaxcarrera (idcarrera, idasignatura)
        VALUES (%s, %s)
    """, (idcarrera, idasignatura))

def delete_asignaturaxcarrera(cursor, idcarrera, idasignatura):
    cursor.execute("""
        DELETE FROM asignaturaxcarrera
        WHERE idcarrera = %s AND idasignatura = %s
    """, (idcarrera, idasignatura))

def search_asignaturaxcarrera(cursor, query_term):
    pattern = f"%{query_term}%"
    cursor.execute("""
        SELECT axc.idcarrera,
               c.descripcion_carrera,
               axc.idasignatura,
               a.nombre_asignatura
        FROM asignaturaxcarrera axc
        JOIN carrera c
          ON axc.idcarrera = c.idcarrera
        JOIN asignatura a
          ON axc.idasignatura = a.idasignatura
        WHERE c.descripcion_carrera LIKE %s
           OR a.nombre_asignatura LIKE %s
           OR axc.idcarrera LIKE %s
           OR axc.idasignatura LIKE %s
        ORDER BY c.descripcion_carrera, a.nombre_asignatura;
    """, (pattern, pattern, pattern, pattern))
    return cursor.fetchall()
