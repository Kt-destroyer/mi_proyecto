import sympy as sp
import numpy as np
import re

from sympy.parsing.sympy_parser import (
    parse_expr, standard_transformations, implicit_multiplication_application,
    convert_xor
)

try:
    from scipy.integrate import nquad
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False

# Diccionario de funciones para sympify/lambdify (incluye sec, csc, cot)
sympy_func_dict = {
    "sin": sp.sin, "cos": sp.cos, "tan": sp.tan,
    "log": sp.log, "exp": sp.exp, "sqrt": sp.sqrt,
    "sec": sp.sec, "csc": sp.csc, "cot": sp.cot
}

def parse_math_expr(expr_str):
    """
    Permite entradas tipo 2x, sin x, x^2, etc.
    """
    if expr_str is None or expr_str == "":
        raise ValueError("Expresión vacía")
    transformations = (
        standard_transformations +
        (implicit_multiplication_application, convert_xor)
    )
    return parse_expr(str(expr_str), transformations=transformations, local_dict=sympy_func_dict)

def get_limit_func(expr, args):
    # Devuelve una función de las variables args a partir de un string, número o función
    if isinstance(expr, (float, int)):
        return lambda *a: float(expr)
    elif isinstance(expr, str):
        # Corrige entradas como x2 -> x*2, 2x -> 2*x, x^2 -> x**2
        expr = expr.replace('^', '**')
        expr = re.sub(r'([a-zA-Z])(\d)', r'\1*\2', expr)
        expr = re.sub(r'(\d)([a-zA-Z])', r'\1*\2', expr)
        return sp.lambdify(args, parse_math_expr(expr), modules=["numpy"])
    elif callable(expr):
        return expr
    else:
        raise ValueError("No se pudo convertir el límite a función.")

def simpson_simple(f, a, b, n=1000):
    if n % 2:
        n += 1
    h = (b - a) / n
    x = np.linspace(a, b, n+1)
    y = f(x)
    S = y[0] + y[-1] + 4 * np.sum(y[1:-1:2]) + 2 * np.sum(y[2:-2:2])
    return S * h / 3

def simpson_doble_variable(f, x_inf, x_sup, y_inf_func, y_sup_func, nx=50, ny=50):
    if nx % 2: nx += 1
    if ny % 2: ny += 1
    x_vals = np.linspace(x_inf, x_sup, nx+1)
    hx = (x_sup - x_inf) / nx
    S_total = 0.0
    for i, xi in enumerate(x_vals):
        y_inf = y_inf_func(xi)
        y_sup = y_sup_func(xi)
        if y_sup <= y_inf:
            continue
        y_vals = np.linspace(y_inf, y_sup, ny+1)
        hy = (y_sup - y_inf) / ny
        S_y = 0.0
        for j, yj in enumerate(y_vals):
            coeff = 1
            if i == 0 or i == nx:
                coeff *= 1
            elif i % 2 == 1:
                coeff *= 4
            else:
                coeff *= 2
            if j == 0 or j == ny:
                coeff *= 1
            elif j % 2 == 1:
                coeff *= 4
            else:
                coeff *= 2
            try:
                v = f(xi, yj)
            except Exception:
                v = 0.0  # Evita errores por valores fuera de dominio
            S_y += coeff * v
        S_y *= hy / 3
        S_total += S_y
    return S_total * hx / 3

def simpson_triple_variable(
    f, x_inf, x_sup,
    y_inf_func, y_sup_func,
    z_inf_func, z_sup_func,
    nx=10, ny=10, nz=10
):
    if nx % 2: nx += 1
    if ny % 2: ny += 1
    if nz % 2: nz += 1
    x_vals = np.linspace(x_inf, x_sup, nx+1)
    hx = (x_sup - x_inf) / nx
    S_total = 0.0
    for i, xi in enumerate(x_vals):
        y_inf = y_inf_func(xi)
        y_sup = y_sup_func(xi)
        if y_sup <= y_inf:
            continue
        y_vals = np.linspace(y_inf, y_sup, ny+1)
        hy = (y_sup - y_inf) / ny
        S_y = 0.0
        for j, yj in enumerate(y_vals):
            z_inf = z_inf_func(xi, yj)
            z_sup = z_sup_func(xi, yj)
            if z_sup <= z_inf:
                continue
            z_vals = np.linspace(z_inf, z_sup, nz+1)
            hz = (z_sup - z_inf) / nz
            S_z = 0.0
            for k, zk in enumerate(z_vals):
                coeff = 1
                if i == 0 or i == nx:
                    coeff *= 1
                elif i % 2 == 1:
                    coeff *= 4
                else:
                    coeff *= 2
                if j == 0 or j == ny:
                    coeff *= 1
                elif j % 2 == 1:
                    coeff *= 4
                else:
                    coeff *= 2
                if k == 0 or k == nz:
                    coeff *= 1
                elif k % 2 == 1:
                    coeff *= 4
                else:
                    coeff *= 2
                try:
                    v = f(xi, yj, zk)
                except Exception:
                    v = 0.0  # Evita errores por valores fuera de dominio
                S_z += coeff * v
            S_z *= hz / 3
            S_y += S_z
        S_y *= hy / 3
        S_total += S_y
    return S_total * hx / 3

