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
        y_inf = limites["c"]
        y_sup = limites["d"]

        # Si los límites son strings, evalúa como float (constantes). Si son funciones, usa extremos.
        if isinstance(y_inf, str):
            try:
                y_inf_eval = float(y_inf)
            except Exception:
                y_inf_func = sp.lambdify(x, parse_expr(y_inf, local_dict=sympy_func_dict), modules="numpy")
                y_inf_eval = y_inf_func(x_inf)
        else:
            y_inf_eval = float(y_inf)
        if isinstance(y_sup, str):
            try:
                y_sup_eval = float(y_sup)
            except Exception:
                y_sup_func = sp.lambdify(x, parse_expr(y_sup, local_dict=sympy_func_dict), modules="numpy")
                y_sup_eval = y_sup_func(x_sup)
        else:
            y_sup_eval = float(y_sup)

        X = np.linspace(x_inf, x_sup, 60)
        Y = np.linspace(y_inf_eval, y_sup_eval, 60)
        XX, YY = np.meshgrid(X, Y)
        try:
            Z = fxy(XX, YY)
        except Exception:
            Z = np.zeros_like(XX)

        if not _valida_arreglo_json(Z):
            raise ValueError("La función tiene valores infinitos o indefinidos en el rango seleccionado. Cambia el intervalo.")

        if modo_interactivo:
            fig = go.Figure(data=[go.Surface(z=Z, x=XX, y=YY, colorbar_title='f(x, y)')])
            fig.update_layout(
                title=f"Integral doble de {sp.latex(expr)} en x:[{x_inf},{x_sup}], y:[{y_inf_eval},{y_sup_eval}]",
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
            ax.plot_surface(XX, YY, Z, cmap='viridis', edgecolor='none')
            ax.set_title(f"Integral doble de ${sp.latex(expr)}$")
            ax.set_xlabel('x')
            ax.set_ylabel('y')
            ax.set_zlabel('f(x, y)')
            plt.tight_layout()
            plt.savefig(ruta)
            plt.close(fig)
            return ruta

    elif tipo == "triple":
        # Normalmente no se puede graficar 4D, pero mostramos una suma en cubo
        expr = sp.sympify(expresion, locals=sympy_func_dict)
        expr = _asegura_escalar(expr)
        fxyz = sp.lambdify((x, y, z), expr, modules="numpy")

        x_inf = _get_float_limit(limites["a"])
        x_sup = _get_float_limit(limites["b"])
        y_inf = limites["c"]
        y_sup = limites["d"]
        z_inf = limites["e"]
        z_sup = limites["f"]

        if isinstance(y_inf, str):
            try:
                y_inf_eval = float(y_inf)
            except Exception:
                y_inf_func = sp.lambdify(x, parse_expr(y_inf, local_dict=sympy_func_dict), modules="numpy")
                y_inf_eval = y_inf_func(x_inf)
        else:
            y_inf_eval = float(y_inf)
        if isinstance(y_sup, str):
            try:
                y_sup_eval = float(y_sup)
            except Exception:
                y_sup_func = sp.lambdify(x, parse_expr(y_sup, local_dict=sympy_func_dict), modules="numpy")
                y_sup_eval = y_sup_func(x_sup)
        else:
            y_sup_eval = float(y_sup)

        if isinstance(z_inf, str):
            try:
                z_inf_eval = float(z_inf)
            except Exception:
                z_inf_func = sp.lambdify([x, y], parse_expr(z_inf, local_dict=sympy_func_dict), modules="numpy")
                z_inf_eval = z_inf_func(x_inf, y_inf_eval)
        else:
            z_inf_eval = float(z_inf)
        if isinstance(z_sup, str):
            try:
                z_sup_eval = float(z_sup)
            except Exception:
                z_sup_func = sp.lambdify([x, y], parse_expr(z_sup, local_dict=sympy_func_dict), modules="numpy")
                z_sup_eval = z_sup_func(x_sup, y_sup_eval)
        else:
            z_sup_eval = float(z_sup)

        X = np.linspace(x_inf, x_sup, 15)
        Y = np.linspace(y_inf_eval, y_sup_eval, 15)
        Z = np.linspace(z_inf_eval, z_sup_eval, 15)

        # Para visualizar algo: sumamos f(x, y, z) para cada xy como "colormap"
        XX, YY = np.meshgrid(X, Y)
        try:
            vals = np.zeros_like(XX)
            for i in range(len(X)):
                for j in range(len(Y)):
                    fz = [fxyz(X[i], Y[j], zz) for zz in Z]
                    vals[j, i] = np.sum(fz)
        except Exception:
            vals = np.zeros_like(XX)

        if not _valida_arreglo_json(vals):
            raise ValueError("La función tiene valores infinitos o indefinidos en el rango seleccionado. Cambia el intervalo.")

        if modo_interactivo:
            fig = go.Figure(data=[go.Surface(z=vals, x=XX, y=YY, colorbar_title='∫ f(x, y, z) dz')])
            fig.update_layout(
                title=f"Triple integral (suma sobre z) de {sp.latex(expr)}",
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
            ax.plot_surface(XX, YY, vals, cmap='plasma', edgecolor='none')
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