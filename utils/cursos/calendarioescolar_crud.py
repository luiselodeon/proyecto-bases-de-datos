import mysql.connector

def list_calendarios(cursor):
    """Lista todos los calendarios escolares"""
    cursor.execute("""
        SELECT idcalendarioescolar, descripcion, fecha_inicio, fecha_fin
        FROM calendarioescolar
        ORDER BY fecha_inicio DESC;
    """)
    return cursor.fetchall()

def add_calendario(cursor, descripcion, fecha_inicio, fecha_fin):
    """Añade un nuevo calendario escolar"""
    cursor.execute("""
        INSERT INTO calendarioescolar
        (descripcion, fecha_inicio, fecha_fin)
        VALUES (%s, %s, %s)
    """, (descripcion, fecha_inicio, fecha_fin))

def get_calendario(cursor, idcalendario):
    """Obtiene un calendario escolar por ID"""
    cursor.execute("""
        SELECT *
        FROM calendarioescolar
        WHERE idcalendarioescolar = %s;
    """, (idcalendario,))
    return cursor.fetchone()

def update_calendario(cursor, idcalendario, descripcion, fecha_inicio, fecha_fin):
    """Actualiza un calendario escolar existente"""
    cursor.execute("""
        UPDATE calendarioescolar
        SET descripcion = %s,
            fecha_inicio = %s,
            fecha_fin = %s
        WHERE idcalendarioescolar = %s
    """, (descripcion, fecha_inicio, fecha_fin, idcalendario))

def delete_calendario(cursor, idcalendario):
    """Elimina un calendario escolar"""
    cursor.execute("""
        DELETE FROM calendarioescolar
        WHERE idcalendarioescolar = %s
    """, (idcalendario,))

def search_calendarios(cursor, term):
    """Busca calendarios escolares por descripción o año"""
    cursor.execute("""
        SELECT *
        FROM calendarioescolar
        WHERE descripcion LIKE %s
           OR YEAR(fecha_inicio) LIKE %s
           OR YEAR(fecha_fin) LIKE %s
        ORDER BY fecha_inicio DESC;
    """, (f"%{term}%", f"%{term}%", f"%{term}%"))
    return cursor.fetchall()