def _valida_resultado(result):
    if isinstance(result, (float, int, np.floating)):
        return np.isfinite(result)
    try:
        arr = np.asarray(result, dtype=float)
        return np.all(np.isfinite(arr))
    except Exception:
        return False

def calcular_integral(tipo: str, expresion: str, limites: dict, metodo: str = "simpson"):
    x, y, z = sp.symbols('x y z')
    resultado = None

    try:
        # Robust parser (permite notación matemática común)
        expr = parse_math_expr(expresion) if expresion else None

        if tipo == "simple":
            a, b = float(limites["a"]), float(limites["b"])
            f = sp.lambdify(x, expr, modules=["numpy"])
            if metodo == "simpson":
                resultado = simpson_simple(f, a, b, n=1000)
            elif metodo == "scipy" and SCIPY_AVAILABLE:
                resultado, err = nquad(lambda x_: f(x_), [[a, b]])
            else:
                return {"error": "Método de integración no soportado o scipy no instalado."}

        elif tipo == "doble":
            a, b = float(limites["a"]), float(limites["b"])
            f = sp.lambdify((x, y), expr, modules=["numpy"])
            y_inf_func = get_limit_func(limites["c"], (x,))
            y_sup_func = get_limit_func(limites["d"], (x,))

            if metodo == "simpson":
                resultado = simpson_doble_variable(
                    f, a, b, y_inf_func, y_sup_func, nx=50, ny=50
                )
            elif metodo == "scipy" and SCIPY_AVAILABLE:
                def scipy_integrand(y_, x_):
                    return f(x_, y_)
                resultado, err = nquad(
                    scipy_integrand,
                    [[a, b], lambda x_: y_inf_func(x_), lambda x_: y_sup_func(x_)]
                )
            else:
                return {"error": "Método de integración no soportado o scipy no instalado."}

        elif tipo == "triple":
            a, b = float(limites["a"]), float(limites["b"])
            f = sp.lambdify((x, y, z), expr, modules=["numpy"])
            y_inf_func = get_limit_func(limites["c"], (x,))
            y_sup_func = get_limit_func(limites["d"], (x,))
            z_inf_func = get_limit_func(limites["e"], (x, y))
            z_sup_func = get_limit_func(limites["f"], (x, y))

            if metodo == "simpson":
                resultado = simpson_triple_variable(
                    f, a, b, y_inf_func, y_sup_func, z_inf_func, z_sup_func, nx=10, ny=10, nz=10
                )
            elif metodo == "scipy" and SCIPY_AVAILABLE:
                def scipy_integrand(z_, y_, x_):
                    return f(x_, y_, z_)
                resultado, err = nquad(
                    scipy_integrand,
                    [
                        [a, b],
                        lambda x_: y_inf_func(x_),
                        lambda x_: y_sup_func(x_),
                        lambda x_, y_: z_inf_func(x_, y_),
                        lambda x_, y_: z_sup_func(x_, y_)
                    ]
                )
            else:
                return {"error": "Método de integración no soportado o scipy no instalado."}

        else:
            return {"error": f"Tipo de integral no soportada: {tipo}"}

        if not _valida_resultado(resultado):
            return {"error": "El resultado de la integral es infinito o indefinido. Cambia los límites o la función."}
        return {
            "valor": float(resultado),
            "grafica": ""
        }

    except Exception as e:
        print(f"Error al calcular integral: {str(e)}")
        return {"error": f"Error interno al calcular la integral: {str(e)}"}