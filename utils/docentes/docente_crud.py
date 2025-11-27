import mysql.connector

def list_docentes(cursor):
    """List all docentes with persona information"""
    query = """
    SELECT 
        d.iddocente,
        d.idpersona,
        d.fecha_alta,
        d.fecha_baja,
        d.estatus,
        p.nombre,
        p.apellido_paterno,
        p.apellido_materno,
        p.correo,
        p.telefono
    FROM docente d
    JOIN persona p ON d.idpersona = p.idpersona
    ORDER BY p.apellido_paterno, p.apellido_materno, p.nombre
    """
    cursor.execute(query)
    return cursor.fetchall()

def get_docente(cursor, iddocente):
    """Get a specific docente by ID"""
    query = """
    SELECT * FROM docente 
    WHERE iddocente = %s
    """
    cursor.execute(query, (iddocente,))
    return cursor.fetchone()

def add_docente(cursor, idpersona, fecha_alta, estatus='A'):
    """Add a new docente"""
    query = """
    INSERT INTO docente (idpersona, fecha_alta, estatus)
    VALUES (%s, %s, %s)
    """
    cursor.execute(query, (idpersona, fecha_alta, estatus))
    return cursor.lastrowid

def update_docente(cursor, iddocente, fecha_alta, fecha_baja, estatus):
    """Update an existing docente"""
    query = """
    UPDATE docente
    SET fecha_alta = %s, fecha_baja = %s, estatus = %s
    WHERE iddocente = %s
    """
    cursor.execute(query, (fecha_alta, fecha_baja, estatus, iddocente))

def delete_docente(cursor, iddocente):
    """Delete a docente"""
    query = "DELETE FROM docente WHERE iddocente = %s"
    cursor.execute(query, (iddocente,))

def get_personas_sin_docente(cursor):
    """Get list of personas that are not yet docentes"""
    query = """
    SELECT p.idpersona, 
           CONCAT(p.nombre, ' ', p.apellido_paterno, ' ', IFNULL(p.apellido_materno, '')) AS nombre_completo
    FROM persona p
    LEFT JOIN docente d ON p.idpersona = d.idpersona
    WHERE d.iddocente IS NULL
    ORDER BY nombre_completo
    """
    cursor.execute(query)
    return cursor.fetchall()

def search_docentes(cursor, query_term):
    """Search docentes by name or email"""
    query = """
    SELECT 
        d.iddocente,
        d.idpersona,
        d.fecha_alta,
        d.fecha_baja,
        d.estatus,
        p.nombre,
        p.apellido_paterno,
        p.apellido_materno,
        p.correo,
        p.telefono
    FROM docente d
    JOIN persona p ON d.idpersona = p.idpersona
    WHERE p.nombre LIKE %s 
       OR p.apellido_paterno LIKE %s 
       OR p.apellido_materno LIKE %s
       OR p.correo LIKE %s
    ORDER BY p.apellido_paterno, p.nombre
    """
    term = f"%{query_term}%"
    cursor.execute(query, (term, term, term, term))
    return cursor.fetchall()
