import mysql.connector

def list_tipobeca(cursor):
    cursor.execute("""
        SELECT idtipo_beca, nombre_tipo
        FROM tipo_beca
        ORDER BY idtipo_beca;
    """)
    return cursor.fetchall()

def add_tipobeca(cursor, nombre):
    cursor.execute("""
        INSERT INTO tipo_beca (nombre_tipo)
        VALUES (%s)
    """, (nombre,))

def get_tipobeca(cursor, idtipo):
    cursor.execute("SELECT * FROM tipo_beca WHERE idtipo_beca = %s", (idtipo,))
    return cursor.fetchone()

def update_tipobeca(cursor, idtipo, nombre):
    cursor.execute("""
        UPDATE tipo_beca
        SET nombre_tipo = %s
        WHERE idtipo_beca = %s
    """, (nombre, idtipo))

def delete_tipobeca(cursor, idtipo):
    cursor.execute("DELETE FROM tipo_beca WHERE idtipo_beca = %s", (idtipo,))

def search_tipobeca(cursor, query_term):
    patron = f"%{query_term}%"
    cursor.execute("""
        SELECT idtipo_beca, nombre_tipo
        FROM tipo_beca
        WHERE nombre_tipo LIKE %s
           OR idtipo_beca LIKE %s
        ORDER BY idtipo_beca;
    """, (patron, patron))
    return cursor.fetchall()
