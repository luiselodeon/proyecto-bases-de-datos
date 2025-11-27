import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

def list_usuarios(cursor):
    """List all usuarios"""
    query = "SELECT idusuario, email, rol FROM usuarios ORDER BY email"
    cursor.execute(query)
    return cursor.fetchall()

def get_usuario(cursor, idusuario):
    """Get a specific usuario (without password)"""
    query = "SELECT idusuario, email, rol FROM usuarios WHERE idusuario = %s"
    cursor.execute(query, (idusuario,))
    return cursor.fetchone()

def add_usuario(cursor, email, password, rol):
    """Add new usuario with hashed password"""
    hashed_password = generate_password_hash(password)
    query = """
    INSERT INTO usuarios (email, password, rol)
    VALUES (%s, %s, %s)
    """
    cursor.execute(query, (email, hashed_password, rol))
    return cursor.lastrowid

def update_usuario(cursor, idusuario, email, rol, password=None):
    """Update usuario, optionally change password"""
    if password:
        hashed_password = generate_password_hash(password)
        query = """
        UPDATE usuarios
        SET email = %s, rol = %s, password = %s
        WHERE idusuario = %s
        """
        cursor.execute(query, (email, rol, hashed_password, idusuario))
    else:
        query = """
        UPDATE usuarios
        SET email = %s, rol = %s
        WHERE idusuario = %s
        """
        cursor.execute(query, (email, rol, idusuario))

def delete_usuario(cursor, idusuario):
    """Delete usuario"""
    query = "DELETE FROM usuarios WHERE idusuario = %s"
    cursor.execute(query, (idusuario,))

def search_usuarios(cursor, query_term):
    """Search usuarios by email or rol"""
    query = "SELECT idusuario, email, rol FROM usuarios WHERE email LIKE %s OR rol LIKE %s ORDER BY email"
    term = f"%{query_term}%"
    cursor.execute(query, (term, term))
    return cursor.fetchall()
