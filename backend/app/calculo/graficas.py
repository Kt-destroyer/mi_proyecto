import os
import numpy as np
import sympy
import sympy as sp
from sympy.parsing.sympy_parser import parse_expr
import plotly.graph_objs as go

# Diccionario extendido para funciones matemáticas (debes mantener igual que en math_parser.py)
sympy_func_dict = {
    "sin": sympy.sin, "cos": sympy.cos, "tan": sympy.tan,
    "log": sympy.log, "exp": sympy.exp, "sqrt": sympy.sqrt,
    "sec": sympy.sec, "csc": sympy.csc, "cot": sympy.cot,
    "asin": sympy.asin, "acos": sympy.acos, "atan": sympy.atan,
    "pi": sympy.pi, "e": sympy.E,
}

def _asegura_escalar(expr):
    if hasattr(expr, 'is_Matrix') and expr.is_Matrix:
        expr = expr.tolist()
    if hasattr(expr, 'is_Vector') and expr.is_Vector:
        expr = expr.tolist()
    if isinstance(expr, (sp.ImmutableDenseNDimArray, sp.NDimArray)):
        expr = expr.tolist()
    while isinstance(expr, (list, tuple)) and len(expr) > 0:
        expr = expr[0]
    if isinstance(expr, sp.Basic):
        try:
            expr = float(expr)
        except Exception:
            pass
    return expr

def _valida_arreglo_json(vals):
    arr = np.asarray(vals)
    return np.all(np.isfinite(arr))

def _get_float_limit(val, x=None, y=None):
    # Si es float/int, retorna directo
    if isinstance(val, (float, int)):
        return float(val)
    # Si es string que representa número
    try:
        return float(val)
    except Exception:
        pass
    # Si es función/lambda sympy
    try:
        if callable(val):
            # Si espera x, o x, y
            if x is not None and y is None:
                return float(val(x))
            elif x is not None and y is not None:
                return float(val(x, y))
    except Exception:
        pass
    return None # fallback

def _parse_limit_func(expr, vars_):
    # Devuelve una función de las variables vars_ a partir de una expresión string o numérica
    if isinstance(expr, (float, int)):
        return lambda *args: float(expr)
    elif isinstance(expr, str):
        try:
            return sp.lambdify(vars_, parse_expr(expr, local_dict=sympy_func_dict), modules="numpy")
        except Exception:
            # Si no es función, intenta forzar a float
            try:
                return lambda *args: float(expr)
            except Exception:
                raise
    elif callable(expr):
        return expr
    else:
        raise ValueError("No se pudo convertir el límite a función.")

