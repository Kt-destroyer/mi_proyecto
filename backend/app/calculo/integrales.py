import sympy as sp
import numpy as np
from .graficas import generar_grafica

def simpson_doble_variable(f, x_inf, x_sup, y_inf_func, y_sup_func, nx=50, ny=50):
    if nx % 2: nx += 1
    if ny % 2: ny += 1
    x_vals = np.linspace(x_inf, x_sup, nx+1)
    hx = (x_sup - x_inf) / nx
    S = 0.0
    for i, xi in enumerate(x_vals):
        # Calcula los límites variables para y
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

def calcular_integral(tipo: str, expresion: str, limites: dict):
    """
    Calcula integrales simples, dobles (con límites variables) o triples (solo constantes).
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

            # Permite límites variables en y (enviados como strings)
            y_inf_expr = limites["c"]
            y_sup_expr = limites["d"]

            # Si los límites son funciones (strings), conviértelos con sympy
            if isinstance(y_inf_expr, str):
                y_inf_func = sp.lambdify(x, sp.sympify(y_inf_expr), modules=['numpy'])
            else:
                y_inf_func = lambda x: y_inf_expr
            if isinstance(y_sup_expr, str):
                y_sup_func = sp.lambdify(x, sp.sympify(y_sup_expr), modules=['numpy'])
            else:
                y_sup_func = lambda x: y_sup_expr

            resultado = simpson_doble_variable(f, limites["a"], limites["b"], y_inf_func, y_sup_func, nx=50, ny=50)

        elif tipo == "triple":
            # Por simplicidad en este ejemplo, solo límites constantes (puedes extenderlo análogamente)
            expr = sp.sympify(expresion)
            f = sp.lambdify((x, y, z), expr, modules=['numpy'])
            resultado = simpson_triple(f, limites["a"], limites["b"], limites["c"], limites["d"], limites["e"], limites["f"], nx=10, ny=10, nz=10)

        else:
            return {"error": f"Tipo de integral no soportada: {tipo}"}

        ruta_grafica = generar_grafica(tipo, expresion, limites)
        return {
            "valor": float(resultado),
            "grafica": ruta_grafica
        }

    except Exception as e:
        print(f"Error al calcular integral: {str(e)}")
        return {"error": str(e)}

# No olvides incluir también simpson_simple y simpson_triple, igual que antes.
def simpson_simple(f, a, b, n=1000):
    if n % 2:
        n += 1
    h = (b - a) / n
    x = np.linspace(a, b, n+1)
    y = f(x)
    S = y[0] + y[-1] + 4 * np.sum(y[1:-1:2]) + 2 * np.sum(y[2:-2:2])
    return S * h / 3

def simpson_triple(f, x_inf, x_sup, y_inf, y_sup, z_inf, z_sup, nx=10, ny=10, nz=10):
    if nx % 2: nx += 1
    if ny % 2: ny += 1
    if nz % 2: nz += 1
    x = np.linspace(x_inf, x_sup, nx+1)
    y = np.linspace(y_inf, y_sup, ny+1)
    z = np.linspace(z_inf, z_sup, nz+1)
    hx = (x_sup - x_inf) / nx
    hy = (y_sup - y_inf) / ny
    hz = (z_sup - z_inf) / nz
    S = 0.0
    for i in range(nx+1):
        for j in range(ny+1):
            for k in range(nz+1):
                coeff = 1
                for idx, n in zip((i, j, k), (nx, ny, nz)):
                    if idx == 0 or idx == n:
                        coeff *= 1
                    elif idx % 2 == 1:
                        coeff *= 4
                    else:
                        coeff *= 2
                S += coeff * f(x[i], y[j], z[k])
    return S * hx * hy * hz / 27