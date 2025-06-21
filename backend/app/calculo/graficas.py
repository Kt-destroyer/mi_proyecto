import numpy as np

# ---- MATPLOTLIB SERVER FIX ----
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
# ---- FIN FIX ----

import sympy as sp
import os
from matplotlib import cm

# Diccionario para sympify/lambdify con funciones trigonométricas extendidas
sympy_func_dict = {
    "sin": sp.sin, "cos": sp.cos, "tan": sp.tan,
    "log": sp.log, "exp": sp.exp, "sqrt": sp.sqrt,
    "sec": sp.sec, "csc": sp.csc, "cot": sp.cot
}

def generar_grafica(tipo: str, expresion: str, limites: dict):
    """
    Genera gráficas para integrales y las guarda en ./static/graficas/
    """
    os.makedirs("static/graficas", exist_ok=True)
    ruta = f"static/graficas/integral_{tipo}_{hash(str(expresion)+str(limites))}.png"
    x, y, z = sp.symbols('x y z')
    plt.close('all')

    if tipo == "simple":
        expr = sp.sympify(expresion, locals=sympy_func_dict)
        f = sp.lambdify(x, expr, modules=[sympy_func_dict, "numpy"])
        x_vals = np.linspace(limites["a"], limites["b"], 500)
        y_vals = f(x_vals)
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
        fxy = sp.lambdify((x, y), expr, modules=[sympy_func_dict, "numpy"])
        x_inf = limites["a"]
        x_sup = limites["b"]
        y_inf_expr = limites["c"]
        y_sup_expr = limites["d"]

        # Soporta funciones o constantes para los límites de y
        if isinstance(y_inf_expr, str):
            y_inf_func = sp.lambdify(x, sp.sympify(y_inf_expr, locals=sympy_func_dict), modules=[sympy_func_dict, "numpy"])
        else:
            y_inf_func = lambda x: y_inf_expr
        if isinstance(y_sup_expr, str):
            y_sup_func = sp.lambdify(x, sp.sympify(y_sup_expr, locals=sympy_func_dict), modules=[sympy_func_dict, "numpy"])
        else:
            y_sup_func = lambda x: y_sup_expr

        X = np.linspace(x_inf, x_sup, 50)
        Xg, Yg = [], []
        for xi in X:
            y1i, y2i = y_inf_func(xi), y_sup_func(xi)
            Yg.append(np.linspace(y1i, y2i, 50))
            Xg.append(np.full(50, xi))
        Xg = np.concatenate(Xg)
        Yg = np.concatenate(Yg)
        Zg = fxy(Xg, Yg)

        fig = plt.figure(figsize=(10, 7))
        ax = fig.add_subplot(111, projection='3d')
        ax.plot_trisurf(Xg, Yg, Zg, alpha=0.6, cmap=cm.viridis, linewidth=0.1)
        # Curvas de frontera en z=0
        Y1 = y_inf_func(X)
        Y2 = y_sup_func(X)
        # --- FIX: Asegura que Y1 y Y2 sean arrays del mismo tamaño que X ---
        if np.isscalar(Y1):
            Y1 = np.full_like(X, Y1)
        if np.isscalar(Y2):
            Y2 = np.full_like(X, Y2)
        # ---------------------------------------------------------------
        ax.plot(X, Y1, np.zeros_like(X), color='brown', linewidth=2, label="y_inf(x) en z=0")
        ax.plot(X, Y2, np.zeros_like(X), color='green', linewidth=2, label="y_sup(x) en z=0")
        # Curvas sobre la superficie
        ax.plot(X, Y1, fxy(X, Y1), color='brown', linestyle='--', linewidth=2, label="y_inf(x) sobre f(x,y)")
        ax.plot(X, Y2, fxy(X, Y2), color='green', linestyle='--', linewidth=2, label="y_sup(x) sobre f(x,y)")
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.set_zlabel("z")
        ax.legend()
        plt.tight_layout()
        plt.savefig(ruta)
        plt.close(fig)
        return ruta

    elif tipo == "triple":
        x_inf = limites["a"]
        x_sup = limites["b"]
        y_inf_expr = limites["c"]
        y_sup_expr = limites["d"]
        z_inf_expr = limites["e"]
        z_sup_expr = limites["f"]

        # Soporta funciones o constantes para los límites de y y z
        if isinstance(y_inf_expr, str):
            y_inf_func = sp.lambdify(x, sp.sympify(y_inf_expr, locals=sympy_func_dict), modules=[sympy_func_dict, "numpy"])
        else:
            y_inf_func = lambda x: y_inf_expr

        if isinstance(y_sup_expr, str):
            y_sup_func = sp.lambdify(x, sp.sympify(y_sup_expr, locals=sympy_func_dict), modules=[sympy_func_dict, "numpy"])
        else:
            y_sup_func = lambda x: y_sup_expr

        if isinstance(z_inf_expr, str):
            z_inf_func = sp.lambdify([x, y], sp.sympify(z_inf_expr, locals=sympy_func_dict), modules=[sympy_func_dict, "numpy"])
        else:
            z_inf_func = lambda x, y: z_inf_expr

        if isinstance(z_sup_expr, str):
            z_sup_func = sp.lambdify([x, y], sp.sympify(z_sup_expr, locals=sympy_func_dict), modules=[sympy_func_dict, "numpy"])
        else:
            z_sup_func = lambda x, y: z_sup_expr

        X = np.linspace(x_inf, x_sup, 15)
        Y_low = y_inf_func(X)
        Y_high = y_sup_func(X)
        # --- FIX: Asegura que Y_low y Y_high sean arrays del mismo tamaño que X ---
        if np.isscalar(Y_low):
            Y_low = np.full_like(X, Y_low)
        if np.isscalar(Y_high):
            Y_high = np.full_like(X, Y_high)
        # ---------------------------------------------------------------

        fig = plt.figure(figsize=(8, 7))
        ax = fig.add_subplot(111, projection='3d')

        # Superficies laterales (bordes)
        for i in range(len(X)):
            y0 = Y_low[i]
            y1 = Y_high[i]
            y_arr = np.linspace(y0, y1, 15)
            x_arr = np.full_like(y_arr, X[i])
            z_inf_arr = z_inf_func(X[i], y_arr)
            z_sup_arr = z_sup_func(X[i], y_arr)
            ax.plot(x_arr, y_arr, z_inf_arr, color='red', alpha=0.7, linewidth=1)
            ax.plot(x_arr, y_arr, z_sup_arr, color='blue', alpha=0.7, linewidth=1)
            ax.plot([X[i]]*2, [y0, y1], [z_inf_func(X[i], y0), z_inf_func(X[i], y1)], 'r--', alpha=0.5)
            ax.plot([X[i]]*2, [y0, y1], [z_sup_func(X[i], y0), z_sup_func(X[i], y1)], 'b--', alpha=0.5)

        # Caras en y = y_inf(x), y = y_sup(x)
        Y = np.linspace(np.min(Y_low), np.max(Y_high), 15)
        for j in range(len(Y)):
            x_arr = np.linspace(x_inf, x_sup, 15)
            y_arr = np.full_like(x_arr, Y[j])
            try:
                z_inf_arr = z_inf_func(x_arr, y_arr)
                z_sup_arr = z_sup_func(x_arr, y_arr)
                ax.plot(x_arr, y_arr, z_inf_arr, color='green', alpha=0.5, linewidth=1)
                ax.plot(x_arr, y_arr, z_sup_arr, color='purple', alpha=0.5, linewidth=1)
            except Exception:
                continue

        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.set_zlabel("z")
        ax.set_title("Región de integración triple (bordes)")
        ax.view_init(elev=25, azim=45)
        plt.tight_layout()
        plt.savefig(ruta)
        plt.close(fig)
        return ruta

    else:
        return ""