def generar_grafica(tipo: str, expresion: str, limites: dict, modo_interactivo: bool = True):
    """
    Si modo_interactivo=True, retorna dict Plotly para frontend.
    Si modo_interactivo=False, sigue generando PNG (matplotlib).
    """
    os.makedirs("static/graficas", exist_ok=True)
    ruta = f"static/graficas/integral_{tipo}_{hash(str(expresion)+str(limites))}.png"
    x, y, z = sp.symbols('x y z')

    if tipo == "simple":
        expr = sp.sympify(expresion, locals=sympy_func_dict)
        expr = _asegura_escalar(expr)
        f = sp.lambdify(x, expr, modules="numpy")
        x_vals = np.linspace(limites["a"], limites["b"], 500)
        y_vals = f(x_vals)
        if not _valida_arreglo_json(y_vals):
            raise ValueError("La función tiene valores infinitos o indefinidos en el rango seleccionado. Cambia el intervalo.")

        if modo_interactivo:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=x_vals, y=y_vals, mode='lines', fill='tozeroy', name="f(x)"))
            fig.update_layout(
                title=f"Integral de {sp.latex(expr)} entre {limites['a']} y {limites['b']}",
                xaxis_title="x", yaxis_title="f(x)",
                template="plotly_white"
            )
            return fig.to_dict()
        else:
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
            if np.isscalar(y_vals):
                y_vals = np.full_like(x_vals, y_vals)
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.plot(x_vals, y_vals, 'b-', linewidth=2)
            ax.fill_between(x_vals, y_vals, alpha=0.3)
            ax.set_title(f"Integral de ${sp.latex(expr)}$ entre {limites['a']} y {limites['b']}")
            ax.set_xlabel("x")
            ax.set_ylabel("f(x)")
            ax.grid(True)
            plt.tight_layout()
            plt.savefig(ruta)
            plt.close(fig)
            return ruta

    elif tipo == "doble":
        expr = sp.sympify(expresion, locals=sympy_func_dict)
        expr = _asegura_escalar(expr)
        fxy = sp.lambdify((x, y), expr, modules="numpy")
        x_inf = _get_float_limit(limites["a"])
        x_sup = _get_float_limit(limites["b"])
        y_inf_func = _parse_limit_func(limites["c"], [x])
        y_sup_func = _parse_limit_func(limites["d"], [x])

        # Para cada x en la grilla, calcula los límites funcionales de y
        nx, ny = 40, 40
        X = np.linspace(x_inf, x_sup, nx)
        Y = np.zeros((ny, nx))
        Z = np.zeros((ny, nx))
        for ix, xv in enumerate(X):
            y_min = y_inf_func(xv)
            y_max = y_sup_func(xv)
            # Si los límites son inválidos, rellena con nan
            if y_max <= y_min:
                Y[:, ix] = np.nan
                Z[:, ix] = np.nan
                continue
            Y[:, ix] = np.linspace(y_min, y_max, ny)
            try:
                Z[:, ix] = fxy(xv, Y[:, ix])
            except Exception:
                Z[:, ix] = np.nan

        if not _valida_arreglo_json(Z):
            raise ValueError("La función tiene valores infinitos o indefinidos en el rango seleccionado. Cambia el intervalo.")

        if modo_interactivo:
            fig = go.Figure(data=[go.Surface(z=Z, x=X, y=Y, colorbar_title='f(x, y)')])
            fig.update_layout(
                title=f"Integral doble de {sp.latex(expr)} en x:[{x_inf},{x_sup}], y:funcional",
                scene=dict(
                    xaxis_title="x",
                    yaxis_title="y",
                    zaxis_title="f(x, y)"
                ),
                template="plotly_white"
            )
            return fig.to_dict()
        else:
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
            fig = plt.figure(figsize=(8,6))
            ax = fig.add_subplot(111, projection='3d')
            ax.plot_surface(X, Y, Z, cmap='viridis', edgecolor='none')
            ax.set_title(f"Integral doble de ${sp.latex(expr)}$")
            ax.set_xlabel('x')
            ax.set_ylabel('y')
            ax.set_zlabel('f(x, y)')
            plt.tight_layout()
            plt.savefig(ruta)
            plt.close(fig)
            return ruta

    elif tipo == "triple":
        # Mostramos para cada (x, y) la suma sobre z respetando límites funcionales
        expr = sp.sympify(expresion, locals=sympy_func_dict)
        expr = _asegura_escalar(expr)
        fxyz = sp.lambdify((x, y, z), expr, modules="numpy")

        x_inf = _get_float_limit(limites["a"])
        x_sup = _get_float_limit(limites["b"])
        y_inf_func = _parse_limit_func(limites["c"], [x])
        y_sup_func = _parse_limit_func(limites["d"], [x])
        z_inf_func = _parse_limit_func(limites["e"], [x, y])
        z_sup_func = _parse_limit_func(limites["f"], [x, y])

        nx, ny, nz = 15, 15, 15
        X = np.linspace(x_inf, x_sup, nx)
        Y = np.zeros((ny, nx))
        S = np.zeros((ny, nx))
        for ix, xv in enumerate(X):
            y_min = y_inf_func(xv)
            y_max = y_sup_func(xv)
            if y_max <= y_min:
                Y[:, ix] = np.nan
                S[:, ix] = np.nan
                continue
            Y[:, ix] = np.linspace(y_min, y_max, ny)
            for iy, yv in enumerate(Y[:, ix]):
                z_min = z_inf_func(xv, yv)
                z_max = z_sup_func(xv, yv)
                if z_max <= z_min:
                    S[iy, ix] = np.nan
                    continue
                Z = np.linspace(z_min, z_max, nz)
                try:
                    vals = fxyz(xv, yv, Z)
                    S[iy, ix] = np.nansum(vals)
                except Exception:
                    S[iy, ix] = np.nan

        if not _valida_arreglo_json(S):
            raise ValueError("La función tiene valores infinitos o indefinidos en el rango seleccionado. Cambia los límites o la función.")

        if modo_interactivo:
            fig = go.Figure(data=[go.Surface(z=S, x=X, y=Y, colorbar_title='∫ f(x, y, z) dz')])
            fig.update_layout(
                title=f"Triple integral (suma sobre z) de {sp.latex(expr)} (respetando límites funcionales)",
                scene=dict(
                    xaxis_title="x",
                    yaxis_title="y",
                    zaxis_title="Suma f(x, y, z)"
                ),
                template="plotly_white"
            )
            return fig.to_dict()
        else:
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
            fig = plt.figure(figsize=(8,6))
            ax = fig.add_subplot(111, projection='3d')
            ax.plot_surface(X, Y, S, cmap='plasma', edgecolor='none')
            ax.set_title(f"Triple integral (suma sobre z) de ${sp.latex(expr)}$")
            ax.set_xlabel('x')
            ax.set_ylabel('y')
            ax.set_zlabel('Suma f(x, y, z)')
            plt.tight_layout()
            plt.savefig(ruta)
            plt.close(fig)
            return ruta

    else:
        raise ValueError(f"Tipo de integral no soportado para graficar: {tipo}")