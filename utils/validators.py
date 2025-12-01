# utils/validators.py

import re
from datetime import datetime

def validate_string(value, rules):
    if "max" in rules and len(value) > rules["max"]:
        return False, f"El campo excede {rules['max']} caracteres."
    return True, None

def validate_int(value, rules):
    if not value.isdigit():
        return False, "Debe ser un número entero."
    return True, None

def validate_float(value, rules):
    try:
        float(value)
        return True, None
    except ValueError:
        return False, "Debe ser un número decimal válido."

def validate_date(value, rules):
    try:
        datetime.strptime(value, "%Y-%m-%d")
        return True, None
    except ValueError:
        return False, "Fecha inválida. Usa formato YYYY-MM-DD."

def validate_enum(value, rules):
    if value not in rules["values"]:
        return False, f"Valor inválido. Debe ser uno de: {rules['values']}"
    return True, None
