"""
Filtros personalizados para templates de eventos.
"""
from django import template

register = template.Library()


@register.filter
def replace(value, arg):
    """
    Reemplaza todas las ocurrencias de 'old' por 'new'.
    Uso: {{ value|replace:"_" }} o {{ value|replace:"_: " }} para replace _ con espacio
    El argumento debe ser en formato "old:new" o solo "old" (reemplaza por espacio)
    """
    if not value:
        return value
    
    # Si el argumento contiene ':', separar en old y new
    if ':' in arg:
        old, new = arg.split(':', 1)
    else:
        old = arg
        new = ' '
    
    return str(value).replace(old, new)


@register.filter
def format_field_name(value):
    """
    Formatea un nombre de campo para mostrarlo de forma legible.
    Convierte snake_case a Title Case con espacios.
    Uso: {{ field_name|format_field_name }}
    """
    if not value:
        return value
    return str(value).replace('_', ' ').title()
