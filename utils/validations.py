# utils/validations.py
import re
from datetime import datetime

def validate_not_empty(value):
    """Validación simple para campos obligatorios."""
    return value is not None and str(value).strip() != ""

def validate_date(date_value):
    """Valida fechas obligatorias."""
    try:
        datetime.strptime(str(date_value), "%Y-%m-%d")
        return True
    except (ValueError, TypeError):
        return False

def validate_email(email):
    """Valida formato de correo."""
    patron = r"[^@]+@[^@]+\.[^@]+"
    return bool(re.match(patron, email))

def validate_number(num):
    """Valida números positivos."""
    try:
        return float(num) >= 0
    except (ValueError, TypeError):
        return False

def validate_file(file, tipos):
    """Valida extensiones permitidas."""
    if not file:
        return False
    ext = file.name.split(".")[-1].lower()
    return ext in tipos


def validar_riesgo(valor):
    """Devuelve True si el valor representa un riesgo alto (>=15)."""
    try:
        return int(valor) >= 15
    except (ValueError, TypeError):
        return False
