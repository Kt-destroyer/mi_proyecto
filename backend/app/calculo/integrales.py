import sympy as sp
import numpy as np
import re

from sympy.parsing.sympy_parser import (
    parse_expr, standard_transformations, implicit_multiplication_application,
    convert_xor
)

# Diccionario extendido para trigonométricas y constantes
sympy_func_dict = {
    "sin": sp.sin, "cos": sp.cos, "tan": sp.tan,
    "log": sp.log, "exp": sp.exp, "sqrt": sp.sqrt,
    "sec": sp.sec, "csc": sp.csc, "cot": sp.cot,
    "Abs": sp.Abs, "abs": sp.Abs, "pi": sp.pi, "e": sp.E
}

def preprocess_math_expr(expr_str):
    """
    Preprocesa la expresión matemática:
    - Reemplaza abs( por Abs(
    - Soporta 'π' como 'pi'
    - Soporta PI/E en cualquier capitalización
    - Inserta * entre número y pi o e, por ejemplo 2pi -> 2*pi
    """
    expr_str = re.sub(r'\babs\s*\(', 'Abs(', expr_str)
    expr_str = expr_str.replace('π', 'pi')
    expr_str = re.sub(r'\bPI\b', 'pi', expr_str, flags=re.IGNORECASE)
    expr_str = re.sub(r'\bE\b', 'e', expr_str, flags=re.IGNORECASE)
    # Inserta un * entre número y pi o e (por ejemplo 2pi -> 2*pi, 3e -> 3*e)
    expr_str = re.sub(r'(\d)(pi|e)\b', r'\1*\2', expr_str)
    return expr_str

def parse_limit_string(val):
    # Convierte un string como "pi", "2*pi", "e", "3.5", etc. a float usando sympy
    try:
        val_proc = preprocess_math_expr(str(val))
        expr = sp.sympify(val_proc, locals=sympy_func_dict)
        return float(expr.evalf())
    except Exception as ex:
        print(f"Error en parse_limit_string para val={val}: {ex}")
        raise ValueError(f"Límite inválido: {val}")

def parse_math_expr(expr_str):
    if expr_str is None or expr_str == "":
        raise ValueError("Expresión vacía")
    expr_str = preprocess_math_expr(expr_str)
    transformations = (
        standard_transformations +
        (implicit_multiplication_application, convert_xor)
    )
    return parse_expr(str(expr_str), transformations=transformations, local_dict=sympy_func_dict)

def get_limit_func(expr, args):
    if isinstance(expr, (float, int)):
        return lambda *a: float(expr)
    elif isinstance(expr, str):
        expr = expr.replace('^', '**')
        expr = re.sub(r'([a-zA-Z])(\d)', r'\1*\2', expr)
        expr = re.sub(r'(\d)([a-zA-Z])', r'\1*\2', expr)
        expr = preprocess_math_expr(expr)
        try:
            return sp.lambdify(args, parse_math_expr(expr), modules=["numpy"])
        except Exception:
            # Si no es función, intenta forzar a float interpretando como expresión sympy
            try:
                return lambda *a: float(sp.sympify(expr, locals=sympy_func_dict).evalf())
            except Exception:
                raise
    elif callable(expr):
        return expr
    else:
        raise ValueError("No se pudo convertir el límite a función.")

def detectar_discontinuidad(expr, a, b):
    """
    Detecta discontinuidades simples para tan(x), sec(x), csc(x), cot(x), 1/x en [a, b].
    Solo para integrales simples, pero fácil de adaptar a dobles/triples.
    """
    x = sp.symbols('x')
    puntos = []
    # tan(x), sec(x) --> cos(x)=0
    if expr.has(sp.tan) or expr.has(sp.sec):
        k = int(np.floor(a/np.pi - 0.5))
        while True:
            punto = (np.pi/2) + k*np.pi
            if punto > b:
                break
            if a < punto < b:
                puntos.append(punto)
            k += 1
    # cot(x), csc(x) --> sin(x)=0
    if expr.has(sp.cot) or expr.has(sp.csc):
        k = int(np.floor(a/np.pi))
        while True:
            punto = k*np.pi
            if punto > b:
                break
            if a < punto < b:
                puntos.append(punto)
            k += 1
    # 1/x
    if expr.has(1/x):
        if a < 0 < b:
            puntos.append(0)
    return len(puntos) > 0

