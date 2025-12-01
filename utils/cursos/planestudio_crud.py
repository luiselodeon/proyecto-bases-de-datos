import mysql.connector

def list_planestudios(cursor):
    """Lista todos los planes de estudio con información de la carrera"""
    query = """
    SELECT p.idplanestudio, p.nombre_plan, p.vigencia_inicio, p.vigencia_fin, 
           c.descripcion_carrera, p.idcarrera
    FROM planestudio p
    JOIN carrera c ON p.idcarrera = c.idcarrera
    ORDER BY p.idplanestudio ASC
    """
    cursor.execute(query)
    return cursor.fetchall()

def get_planestudio(cursor, idplanestudio):
    """Obtiene un plan de estudio específico"""
    query = """
    SELECT idplanestudio, nombre_plan, vigencia_inicio, vigencia_fin, idcarrera
    FROM planestudio
    WHERE idplanestudio = %s
    """
    cursor.execute(query, (idplanestudio,))
    return cursor.fetchone()

def add_planestudio(cursor, nombre_plan, vigencia_inicio, vigencia_fin, idcarrera):
    """Añade un nuevo plan de estudio"""
    sql = """
    INSERT INTO planestudio (nombre_plan, vigencia_inicio, vigencia_fin, idcarrera)
    VALUES (%s, %s, %s, %s)
    """
    cursor.execute(sql, (nombre_plan, vigencia_inicio, vigencia_fin if vigencia_fin else None, idcarrera))

def update_planestudio(cursor, idplanestudio, nombre_plan, vigencia_inicio, vigencia_fin, idcarrera):
    """Actualiza un plan de estudio existente"""
    sql = """
    UPDATE planestudio
    SET nombre_plan = %s, vigencia_inicio = %s, vigencia_fin = %s, idcarrera = %s
    WHERE idplanestudio = %s
    """
    cursor.execute(sql, (nombre_plan, vigencia_inicio, vigencia_fin if vigencia_fin else None, idcarrera, idplanestudio))

def delete_planestudio(cursor, idplanestudio):
    """Elimina un plan de estudio"""
    cursor.execute("DELETE FROM planestudio WHERE idplanestudio = %s", (idplanestudio,))

def search_planestudio(cursor, query_term):
    """Busca planes de estudio por nombre o carrera"""
    pattern = f"%{query_term}%"
    query = """
    SELECT p.idplanestudio, p.nombre_plan, p.vigencia_inicio, p.vigencia_fin, 
           c.descripcion_carrera, p.idcarrera
    FROM planestudio p
    JOIN carrera c ON p.idcarrera = c.idcarrera
    WHERE p.nombre_plan LIKE %s OR c.descripcion_carrera LIKE %s
    ORDER BY p.idplanestudio ASC
    """
    cursor.execute(query, (pattern, pattern))
    return cursor.fetchall()

def get_carreras(cursor):
    """Obtiene todas las carreras para el dropdown"""
    cursor.execute("SELECT idcarrera, descripcion_carrera FROM carrera ORDER BY descripcion_carrera")
    return cursor.fetchall()
