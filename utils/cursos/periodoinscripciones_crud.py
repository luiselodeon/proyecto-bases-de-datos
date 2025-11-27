import mysql.connector

def list_periodos(cursor):
    """List all periodos de inscripciones"""
    query = """
    SELECT *
    FROM periodoinscripciones
    ORDER BY fecha_inicio_insc DESC
    """
    cursor.execute(query)
    return cursor.fetchall()

def get_periodo(cursor, idperiodo):
    """Get a specific periodo"""
    query = "SELECT * FROM periodoinscripciones WHERE idperiodoinscripciones = %s"
    cursor.execute(query, (idperiodo,))
    return cursor.fetchone()

def add_periodo(cursor, descripcion_periodo, fecha_inicio_insc, fecha_fin_insc, costo_por_credito, estatus='ABIERTO'):
    """Add new periodo de inscripciones"""
    query = """
    INSERT INTO periodoinscripciones (descripcion_periodo, fecha_inicio_insc, fecha_fin_insc, estatus, costo_por_credito)
    VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(query, (descripcion_periodo, fecha_inicio_insc, fecha_fin_insc, estatus, costo_por_credito))
    return cursor.lastrowid

def update_periodo(cursor, idperiodo, descripcion_periodo, fecha_inicio_insc, fecha_fin_insc, costo_por_credito, estatus):
    """Update periodo de inscripciones"""
    query = """
    UPDATE periodoinscripciones
    SET descripcion_periodo = %s, fecha_inicio_insc = %s, fecha_fin_insc = %s, costo_por_credito = %s, estatus = %s
    WHERE idperiodoinscripciones = %s
    """
    cursor.execute(query, (descripcion_periodo, fecha_inicio_insc, fecha_fin_insc, costo_por_credito, estatus, idperiodo))

def delete_periodo(cursor, idperiodo):
    """Delete periodo de inscripciones"""
    query = "DELETE FROM periodoinscripciones WHERE idperiodoinscripciones = %s"
    cursor.execute(query, (idperiodo,))

def search_periodos(cursor, query_term):
    """Search periodos by description"""
    query = """
    SELECT *
    FROM periodoinscripciones
    WHERE descripcion_periodo LIKE %s
    ORDER BY fecha_inicio_insc DESC
    """
    term = f"%{query_term}%"
    cursor.execute(query, (term,))
    return cursor.fetchall()
