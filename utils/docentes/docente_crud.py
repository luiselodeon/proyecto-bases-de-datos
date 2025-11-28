import mysql.connector
from datetime import date

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

def add_docente(cursor, nombre, apellido_paterno, apellido_materno, correo, fecha_alta=None, estatus='A'):
    """Add a new docente - creates persona and docente records"""
    # 1. Obtener el siguiente ID para persona
    cursor.execute("SELECT MAX(idpersona) FROM persona")
    result = cursor.fetchone()
    next_id_persona = (result['MAX(idpersona)'] or 0) + 1 if result else 1
    
    # 2. Insertar en persona
    sql_persona = "INSERT INTO persona (idpersona, nombre, apellido_paterno, apellido_materno, correo) VALUES (%s, %s, %s, %s, %s)"
    cursor.execute(sql_persona, (next_id_persona, nombre, apellido_paterno, apellido_materno, correo))
    
    # 3. Usar fecha actual si no se proporciona
    if not fecha_alta:
        fecha_alta = date.today()
    
    # 4. Insertar en docente
    sql_docente = "INSERT INTO docente (idpersona, fecha_alta, estatus) VALUES (%s, %s, %s)"
    cursor.execute(sql_docente, (next_id_persona, fecha_alta, estatus))
    
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
    """Delete a docente and associated persona"""
    # 1. Obtener idpersona antes de borrar
    cursor.execute("SELECT idpersona FROM docente WHERE iddocente = %s", (iddocente,))
    result = cursor.fetchone()
    if not result:
        return False
    
    id_persona = result['idpersona'] if isinstance(result, dict) else result[0]
    
    # 2. Eliminar de docente
    cursor.execute("DELETE FROM docente WHERE iddocente = %s", (iddocente,))
    
    # 3. Eliminar de persona
    cursor.execute("DELETE FROM persona WHERE idpersona = %s", (id_persona,))
    
    return True

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
