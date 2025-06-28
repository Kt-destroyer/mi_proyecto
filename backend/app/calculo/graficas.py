import os
import numpy as np
import sympy
import sympy as sp
from sympy.parsing.sympy_parser import parse_expr
import traceback

# Diccionario extendido para funciones matemáticas
sympy_func_dict = {
    "sin": sympy.sin, "cos": sympy.cos, "tan": sympy.tan,
    "log": sympy.log, "exp": sympy.exp, "sqrt": sympy.sqrt,
    "sec": sympy.sec, "csc": sympy.csc, "cot": sympy.cot,
    "asin": sympy.asin, "acos": sympy.acos, "atan": sympy.atan,
    "pi": sympy.pi, "e": sympy.E,
}

def parse_limit_string(val):
    # Convierte un string como "pi", "2*pi", "e", "3.5", etc. a float usando sympy
    try:
        expr = sympy.sympify(val, locals=sympy_func_dict)
        return float(expr.evalf())
    except Exception:
        raise ValueError(f"Límite inválido: {val}")

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

def _parse_limit_func(expr, vars_):
    # Devuelve una función de las variables vars_ a partir de una expresión string o numérica
    if isinstance(expr, (float, int)):
        return lambda *args: float(expr)
    elif isinstance(expr, str):
        try:
            return sp.lambdify(vars_, parse_expr(expr, local_dict=sympy_func_dict), modules="numpy")
        except Exception:
            # Si no es función, intenta forzar a float interpretando como expresión sympy
            try:
                return lambda *args: float(sympy.sympify(expr, locals=sympy_func_dict).evalf())
            except Exception:
                raise
    elif callable(expr):
        return expr
    else:
        raise ValueError("No se pudo convertir el límite a función.")

def generar_grafica(tipo: str, expresion: str, limites: dict, modo_interactivo: bool = True):
    """
    Siempre genera PNG (matplotlib) con estilo profesional.
    """
    print("DEBUG: Entrando a generar_grafica")
    print(f"Tipo: {tipo}, Expresión: {expresion}, Límites: {limites}")

    os.makedirs("static/graficas", exist_ok=True)
    ruta = f"static/graficas/integral_{tipo}_{hash(str(expresion)+str(limites))}.png"
    x, y, z = sp.symbols('x y z')

    try:
        if tipo == "simple":
            expr = sp.sympify(expresion, locals=sympy_func_dict)
            expr = _asegura_escalar(expr)
            f = sp.lambdify(x, expr, modules="numpy")
            x_vals = np.linspace(parse_limit_string(limites["a"]), parse_limit_string(limites["b"]), 500)
            y_vals = f(x_vals)
            if not _valida_arreglo_json(y_vals):
                raise ValueError("La función tiene valores infinitos o indefinidos en el rango seleccionado. Cambia el intervalo.")

            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.plot(x_vals, y_vals, 'b-', linewidth=2)
            ax.fill_between(x_vals, y_vals, alpha=0.3)
            ax.set_title(r'Visualización de $f(x) = %s$' % sp.latex(expr), fontsize=18, pad=20)
            ax.set_xlabel('x', fontsize=14, labelpad=10)
            ax.set_ylabel('f(x)', fontsize=14, labelpad=10)
            ax.grid(True)
            plt.tight_layout()
            plt.savefig(ruta, dpi=200, bbox_inches='tight')
            plt.close(fig)
            return ruta

        elif tipo == "doble":
            expr = sp.sympify(expresion, locals=sympy_func_dict)
            expr = _asegura_escalar(expr)
            fxy = sp.lambdify((x, y), expr, modules="numpy")
            x_inf = parse_limit_string(limites["a"])
            x_sup = parse_limit_string(limites["b"])
            y_inf_func = _parse_limit_func(limites["c"], [x])
            y_sup_func = _parse_limit_func(limites["d"], [x])

            nx, ny = 40, 40
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

            # Solo aborta si TODOS los valores son NaN o infinitos, no si hay algunos NaN
            if not np.any(np.isfinite(Z)):
                raise ValueError("No hay datos válidos para graficar (todos los valores son NaN o infinitos). Cambia el intervalo.")

            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
            fig = plt.figure(figsize=(8, 6))
            ax = fig.add_subplot(111, projection='3d')
            surf = ax.plot_surface(X, Y, Z, cmap='plasma', edgecolor='k', linewidth=0.5, antialiased=True)
            ax.set_title(r'Visualización del volumen bajo $f(x, y) = %s$' % sp.latex(expr), fontsize=18, pad=20)
            ax.set_xlabel('x', fontsize=14, labelpad=10)
            ax.set_ylabel('y', fontsize=14, labelpad=10)
            ax.set_zlabel('z', fontsize=14, labelpad=10)
            fig.colorbar(surf, shrink=0.7, aspect=15, pad=0.1)
            plt.tight_layout()
            plt.savefig(ruta, dpi=200, bbox_inches='tight')
            plt.close(fig)
            return ruta

        elif tipo == "triple":
            expr = sp.sympify(expresion, locals=sympy_func_dict)
            expr = _asegura_escalar(expr)
            fxyz = sp.lambdify((x, y, z), expr, modules="numpy")

            x_inf = parse_limit_string(limites["a"])
            x_sup = parse_limit_string(limites["b"])
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
                    except Exception as e:
                        print("Error en S[iy, ix] = np.nansum(vals):", e)
                        S[iy, ix] = np.nan

            if not np.any(np.isfinite(S)):
                raise ValueError("No hay datos válidos para graficar (todos los valores son NaN o infinitos). Cambia los límites o la función.")

            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
            fig = plt.figure(figsize=(8, 6))
            ax = fig.add_subplot(111, projection='3d')
            surf = ax.plot_surface(X, Y, S, cmap='plasma', edgecolor='k', linewidth=0.5, antialiased=True)
            ax.set_title(r'Visualización del volumen bajo $\int f(x, y, z)\,dz$ de %s' % sp.latex(expr), fontsize=16, pad=20)
            ax.set_xlabel('x', fontsize=14, labelpad=10)
            ax.set_ylabel('y', fontsize=14, labelpad=10)
            ax.set_zlabel('Suma f(x, y, z)', fontsize=14, labelpad=10)
            fig.colorbar(surf, shrink=0.7, aspect=15, pad=0.1)
            plt.tight_layout()
            plt.savefig(ruta, dpi=200, bbox_inches='tight')
            plt.close(fig)
            return ruta

        else:
            raise ValueError(f"Tipo de integral no soportado para graficar: {tipo}")

    except Exception as e:
        print("Error en generar_grafica:", e)
        traceback.print_exc()
        return ""