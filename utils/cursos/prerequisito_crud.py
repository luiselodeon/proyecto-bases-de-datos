import mysql.connector

def list_prerequisitos(cursor):
    """List all prerequisitos with asignatura names"""
    query = """
    SELECT 
        p.idasignatura,
        p.idasignatura_prereq,
        a1.nombre_asignatura AS asignatura_nombre,
        a2.nombre_asignatura AS prerequisito_nombre
    FROM prerequisito_asignatura p
    JOIN asignatura a1 ON p.idasignatura = a1.idasignatura
    JOIN asignatura a2 ON p.idasignatura_prereq = a2.idasignatura
    ORDER BY a1.nombre_asignatura
    """
    cursor.execute(query)
    return cursor.fetchall()

def get_prerequisito(cursor, idasignatura, idasignatura_prereq):
    """Get a specific prerequisito"""
    query = "SELECT * FROM prerequisito_asignatura WHERE idasignatura = %s AND idasignatura_prereq = %s"
    cursor.execute(query, (idasignatura, idasignatura_prereq))
    return cursor.fetchone()

def add_prerequisito(cursor, idasignatura, idasignatura_prereq):
    """Add new prerequisito"""
    query = """
    INSERT INTO prerequisito_asignatura (idasignatura, idasignatura_prereq)
    VALUES (%s, %s)
    """
    cursor.execute(query, (idasignatura, idasignatura_prereq))

def delete_prerequisito(cursor, idasignatura, idasignatura_prereq):
    """Delete prerequisito"""
    query = "DELETE FROM prerequisito_asignatura WHERE idasignatura = %s AND idasignatura_prereq = %s"
    cursor.execute(query, (idasignatura, idasignatura_prereq))

def get_asignaturas(cursor):
    """Get list of asignaturas for dropdown"""
    query = "SELECT idasignatura, nombre_asignatura FROM asignatura ORDER BY nombre_asignatura"
    cursor.execute(query)
    return cursor.fetchall()

def search_prerequisitos(cursor, query_term):
    """Search prerequisitos by asignatura name"""
    query = """
    SELECT 
        p.idasignatura,
        p.idasignatura_prereq,
        a1.nombre_asignatura AS asignatura_nombre,
        a2.nombre_asignatura AS prerequisito_nombre
    FROM prerequisito_asignatura p
    JOIN asignatura a1 ON p.idasignatura = a1.idasignatura
    JOIN asignatura a2 ON p.idasignatura_prereq = a2.idasignatura
    WHERE a1.nombre_asignatura LIKE %s OR a2.nombre_asignatura LIKE %s
    ORDER BY a1.nombre_asignatura
    """
    term = f"%{query_term}%"
    cursor.execute(query, (term, term))
    return cursor.fetchall()
