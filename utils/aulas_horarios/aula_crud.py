import mysql.connector

def list_aulas(cursor):
    """List all aulas"""
    query = "SELECT * FROM aula ORDER BY descripcion_aula"
    cursor.execute(query)
    return cursor.fetchall()

def get_aula(cursor, idaula):
    """Get a specific aula"""
    query = "SELECT * FROM aula WHERE idaula = %s"
    cursor.execute(query, (idaula,))
    return cursor.fetchone()

def add_aula(cursor, descripcion, lugar, capacidad):
    """Add new aula"""
    query = """
    INSERT INTO aula (descripcion_aula, lugar_fisico, capacidad)
    VALUES (%s, %s, %s)
    """
    cursor.execute(query, (descripcion, lugar, capacidad))
    return cursor.lastrowid

def update_aula(cursor, idaula, descripcion, lugar, capacidad):
    """Update aula"""
    query = """
    UPDATE aula
    SET descripcion_aula = %s, lugar_fisico = %s, capacidad = %s
    WHERE idaula = %s
    """
    cursor.execute(query, (descripcion, lugar, capacidad, idaula))

def delete_aula(cursor, idaula):
    """Delete aula"""
    query = "DELETE FROM aula WHERE idaula = %s"
    cursor.execute(query, (idaula,))

def search_aulas(cursor, query_term):
    """Search aulas by description or place"""
    query = "SELECT * FROM aula WHERE descripcion_aula LIKE %s OR lugar_fisico LIKE %s ORDER BY descripcion_aula"
    term = f"%{query_term}%"
    cursor.execute(query, (term, term))
    return cursor.fetchall()
