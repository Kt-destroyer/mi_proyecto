import sympy as sp
import numpy as np

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
    S = 0.0
    for i, xi in enumerate(x_vals):
        y_inf = y_inf_func(xi)
        y_sup = y_sup_func(xi)
        y_vals = np.linspace(y_inf, y_sup, ny+1)
        hy = (y_sup - y_inf) / ny
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
            S += coeff * f(xi, yj)
        S *= hy / 3  # Simpson en y, para cada x
    return S * hx / 3  # Simpson en x

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
    S = 0.0
    for i, xi in enumerate(x_vals):
        y_inf = y_inf_func(xi)
        y_sup = y_sup_func(xi)
        y_vals = np.linspace(y_inf, y_sup, ny+1)
        hy = (y_sup - y_inf) / ny
        for j, yj in enumerate(y_vals):
            z_inf = z_inf_func(xi, yj)
            z_sup = z_sup_func(xi, yj)
            z_vals = np.linspace(z_inf, z_sup, nz+1)
            hz = (z_sup - z_inf) / nz
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
                S += coeff * f(xi, yj, zk)
            S *= hz / 3
        S *= hy / 3
    return S * hx / 3

def calcular_integral(tipo: str, expresion: str, limites: dict):
    """
    Calcula integrales simples, dobles (con límites variables) o triples (con internos funcionales).
    Retorna: {"valor": float, "grafica": "ruta/imagen.png"}
    """
    x, y, z = sp.symbols('x y z')
    resultado = None

    try:
        if tipo == "simple":
            expr = sp.sympify(expresion)
            f = sp.lambdify(x, expr, modules=['numpy'])
            a, b = limites["a"], limites["b"]
            resultado = simpson_simple(f, a, b, n=1000)

        elif tipo == "doble":
            expr = sp.sympify(expresion)
            f = sp.lambdify((x, y), expr, modules=['numpy'])

            y_inf_expr = limites["c"]
            y_sup_expr = limites["d"]

            if isinstance(y_inf_expr, str):
                y_inf_parsed = sp.sympify(y_inf_expr)
                y_inf_func = sp.lambdify(x, y_inf_parsed, modules=['numpy'])
            elif isinstance(y_inf_expr, sp.Basic):
                y_inf_func = sp.lambdify(x, y_inf_expr, modules=['numpy'])
            else:
                y_inf_func = lambda x: y_inf_expr

            if isinstance(y_sup_expr, str):
                y_sup_parsed = sp.sympify(y_sup_expr)
                y_sup_func = sp.lambdify(x, y_sup_parsed, modules=['numpy'])
            elif isinstance(y_sup_expr, sp.Basic):
                y_sup_func = sp.lambdify(x, y_sup_expr, modules=['numpy'])
            else:
                y_sup_func = lambda x: y_sup_expr

            resultado = simpson_doble_variable(
                f, limites["a"], limites["b"], y_inf_func, y_sup_func, nx=50, ny=50
            )

        elif tipo == "triple":
            expr = sp.sympify(expresion)
            f = sp.lambdify((x, y, z), expr, modules=['numpy'])

            a, b = limites["a"], limites["b"]
            c_expr = limites["c"]
            d_expr = limites["d"]
            e_expr = limites["e"]
            f_expr = limites["f"]

            # y_inf, y_sup pueden ser funciones de x
            if isinstance(c_expr, str):
                y_inf_parsed = sp.sympify(c_expr)
                y_inf_func = sp.lambdify(x, y_inf_parsed, modules=['numpy'])
            elif isinstance(c_expr, sp.Basic):
                y_inf_func = sp.lambdify(x, c_expr, modules=['numpy'])
            else:
                y_inf_func = lambda x: c_expr

            if isinstance(d_expr, str):
                y_sup_parsed = sp.sympify(d_expr)
                y_sup_func = sp.lambdify(x, y_sup_parsed, modules=['numpy'])
            elif isinstance(d_expr, sp.Basic):
                y_sup_func = sp.lambdify(x, d_expr, modules=['numpy'])
            else:
                y_sup_func = lambda x: d_expr

            # z_inf, z_sup pueden ser funciones de x, y
            if isinstance(e_expr, str):
                z_inf_parsed = sp.sympify(e_expr)
                z_inf_func = sp.lambdify([x, y], z_inf_parsed, modules=['numpy'])
            elif isinstance(e_expr, sp.Basic):
                z_inf_func = sp.lambdify([x, y], e_expr, modules=['numpy'])
            else:
                z_inf_func = lambda x, y: e_expr

            if isinstance(f_expr, str):
                z_sup_parsed = sp.sympify(f_expr)
                z_sup_func = sp.lambdify([x, y], z_sup_parsed, modules=['numpy'])
            elif isinstance(f_expr, sp.Basic):
                z_sup_func = sp.lambdify([x, y], f_expr, modules=['numpy'])
            else:
                z_sup_func = lambda x, y: f_expr

            resultado = simpson_triple_variable(
                f, a, b, y_inf_func, y_sup_func, z_inf_func, z_sup_func, nx=10, ny=10, nz=10
            )

        else:
            return {"error": f"Tipo de integral no soportada: {tipo}"}

        # La gráfica se genera en main.py, así que retornamos solo el resultado aquí
        return {
            "valor": float(resultado),
            "grafica": ""  # la gráfica se maneja en main.py
        }

    except Exception as e:
        print(f"Error al calcular integral: {str(e)}")
        return {"error": str(e)}