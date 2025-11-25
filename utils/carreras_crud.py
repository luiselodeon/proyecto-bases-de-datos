import mysql.connector

def list_carreras(cursor):
    cursor.execute("""
        SELECT c.idcarrera, c.descripcion_carrera, c.creditos_carrera,
               c.iddepartamentoacademico, d.nombre_departamento,
               c.costo_inscripcion
        FROM carrera c
        JOIN departamentoacademico d
            ON c.iddepartamentoacademico = d.iddepartamentoacademico
        ORDER BY c.idcarrera;
    """)
    return cursor.fetchall()

def get_departamentos(cursor):
    cursor.execute("SELECT * FROM departamentoacademico ORDER BY iddepartamentoacademico;")
    return cursor.fetchall()

def add_carrera(cursor, idcarrera, descripcion, creditos, iddepto, costo):
    cursor.execute("""
        INSERT INTO carrera
        (idcarrera, descripcion_carrera, creditos_carrera,
         iddepartamentoacademico, costo_inscripcion)
        VALUES (%s, %s, %s, %s, %s)
    """, (idcarrera, descripcion, creditos, iddepto, costo))

def get_carrera(cursor, idcarrera):
    cursor.execute("""
        SELECT * FROM carrera
        WHERE idcarrera = %s;
    """, (idcarrera,))
    return cursor.fetchone()

def update_carrera(cursor, idcarrera, descripcion, creditos, iddepto, costo):
    cursor.execute("""
        UPDATE carrera
        SET descripcion_carrera = %s,
            creditos_carrera = %s,
            iddepartamentoacademico = %s,
            costo_inscripcion = %s
        WHERE idcarrera = %s
    """, (descripcion, creditos, iddepto, costo, idcarrera))

def delete_carrera(cursor, idcarrera):
    cursor.execute("DELETE FROM carrera WHERE idcarrera = %s;", (idcarrera,))

def search_carreras(cursor, query_term):
    like = f"%{query_term}%"
    cursor.execute("""
        SELECT c.idcarrera, c.descripcion_carrera, c.creditos_carrera,
               c.iddepartamentoacademico, d.nombre_departamento,
               c.costo_inscripcion
        FROM carrera c
        JOIN departamentoacademico d
            ON c.iddepartamentoacademico = d.iddepartamentoacademico
        WHERE c.descripcion_carrera LIKE %s
           OR d.nombre_departamento LIKE %s
           OR c.idcarrera LIKE %s
        ORDER BY c.idcarrera;
    """, (like, like, like))
    return cursor.fetchall()
