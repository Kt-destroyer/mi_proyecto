from sympy.parsing.sympy_parser import (
    parse_expr, standard_transformations, implicit_multiplication_application, convert_xor
)
import sympy

# Diccionario extendido para funciones matemáticas
sympy_func_dict = {
    "sin": sympy.sin, "cos": sympy.cos, "tan": sympy.tan,
    "log": sympy.log, "exp": sympy.exp, "sqrt": sympy.sqrt,
    "sec": sympy.sec, "csc": sympy.csc, "cot": sympy.cot,
    "asin": sympy.asin, "acos": sympy.acos, "atan": sympy.atan,
    "pi": sympy.pi, "e": sympy.E,
}

# Transformaciones para notación matemática natural (2x, xy, x^2, etc)
TRANSFORM = (
    standard_transformations +
    (implicit_multiplication_application, convert_xor)
)

def parse_math_expr(expr_str: str):
    """
    Parsea una expresión matemática de usuario de forma robusta.
    Permite notación matemática común como 2x, sin x, x^2, etc.
    Lanza excepción si es inválida.
    """
    if expr_str is None or expr_str.strip() == "":
        raise ValueError("La expresión está vacía.")
    expr_str = expr_str.replace("^", "**")  # Compatibilidad con ^ como potencia
    try:
        expr = parse_expr(
            expr_str,
            transformations=TRANSFORM,
            local_dict=sympy_func_dict
        )
        # Validación: no aceptar expresiones vacías ni solo números
        if expr is None or (expr.is_Number and expr.free_symbols == set()):
            raise ValueError("La expresión no es válida o es solo un número.")
        return expr
    except Exception as e:
        raise ValueError(f"Error en la expresión matemática: {e}")

def validar_expr_con_variables(expr_str: str, variables_permitidas: set):
    """
    Valida que una expresión solo contenga variables permitidas.
    Lanza excepción si no se cumple.
    """
    expr = parse_math_expr(expr_str)
    usadas = {str(s) for s in expr.free_symbols}
    no_permitidas = usadas - set(variables_permitidas)
    if no_permitidas:
        raise ValueError(f"Variables no permitidas: {', '.join(no_permitidas)}")
    return expr