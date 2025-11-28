import mysql.connector

def list_becas(cursor):
    cursor.execute("""
        SELECT b.idbeca,
               b.descripcion_beca,
               b.porcentaje_beca,
               b.estatus_beca,
               b.idtipo_beca,
               t.nombre_tipo
        FROM beca b
        LEFT JOIN tipo_beca t
          ON b.idtipo_beca = t.idtipo_beca
        ORDER BY b.idbeca;
    """)
    return cursor.fetchall()

def get_tipos_beca(cursor):
    cursor.execute("SELECT idtipo_beca, nombre_tipo FROM tipo_beca ORDER BY idtipo_beca;")
    return cursor.fetchall()

def add_beca(cursor, descripcion, porcentaje, estatus, idtipo_beca):
    cursor.execute("""
        INSERT INTO beca
        (descripcion_beca, porcentaje_beca, estatus_beca, idtipo_beca)
        VALUES (%s, %s, %s, %s)
    """, (descripcion, porcentaje, estatus, idtipo_beca))

def get_beca(cursor, idbeca):
    cursor.execute("""
        SELECT b.idbeca, b.descripcion_beca, b.porcentaje_beca,
               b.estatus_beca, b.idtipo_beca
        FROM beca b
        WHERE b.idbeca = %s;
    """, (idbeca,))
    return cursor.fetchone()

def update_beca(cursor, idbeca, descripcion, porcentaje, estatus, idtipo_beca):
    cursor.execute("""
        UPDATE beca
        SET descripcion_beca = %s,
            porcentaje_beca = %s,
            estatus_beca = %s,
            idtipo_beca = %s
        WHERE idbeca = %s
    """, (descripcion, porcentaje, estatus, idtipo_beca, idbeca))

def delete_beca(cursor, idbeca):
    cursor.execute("DELETE FROM beca WHERE idbeca = %s;", (idbeca,))

def search_becas(cursor, query_term):
    patron = f"%{query_term}%"
    cursor.execute("""
        SELECT b.idbeca,
               b.descripcion_beca,
               b.porcentaje_beca,
               b.estatus_beca,
               b.idtipo_beca,
               t.nombre_tipo
        FROM beca b
        LEFT JOIN tipo_beca t ON b.idtipo_beca = t.idtipo_beca
        WHERE b.descripcion_beca LIKE %s
           OR b.estatus_beca LIKE %s
           OR t.nombre_tipo LIKE %s
        ORDER BY b.idbeca;
    """, (patron, patron, patron))
    return cursor.fetchall()
