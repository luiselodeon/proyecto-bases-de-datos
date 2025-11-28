import mysql.connector

def list_departamentos_asignatura(cursor):
    cursor.execute("""
        SELECT iddeptoasignatura, nombre_deptoasignatura
        FROM departamentoasignatura
        ORDER BY iddeptoasignatura;
    """)
    return cursor.fetchall()

def add_departamento_asignatura(cursor, nombre):
    cursor.execute("""
        INSERT INTO departamentoasignatura
        (nombre_deptoasignatura)
        VALUES (%s)
    """, (nombre,))

def get_departamento_asignatura(cursor, iddep):
    cursor.execute("""
        SELECT *
        FROM departamentoasignatura
        WHERE iddeptoasignatura = %s;
    """, (iddep,))
    return cursor.fetchone()

def update_departamento_asignatura(cursor, iddep, nombre):
    cursor.execute("""
        UPDATE departamentoasignatura
        SET nombre_deptoasignatura = %s
        WHERE iddeptoasignatura = %s
    """, (nombre, iddep))

def delete_departamento_asignatura(cursor, iddep):
    cursor.execute("""
        DELETE FROM departamentoasignatura
        WHERE iddeptoasignatura = %s
    """, (iddep,))

def search_departamentos_asignatura(cursor, term):
    cursor.execute("""
        SELECT *
        FROM departamentoasignatura
        WHERE nombre_deptoasignatura LIKE %s
           OR iddeptoasignatura LIKE %s
        ORDER BY iddeptoasignatura;
    """, (f"%{term}%", f"%{term}%"))
    return cursor.fetchall()
