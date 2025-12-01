import mysql.connector

# === CAPACITACION ===

def list_capacitaciones(cursor):
    """List all capacitaciones"""
    query = "SELECT * FROM capacitacion ORDER BY fecha_inicio DESC"
    cursor.execute(query)
    return cursor.fetchall()

def get_capacitacion(cursor, idcapacitacion):
    """Get a specific capacitacion"""
    query = "SELECT * FROM capacitacion WHERE idcapacitacion = %s"
    cursor.execute(query, (idcapacitacion,))
    return cursor.fetchone()

def add_capacitacion(cursor, descripcion, fecha_inicio, fecha_fin, horas, institucion):
    """Add new capacitacion"""
    if fecha_fin and str(fecha_fin) < str(fecha_inicio):
        raise ValueError("La fecha de fin no puede ser menor a la fecha de inicio.")

    query = """
    INSERT INTO capacitacion (descripcion, fecha_inicio, fecha_fin, horas_capacitacion, institucion)
    VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(query, (descripcion, fecha_inicio, fecha_fin, horas, institucion))
    return cursor.lastrowid

def update_capacitacion(cursor, idcapacitacion, descripcion, fecha_inicio, fecha_fin, horas, institucion):
    """Update capacitacion"""
    if fecha_fin and str(fecha_fin) < str(fecha_inicio):
        raise ValueError("La fecha de fin no puede ser menor a la fecha de inicio.")

    query = """
    UPDATE capacitacion
    SET descripcion = %s, fecha_inicio = %s, fecha_fin = %s, horas_capacitacion = %s, institucion = %s
    WHERE idcapacitacion = %s
    """
    cursor.execute(query, (descripcion, fecha_inicio, fecha_fin, horas, institucion, idcapacitacion))

def delete_capacitacion(cursor, idcapacitacion):
    """Delete capacitacion"""
    query = "DELETE FROM capacitacion WHERE idcapacitacion = %s"
    cursor.execute(query, (idcapacitacion,))

def search_capacitaciones(cursor, query_term):
    """Search capacitaciones by description"""
    query = "SELECT * FROM capacitacion WHERE descripcion LIKE %s OR institucion LIKE %s ORDER BY fecha_inicio DESC"
    term = f"%{query_term}%"
    cursor.execute(query, (term, term))
    return cursor.fetchall()


# === CERTIFICACION ===

def list_certificaciones(cursor):
    """List all certificaciones"""
    query = "SELECT * FROM certificacion ORDER BY fecha_certificacion DESC"
    cursor.execute(query)
    return cursor.fetchall()

def get_certificacion(cursor, idcertificacion):
    """Get a specific certificacion"""
    query = "SELECT * FROM certificacion WHERE idcertificacion = %s"
    cursor.execute(query, (idcertificacion,))
    return cursor.fetchone()

def add_certificacion(cursor, descripcion, institucion, fecha):
    """Add new certificacion"""
    query = """
    INSERT INTO certificacion (descripcion, institucion, fecha_certificacion)
    VALUES (%s, %s, %s)
    """
    cursor.execute(query, (descripcion, institucion, fecha))
    return cursor.lastrowid

def update_certificacion(cursor, idcertificacion, descripcion, institucion, fecha):
    """Update certificacion"""
    query = """
    UPDATE certificacion
    SET descripcion = %s, institucion = %s, fecha_certificacion = %s
    WHERE idcertificacion = %s
    """
    cursor.execute(query, (descripcion, institucion, fecha, idcertificacion))

def delete_certificacion(cursor, idcertificacion):
    """Delete certificacion"""
    query = "DELETE FROM certificacion WHERE idcertificacion = %s"
    cursor.execute(query, (idcertificacion,))

def search_certificaciones(cursor, query_term):
    """Search certificaciones by description"""
    query = "SELECT * FROM certificacion WHERE descripcion LIKE %s OR institucion LIKE %s ORDER BY fecha_certificacion DESC"
    term = f"%{query_term}%"
    cursor.execute(query, (term, term))
    return cursor.fetchall()


# === HELPERS ===

def get_docentes_for_dropdown(cursor):
    """Get list of docentes for dropdown"""
    query = """
    SELECT d.iddocente,
           CONCAT(p.nombre, ' ', p.apellido_paterno, ' ', IFNULL(p.apellido_materno, '')) AS nombre_completo
    FROM docente d
    JOIN persona p ON d.idpersona = p.idpersona
    WHERE d.estatus = 'A'
    ORDER BY nombre_completo
    """
    cursor.execute(query)
    return cursor.fetchall()

def get_capacitaciones_for_dropdown(cursor):
    """Get capacitaciones for dropdown"""
    query = "SELECT idcapacitacion, descripcion FROM capacitacion ORDER BY descripcion"
    cursor.execute(query)
    return cursor.fetchall()

def get_certificaciones_for_dropdown(cursor):
    """Get certificaciones for dropdown"""
    query = "SELECT idcertificacion, descripcion FROM certificacion ORDER BY descripcion"
    cursor.execute(query)
    return cursor.fetchall()
