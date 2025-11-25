import mysql.connector

def list_departamentos(cursor):
    cursor.execute("SELECT * FROM departamentoacademico ORDER BY iddepartamentoacademico;")
    return cursor.fetchall()

def add_departamento(cursor, iddep, nombre):
    cursor.execute("""
        INSERT INTO departamentoacademico (iddepartamentoacademico, nombre_departamento)
        VALUES (%s, %s)
    """, (iddep, nombre))

def get_departamento(cursor, iddep):
    cursor.execute("SELECT * FROM departamentoacademico WHERE iddepartamentoacademico = %s;", (iddep,))
    return cursor.fetchone()

def update_departamento(cursor, iddep, nombre):
    cursor.execute("""
        UPDATE departamentoacademico
        SET nombre_departamento = %s
        WHERE iddepartamentoacademico = %s
    """, (nombre, iddep))

def delete_departamento(cursor, iddep):
    cursor.execute("DELETE FROM departamentoacademico WHERE iddepartamentoacademico = %s", (iddep,))

def search_departamentos(cursor, query_term):
    like = f"%{query_term}%"
    cursor.execute("""
        SELECT iddepartamentoacademico, nombre_departamento
        FROM departamentoacademico
        WHERE nombre_departamento LIKE %s
           OR iddepartamentoacademico LIKE %s
        ORDER BY iddepartamentoacademico;
    """, (like, like))
    return cursor.fetchall()
