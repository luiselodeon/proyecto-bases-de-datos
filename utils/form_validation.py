# utils/form_validation.py

from utils.validators import (
    validate_string, validate_int, validate_float,
    validate_date, validate_enum
)
from utils.schema_generator import generate_schema_from_table

def validate_form_from_table(cursor, table_name, form):
    schema = generate_schema_from_table(cursor, table_name)

    for field, rules in schema.items():
        if rules.get("required") and field not in form:
            return False, f"El campo {field} es obligatorio."

        value = form.get(field, "").strip()

        # Validación por tipo
        if rules["type"] == "string":
            return validate_string(value, rules)

        if rules["type"] == "int":
            return validate_int(value, rules)

        if rules["type"] == "float":
            return validate_float(value, rules)

        if rules["type"] == "date":
            return validate_date(value, rules)

        if rules["type"] == "enum":
            return validate_enum(value, rules)

    return True, None
