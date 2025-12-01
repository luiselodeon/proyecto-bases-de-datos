import mysql.connector

def list_docente_capacitaciones(cursor):
    """List all teacher-capacity assignments"""
    query = """
    SELECT 
        dc.iddocente,
        dc.idcapacitacion,
        CONCAT(p.nombre, ' ', p.apellido_paterno, ' ', p.apellido_materno) AS nombre_docente,
        c.descripcion AS descripcion_capacitacion,
        c.fecha_inicio,
        c.fecha_fin,
        c.horas_capacitacion,
        c.institucion
    FROM docente_capacitacion dc
    JOIN docente d ON dc.iddocente = d.iddocente
    JOIN persona p ON d.idpersona = p.idpersona
    JOIN capacitacion c ON dc.idcapacitacion = c.idcapacitacion
    ORDER BY c.fecha_inicio DESC, p.apellido_paterno, p.apellido_materno
    """
    cursor.execute(query)
    return cursor.fetchall()

def get_docentes(cursor):
    """Get all active teachers"""
    query = """
    SELECT 
        d.iddocente,
        CONCAT(p.nombre, ' ', p.apellido_paterno, ' ', p.apellido_materno) AS nombre_completo
    FROM docente d
    JOIN persona p ON d.idpersona = p.idpersona
    WHERE d.estatus = 'A'
    ORDER BY p.apellido_paterno, p.apellido_materno, p.nombre
    """
    cursor.execute(query)
    return cursor.fetchall()

def get_capacitaciones(cursor):
    """Get all capacitations"""
    query = """
    SELECT 
        idcapacitacion,
        descripcion,
        fecha_inicio,
        fecha_fin,
        horas_capacitacion,
        institucion
    FROM capacitacion
    ORDER BY fecha_inicio DESC
    """
    cursor.execute(query)
    return cursor.fetchall()

def add_docente_capacitacion(cursor, iddocente, idcapacitacion):
    """Assign a teacher to a capacitation"""
    query = """
    INSERT INTO docente_capacitacion (iddocente, idcapacitacion)
    VALUES (%s, %s)
    """
    cursor.execute(query, (iddocente, idcapacitacion))

def delete_docente_capacitacion(cursor, iddocente, idcapacitacion):
    """Remove a teacher from a capacitation"""
    query = """
    DELETE FROM docente_capacitacion
    WHERE iddocente = %s AND idcapacitacion = %s
    """
    cursor.execute(query, (iddocente, idcapacitacion))

def search_docente_capacitaciones(cursor, query_term):
    """Search teacher-capacity assignments"""
    search_pattern = f"%{query_term}%"
    query = """
    SELECT 
        dc.iddocente,
        dc.idcapacitacion,
        CONCAT(p.nombre, ' ', p.apellido_paterno, ' ', p.apellido_materno) AS nombre_docente,
        c.descripcion AS descripcion_capacitacion,
        c.fecha_inicio,
        c.fecha_fin,
        c.horas_capacitacion,
        c.institucion
    FROM docente_capacitacion dc
    JOIN docente d ON dc.iddocente = d.iddocente
    JOIN persona p ON d.idpersona = p.idpersona
    JOIN capacitacion c ON dc.idcapacitacion = c.idcapacitacion
    WHERE p.nombre LIKE %s
       OR p.apellido_paterno LIKE %s
       OR p.apellido_materno LIKE %s
       OR c.descripcion LIKE %s
       OR c.institucion LIKE %s
    ORDER BY c.fecha_inicio DESC, p.apellido_paterno, p.apellido_materno
    """
    cursor.execute(query, (search_pattern, search_pattern, search_pattern, search_pattern, search_pattern))
    return cursor.fetchall()
