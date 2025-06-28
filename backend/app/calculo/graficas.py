import os
import numpy as np
import sympy
import sympy as sp
from sympy.parsing.sympy_parser import parse_expr
import plotly.graph_objs as go
import traceback

# Diccionario extendido para funciones matemáticas
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
    if isinstance(val, (float, int)):
        return float(val)
    try:
        return float(val)
    except Exception:
        pass
    try:
        if callable(val):
            if x is not None and y is None:
                return float(val(x))
            elif x is not None and y is not None:
                return float(val(x, y))
    except Exception:
        pass
    return None

def _parse_limit_func(expr, vars_):
    if isinstance(expr, (float, int)):
        return lambda *args: float(expr)
    elif isinstance(expr, str):
        try:
            return sp.lambdify(vars_, parse_expr(expr, local_dict=sympy_func_dict), modules="numpy")
        except Exception:
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
    Si modo_interactivo=False, genera PNG (matplotlib) con estilo profesional.
    """
    print("DEBUG: Entrando a generar_grafica")
    print(f"Tipo: {tipo}, Expresión: {expresion}, Límites: {limites}, Modo interactivo: {modo_interactivo}")

    os.makedirs("static/graficas", exist_ok=True)
    ruta = f"static/graficas/integral_{tipo}_{hash(str(expresion)+str(limites))}.png"
    x, y, z = sp.symbols('x y z')

    try:
        if tipo == "simple":
            expr = sp.sympify(expresion, locals=sympy_func_dict)
            expr = _asegura_escalar(expr)
            f = sp.lambdify(x, expr, modules="numpy")
            x_vals = np.linspace(limites["a"], limites["b"], 900)  # Más puntos para curva suave
            y_vals = f(x_vals)
            if not _valida_arreglo_json(y_vals):
                raise ValueError("La función tiene valores infinitos o indefinidos en el rango seleccionado. Cambia el intervalo.")

            if modo_interactivo:
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=x_vals, y=y_vals, mode='lines', fill='tozeroy', name="f(x)",
                    line=dict(color='#1f77b4', width=3)
                ))
                fig.update_layout(
                    title=f"Integral de {expresion} entre {limites['a']} y {limites['b']}",
                    xaxis_title="x",
                    yaxis_title="f(x)",
                    template="plotly_white",
                    font=dict(size=17, family="Montserrat, Arial"),
                    margin=dict(l=60, r=40, t=70, b=50),
                    xaxis=dict(showgrid=True, gridcolor="#eee"),
                    yaxis=dict(showgrid=True, gridcolor="#eee"),
                )
                # Punto inicial y final marcados
                fig.add_trace(go.Scatter(
                    x=[x_vals[0], x_vals[-1]],
                    y=[y_vals[0], y_vals[-1]],
                    mode='markers',
                    marker=dict(color='red', size=10),
                    name="Límites"
                ))
                return fig.to_dict()
            else:
                import matplotlib
                matplotlib.use('Agg')
                import matplotlib.pyplot as plt
                fig, ax = plt.subplots(figsize=(10, 6))
                ax.plot(x_vals, y_vals, 'b-', linewidth=2)
                ax.fill_between(x_vals, y_vals, alpha=0.33, color='#1f77b4')
                ax.scatter([x_vals[0], x_vals[-1]], [y_vals[0], y_vals[-1]], color='red', s=50, zorder=5)
                ax.set_title(r'Visualización de $f(x) = %s$' % sp.latex(expr), fontsize=18, pad=20)
                ax.set_xlabel('x', fontsize=14, labelpad=10)
                ax.set_ylabel('f(x)', fontsize=14, labelpad=10)
                ax.grid(True, color='#ccc', linestyle='--')
                plt.tight_layout()
                plt.savefig(ruta, dpi=220, bbox_inches='tight')
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

            nx, ny = 60, 60  # Más puntos para mayor detalle, pero razonable
            X = np.linspace(x_inf, x_sup, nx)
            Y = np.zeros((ny, nx))
            Z = np.zeros((ny, nx))
            for ix, xv in enumerate(X):
                y_min = y_inf_func(xv)
                y_max = y_sup_func(xv)
                if y_max <= y_min:
                    Y[:, ix] = np.nan
                    Z[:, ix] = np.nan
                    continue
                Y[:, ix] = np.linspace(y_min, y_max, ny)
                try:
                    Z[:, ix] = fxy(xv, Y[:, ix])
                except Exception as e:
                    print("Error en Z[:, ix] = fxy(xv, Y[:, ix])", e)
                    Z[:, ix] = np.nan

            if not _valida_arreglo_json(Z):
                raise ValueError("La función tiene valores infinitos o indefinidos en el rango seleccionado. Cambia el intervalo.")

            if modo_interactivo:
                fig = go.Figure(data=[
                    go.Surface(
                        z=Z, x=X, y=Y,
                        colorbar_title='f(x, y)',
                        colorscale='Viridis',
                        showscale=True,
                        opacity=0.97,
                        contours = {
                            "z": {"show": True, "usecolormap": True, "highlightcolor": "lime", "project_z": True}
                        }
                    ),
                    go.Contour(
                        z=Z, x=X, y=Y,
                        colorscale='Blues',
                        showscale=False,
                        opacity=0.45,
                        contours=dict(showlabels=True, labelfont=dict(size=12, color='white'))
                    )
                ])
                fig.update_layout(
                    title=f"Integral doble de {expresion} en x:[{x_inf},{x_sup}], y:funcional",
                    scene=dict(
                        xaxis_title="x",
                        yaxis_title="y",
                        zaxis_title="f(x, y)",
                        xaxis=dict(showgrid=True, gridcolor="#e1e1e1"),
                        yaxis=dict(showgrid=True, gridcolor="#e1e1e1"),
                        zaxis=dict(showgrid=True, gridcolor="#e1e1e1"),
                    ),
                    font=dict(size=16, family="Montserrat, Arial"),
                    margin=dict(l=60, r=40, t=70, b=50),
                    template="plotly_white"
                )
                return fig.to_dict()
            else:
                import matplotlib
                matplotlib.use('Agg')
                import matplotlib.pyplot as plt
                fig = plt.figure(figsize=(10, 7))
                ax = fig.add_subplot(111, projection='3d')
                surf = ax.plot_surface(X, Y, Z, cmap='viridis', edgecolor='k', linewidth=0.2, antialiased=True, alpha=0.96)
                # Añadir contornos en la base
                ax.contour(X, Y, Z, zdir='z', offset=np.nanmin(Z)-0.1*(np.nanmax(Z)-np.nanmin(Z)), cmap='Blues', linewidths=1)
                ax.set_title(r'Visualización del volumen bajo $f(x, y) = %s$' % sp.latex(expr), fontsize=18, pad=20)
                ax.set_xlabel('x', fontsize=14, labelpad=10)
                ax.set_ylabel('y', fontsize=14, labelpad=10)
                ax.set_zlabel('z', fontsize=14, labelpad=10)
                ax.grid(True, color="#bbb", linestyle='--')
                fig.colorbar(surf, shrink=0.7, aspect=15, pad=0.1)
                plt.tight_layout()
                plt.savefig(ruta, dpi=220, bbox_inches='tight')
                plt.close(fig)
                return ruta

        elif tipo == "triple":
            expr = sp.sympify(expresion, locals=sympy_func_dict)
            expr = _asegura_escalar(expr)
            fxyz = sp.lambdify((x, y, z), expr, modules="numpy")

            x_inf = _get_float_limit(limites["a"])
            x_sup = _get_float_limit(limites["b"])
            y_inf_func = _parse_limit_func(limites["c"], [x])
            y_sup_func = _parse_limit_func(limites["d"], [x])
            z_inf_func = _parse_limit_func(limites["e"], [x, y])
            z_sup_func = _parse_limit_func(limites["f"], [x, y])

            nx, ny, nz = 32, 32, 32  # Más puntos para detalle
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
                    except Exception as e:
                        print("Error en S[iy, ix] = np.nansum(vals):", e)
                        S[iy, ix] = np.nan

            if not _valida_arreglo_json(S):
                raise ValueError("La función tiene valores infinitos o indefinidos en el rango seleccionado. Cambia los límites o la función.")

            if modo_interactivo:
                fig = go.Figure(data=[
                    go.Surface(
                        z=S, x=X, y=Y,
                        colorbar_title='∫ f(x, y, z) dz',
                        colorscale='Cividis',
                        showscale=True,
                        opacity=0.97,
                        contours = {
                            "z": {"show": True, "usecolormap": True, "highlightcolor": "orange", "project_z": True}
                        }
                    ),
                    go.Contour(
                        z=S, x=X, y=Y,
                        colorscale='Oranges',
                        showscale=False,
                        opacity=0.45,
                        contours=dict(showlabels=True, labelfont=dict(size=12, color='white'))
                    )
                ])
                fig.update_layout(
                    title=f"Triple integral (suma sobre z) de {expresion} (respetando límites funcionales)",
                    scene=dict(
                        xaxis_title="x",
                        yaxis_title="y",
                        zaxis_title="Suma f(x, y, z)",
                        xaxis=dict(showgrid=True, gridcolor="#e1e1e1"),
                        yaxis=dict(showgrid=True, gridcolor="#e1e1e1"),
                        zaxis=dict(showgrid=True, gridcolor="#e1e1e1"),
                    ),
                    font=dict(size=15, family="Montserrat, Arial"),
                    margin=dict(l=60, r=40, t=70, b=50),
                    template="plotly_white"
                )
                return fig.to_dict()
            else:
                import matplotlib
                matplotlib.use('Agg')
                import matplotlib.pyplot as plt
                fig = plt.figure(figsize=(10, 7))
                ax = fig.add_subplot(111, projection='3d')
                surf = ax.plot_surface(X, Y, S, cmap='cividis', edgecolor='k', linewidth=0.2, antialiased=True, alpha=0.96)
                ax.contour(X, Y, S, zdir='z', offset=np.nanmin(S)-0.1*(np.nanmax(S)-np.nanmin(S)), cmap='Oranges', linewidths=1)
                ax.set_title(r'Visualización del volumen bajo $\int f(x, y, z)\,dz$ de %s' % sp.latex(expr), fontsize=16, pad=20)
                ax.set_xlabel('x', fontsize=14, labelpad=10)
                ax.set_ylabel('y', fontsize=14, labelpad=10)
                ax.set_zlabel('Suma f(x, y, z)', fontsize=14, labelpad=10)
                ax.grid(True, color="#bbb", linestyle='--')
                fig.colorbar(surf, shrink=0.7, aspect=15, pad=0.1)
                plt.tight_layout()
                plt.savefig(ruta, dpi=220, bbox_inches='tight')
                plt.close(fig)
                return ruta

        else:
            raise ValueError(f"Tipo de integral no soportado para graficar: {tipo}")

    except Exception as e:
        print("Error en generar_grafica:", e)
        traceback.print_exc()
        return ""