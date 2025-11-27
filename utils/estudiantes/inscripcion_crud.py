import mysql.connector

def list_inscripciones(cursor):
    """List all inscripciones"""
    query = """
    SELECT 
        i.idinscripcion,
        i.matricula_alumno,
        i.idperiodoinscripciones,
        i.fecha_inscripcion,
        i.motivo_inscripcion,
        i.estatus,
        CONCAT(p.nombre, ' ', p.apellido_paterno, ' ', IFNULL(p.apellido_materno, '')) AS nombre_estudiante,
        pi.descripcion_periodo
    FROM inscripcion i
    JOIN estudiante e ON i.matricula_alumno = e.matricula_alumno
    JOIN persona p ON e.idpersona = p.idpersona
    JOIN periodoinscripciones pi ON i.idperiodoinscripciones = pi.idperiodoinscripciones
    ORDER BY i.fecha_inscripcion DESC
    """
    cursor.execute(query)
    return cursor.fetchall()

def get_inscripcion(cursor, idinscripcion):
    """Get a specific inscripcion"""
    query = "SELECT * FROM inscripcion WHERE idinscripcion = %s"
    cursor.execute(query, (idinscripcion,))
    return cursor.fetchone()

def add_inscripcion(cursor, matricula_alumno, idperiodo, fecha_inscripcion, motivo_inscripcion, estatus='INICIADA'):
    """Add new inscripcion"""
    query = """
    INSERT INTO inscripcion (matricula_alumno, idperiodoinscripciones, fecha_inscripcion, motivo_inscripcion, estatus)
    VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(query, (matricula_alumno, idperiodo, fecha_inscripcion, motivo_inscripcion, estatus))
    return cursor.lastrowid

def update_inscripcion(cursor, idinscripcion, fecha_inscripcion, motivo_inscripcion, estatus):
    """Update inscripcion"""
    query = """
    UPDATE inscripcion
    SET fecha_inscripcion = %s, motivo_inscripcion = %s, estatus = %s
    WHERE idinscripcion = %s
    """
    cursor.execute(query, (fecha_inscripcion, motivo_inscripcion, estatus, idinscripcion))

def delete_inscripcion(cursor, idinscripcion):
    """Delete inscripcion"""
    query = "DELETE FROM inscripcion WHERE idinscripcion = %s"
    cursor.execute(query, (idinscripcion,))

def get_estudiantes(cursor):
    """Get list of students for dropdown"""
    query = """
    SELECT e.matricula_alumno,
           CONCAT(p.nombre, ' ', p.apellido_paterno, ' ', IFNULL(p.apellido_materno, '')) AS nombre_completo
    FROM estudiante e
    JOIN persona p ON e.idpersona = p.idpersona
    WHERE e.estatus = 'ACTIVO'
    ORDER BY nombre_completo
    """
    cursor.execute(query)
    return cursor.fetchall()

def get_periodos(cursor):
    """Get list of periods for dropdown"""
    query = """
    SELECT idperiodoinscripciones, descripcion_periodo 
    FROM periodoinscripciones 
    WHERE estatus = 'ABIERTO'
    ORDER BY descripcion_periodo DESC
    """
    cursor.execute(query)
    return cursor.fetchall()

def search_inscripciones(cursor, query_term):
    """Search inscripciones by student name or period"""
    query = """
    SELECT 
        i.idinscripcion,
        i.matricula_alumno,
        i.idperiodoinscripciones,
        i.fecha_inscripcion,
        i.motivo_inscripcion,
        i.estatus,
        CONCAT(p.nombre, ' ', p.apellido_paterno, ' ', IFNULL(p.apellido_materno, '')) AS nombre_estudiante,
        pi.descripcion_periodo
    FROM inscripcion i
    JOIN estudiante e ON i.matricula_alumno = e.matricula_alumno
    JOIN persona p ON e.idpersona = p.idpersona
    JOIN periodoinscripciones pi ON i.idperiodoinscripciones = pi.idperiodoinscripciones
    WHERE p.nombre LIKE %s 
       OR p.apellido_paterno LIKE %s
       OR pi.descripcion_periodo LIKE %s
    ORDER BY i.fecha_inscripcion DESC
    """
    term = f"%{query_term}%"
    cursor.execute(query, (term, term, term))
    return cursor.fetchall()
