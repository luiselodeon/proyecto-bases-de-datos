import mysql.connector

def list_horarios(cursor):
    """List all horarios"""
    query = "SELECT * FROM horario ORDER BY dia_semana, hora_inicio"
    cursor.execute(query)
    return cursor.fetchall()

def get_horario(cursor, idhorario):
    """Get a specific horario"""
    query = "SELECT * FROM horario WHERE idhorario = %s"
    cursor.execute(query, (idhorario,))
    return cursor.fetchone()

def add_horario(cursor, dia_semana, hora_inicio, hora_fin, descripcion):
    """Add new horario"""
    query = """
    INSERT INTO horario (dia_semana, hora_inicio, hora_fin, descripcion_horario)
    VALUES (%s, %s, %s, %s)
    """
    cursor.execute(query, (dia_semana, hora_inicio, hora_fin, descripcion))
    return cursor.lastrowid

def update_horario(cursor, idhorario, dia_semana, hora_inicio, hora_fin, descripcion):
    """Update horario"""
    query = """
    UPDATE horario
    SET dia_semana = %s, hora_inicio = %s, hora_fin = %s, descripcion_horario = %s
    WHERE idhorario = %s
    """
    cursor.execute(query, (dia_semana, hora_inicio, hora_fin, descripcion, idhorario))

def delete_horario(cursor, idhorario):
    """Delete horario"""
    query = "DELETE FROM horario WHERE idhorario = %s"
    cursor.execute(query, (idhorario,))

def search_horarios(cursor, query_term):
    """Search horarios by description or day"""
    query = "SELECT * FROM horario WHERE descripcion_horario LIKE %s OR dia_semana LIKE %s ORDER BY dia_semana, hora_inicio"
    term = f"%{query_term}%"
    cursor.execute(query, (term, term))
    return cursor.fetchall()
