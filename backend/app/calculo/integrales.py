import sympy as sp
import numpy as np

# Diccionario de funciones para sympify/lambdify (incluye sec, csc, cot)
sympy_func_dict = {
    "sin": sp.sin, "cos": sp.cos, "tan": sp.tan,
    "log": sp.log, "exp": sp.exp, "sqrt": sp.sqrt,
    "sec": sp.sec, "csc": sp.csc, "cot": sp.cot
}

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
            continue  # Salta subintervalos nulos o con orden incorrecto
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
            S_y += coeff * f(xi, yj)
        S_y *= hy / 3  # Simpson en y, para este x
        S_total += S_y
    return S_total * hx / 3  # Simpson en x

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
            continue  # Salta subintervalos nulos o invertidos para y
        y_vals = np.linspace(y_inf, y_sup, ny+1)
        hy = (y_sup - y_inf) / ny
        S_y = 0.0
        for j, yj in enumerate(y_vals):
            z_inf = z_inf_func(xi, yj)
            z_sup = z_sup_func(xi, yj)
            if z_sup <= z_inf:
                continue  # Salta subintervalos nulos o invertidos para z
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
                S_z += coeff * f(xi, yj, zk)
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
    x, y, z = sp.symbols('x y z')
    resultado = None

    try:
        if tipo == "simple":
            expr = sp.sympify(expresion, locals=sympy_func_dict)
            f = sp.lambdify(x, expr, modules=["numpy"])
            a, b = limites["a"], limites["b"]
            resultado = simpson_simple(f, a, b, n=1000)

        elif tipo == "doble":
            expr = sp.sympify(expresion, locals=sympy_func_dict)
            f = sp.lambdify((x, y), expr, modules=["numpy"])

            y_inf_expr = limites["c"]
            y_sup_expr = limites["d"]

            if isinstance(y_inf_expr, str):
                y_inf_func = sp.lambdify(x, sp.sympify(y_inf_expr, locals=sympy_func_dict), modules=["numpy"])
            else:
                y_inf_func = lambda x: y_inf_expr
            if isinstance(y_sup_expr, str):
                y_sup_func = sp.lambdify(x, sp.sympify(y_sup_expr, locals=sympy_func_dict), modules=["numpy"])
            else:
                y_sup_func = lambda x: y_sup_expr

            resultado = simpson_doble_variable(
                f, limites["a"], limites["b"], y_inf_func, y_sup_func, nx=50, ny=50
            )

        elif tipo == "triple":
            expr = sp.sympify(expresion, locals=sympy_func_dict)
            f = sp.lambdify((x, y, z), expr, modules=["numpy"])

            a, b = limites["a"], limites["b"]
            c_expr = limites["c"]
            d_expr = limites["d"]
            e_expr = limites["e"]
            f_expr = limites["f"]

            if isinstance(c_expr, str):
                y_inf_func = sp.lambdify(x, sp.sympify(c_expr, locals=sympy_func_dict), modules=["numpy"])
            else:
                y_inf_func = lambda x: c_expr

            if isinstance(d_expr, str):
                y_sup_func = sp.lambdify(x, sp.sympify(d_expr, locals=sympy_func_dict), modules=["numpy"])
            else:
                y_sup_func = lambda x: d_expr

            if isinstance(e_expr, str):
                z_inf_func = sp.lambdify([x, y], sp.sympify(e_expr, locals=sympy_func_dict), modules=["numpy"])
            else:
                z_inf_func = lambda x, y: e_expr

            if isinstance(f_expr, str):
                z_sup_func = sp.lambdify([x, y], sp.sympify(f_expr, locals=sympy_func_dict), modules=["numpy"])
            else:
                z_sup_func = lambda x, y: f_expr

            resultado = simpson_triple_variable(
                f, a, b, y_inf_func, y_sup_func, z_inf_func, z_sup_func, nx=10, ny=10, nz=10
            )

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
        return {"error": str(e)}