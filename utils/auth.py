from functools import wraps
from flask import session, redirect, url_for, flash

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            flash("Debes iniciar sesión primero", "danger")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return wrapper


def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            # Si no está logueado
            if "user_rol" not in session:
                flash("Debes iniciar sesión.", "danger")
                return redirect(url_for("login"))

            rol_usuario = session["user_rol"]

            # Los administradores siempre pasan
            if rol_usuario == "admin":
                return f(*args, **kwargs)

            # Si no tiene un rol permitido
            if rol_usuario not in roles:
                flash("No tienes permisos para entrar aquí", "danger")
                return redirect(url_for("inicio"))

            return f(*args, **kwargs)
        return wrapper
    return decorator