def simpson_simple(f, a, b, n=10000):
    """
    Regla de Simpson compuesta (robusta para trigonométricas).
    """
    if n % 2:
        n += 1
    x = np.linspace(a, b, n+1)
    y = f(x)
    # Si hay nan/inf, abortar
    if np.any(~np.isfinite(y)):
        raise ValueError("La función tiene valores infinitos o indefinidos en el intervalo.")
    S = y[0] + y[-1] + 4 * np.sum(y[1:-1:2]) + 2 * np.sum(y[2:-2:2])
    return (b - a) * S / (3 * n)

def simpson_doble_variable(f, x_inf, x_sup, y_inf_func, y_sup_func, nx=100, ny=100):
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
                v = 0.0
            S_y += coeff * v
        S_y *= hy / 3
        S_total += S_y
    return S_total * hx / 3

def simpson_triple_variable(f, x_inf, x_sup, y_inf_func, y_sup_func, z_inf_func, z_sup_func, nx=20, ny=20, nz=20):
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
                    v = 0.0
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

def calcular_integral(tipo: str, expresion: str, limites: dict):
    """
    Calcula la integral definida usando la Regla de Simpson compuesta,
    con manejo robusto de trigonométricas y discontinuidades.
    """
    x, y, z = sp.symbols('x y z')
    resultado = None

    try:
        print("==== DATOS RECIBIDOS ====")
        print("tipo:", tipo)
        print("expresion:", expresion)
        print("limites:", limites)

        expr = parse_math_expr(expresion) if expresion else None

        if tipo == "simple":
            a = parse_limit_string(limites["a"])
            b = parse_limit_string(limites["b"])
            print("Límite inferior procesado:", a)
            print("Límite superior procesado:", b)
            if detectar_discontinuidad(expr, a, b):
                return {"error": "La función tiene discontinuidades en el intervalo de integración. El resultado puede ser indefinido o incorrecto."}
            f = sp.lambdify(x, expr, modules=["numpy"])
            resultado = simpson_simple(f, a, b, n=10000)

        elif tipo == "doble":
            a = parse_limit_string(limites["a"])
            b = parse_limit_string(limites["b"])
            print("Límites X procesados:", a, b)
            f = sp.lambdify((x, y), expr, modules=["numpy"])
            y_inf_func = get_limit_func(limites["c"], (x,))
            y_sup_func = get_limit_func(limites["d"], (x,))
            resultado = simpson_doble_variable(
                f, a, b, y_inf_func, y_sup_func, nx=100, ny=100
            )

        elif tipo == "triple":
            a = parse_limit_string(limites["a"])
            b = parse_limit_string(limites["b"])
            print("Límites X procesados:", a, b)
            f = sp.lambdify((x, y, z), expr, modules=["numpy"])
            y_inf_func = get_limit_func(limites["c"], (x,))
            y_sup_func = get_limit_func(limites["d"], (x,))
            z_inf_func = get_limit_func(limites["e"], (x, y))
            z_sup_func = get_limit_func(limites["f"], (x, y))
            resultado = simpson_triple_variable(
                f, a, b, y_inf_func, y_sup_func, z_inf_func, z_sup_func, nx=20, ny=20, nz=20
            )
        else:
            return {"error": f"Tipo de integral no soportada: {tipo}"}

        if not _valida_resultado(resultado):
            return {"error": "El resultado de la integral es infinito o indefinido. Cambia los límites o la función."}
        return {
            "valor": float(resultado)
        }

    except Exception as e:
        import traceback
        print("==== ERROR INTERNO AL CALCULAR LA INTEGRAL ====")
        traceback.print_exc()
        return {"error": f"Error interno al calcular la integral: {str(e)}"}