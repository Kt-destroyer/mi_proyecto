import numpy as np
import matplotlib.pyplot as plt
import sympy as sp
import os

def generar_grafica(tipo, expresion, limites):
    """
    Genera la gráfica según el tipo de integral.
    Para dobles: grafica la región y la función f(x, y) en la región.
    Para triples: grafica los bordes de integración en 3D.
    """
    if not os.path.exists("static"):
        os.makedirs("static")

    if tipo == "simple":
        x = sp.symbols('x')
        expr = sp.sympify(expresion)
        f = sp.lambdify(x, expr, modules=['numpy'])
        a, b = limites["a"], limites["b"]
        x_vals = np.linspace(a, b, 400)
        y_vals = f(x_vals)
        fig, ax = plt.subplots(figsize=(7, 5))
        ax.plot(x_vals, y_vals, "b", label=f"f(x)={expresion}")
        ax.fill_between(x_vals, y_vals, color="skyblue", alpha=0.5)
        ax.set_xlabel("x", fontsize=14)
        ax.set_ylabel("f(x)", fontsize=14)
        ax.set_title(f"Integral de {expresion}\n", fontsize=16)
        ax.axhline(0, color='black', linewidth=1.5)
        ax.axvline(0, color='black', linewidth=1.5)
        plt.tight_layout()
        img_path = f"static/simple_{np.random.randint(1e6)}.png"
        plt.savefig(img_path)
        plt.close(fig)
        return img_path

    elif tipo == "doble":
        x, y = sp.symbols('x y')
        expr = sp.sympify(expresion)
        fxy = sp.lambdify((x, y), expr, modules=["numpy"])
        x_inf = limites["a"]
        x_sup = limites["b"]
        y_inf_expr = limites["c"]
        y_sup_expr = limites["d"]
        y_inf_func = sp.lambdify(x, sp.sympify(y_inf_expr), modules=["numpy"])
        y_sup_func = sp.lambdify(x, sp.sympify(y_sup_expr), modules=["numpy"])

        # 1. Región en 2D (x, y)
        fig, ax = plt.subplots(figsize=(7, 5))
        X = np.linspace(x_inf, x_sup, 200)
        Y1 = y_inf_func(X)
        Y2 = y_sup_func(X)
        ax.plot(X, Y1, 'r--', linewidth=2, label='y inferior')
        ax.plot(X, Y2, 'g--', linewidth=2, label='y superior')
        ax.fill_between(X, Y1, Y2, color='red', alpha=0.09)
        ax.set_title("Región de integración doble", fontsize=15)
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        y_min = min(np.min(Y1), np.min(Y2), 0) - 1
        y_max = max(np.max(Y1), np.max(Y2), 0) + 2
        ax.set_xlim(x_inf, x_sup)
        ax.set_ylim(y_min, y_max)
        ax.legend()
        plt.tight_layout()
        region_path = f"static/doble_region_{np.random.randint(1e6)}.png"
        plt.savefig(region_path)
        plt.close(fig)

        # 2. Superficie f(x, y) sobre la región
        Xg, Yg = [], []
        for xi in X:
            y1i, y2i = y_inf_func(xi), y_sup_func(xi)
            Yg.append(np.linspace(y1i, y2i, 60))
            Xg.append(np.full(60, xi))
        Xg = np.concatenate(Xg)
        Yg = np.concatenate(Yg)
        Zg = fxy(Xg, Yg)

        fig = plt.figure(figsize=(9, 7))
        ax = fig.add_subplot(111, projection='3d')
        # Superficie
        ax.plot_trisurf(Xg, Yg, Zg, alpha=0.5, color="purple", linewidth=0.2, antialiased=True)
        # Curvas límite en z=0
        ax.plot(X, Y1, np.zeros_like(X), color='brown', linewidth=2, label="y1(x) en z=0")
        ax.plot(X, Y2, np.zeros_like(X), color='green', linewidth=2, label="y2(x) en z=0")
        # Curvas límite sobre superficie
        ax.plot(X, Y1, fxy(X, Y1), color='brown', linestyle='--', linewidth=2, label="y1(x) sobre f(x,y)")
        ax.plot(X, Y2, fxy(X, Y2), color='green', linestyle='--', linewidth=2, label="y2(x) sobre f(x,y)")
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.set_zlabel("z")
        ax.legend()
        ax.set_title("Superficie f(x, y) y límites")
        plt.tight_layout()
        surf_path = f"static/doble_superficie_{np.random.randint(1e6)}.png"
        plt.savefig(surf_path)
        plt.close(fig)

        # Devuelve la ruta de la superficie, opcionalmente podrías devolver ambas
        return surf_path

    elif tipo == "triple":
        x, y, z = sp.symbols('x y z')
        x_inf = limites["a"]
        x_sup = limites["b"]
        y_inf_expr = limites["c"]
        y_sup_expr = limites["d"]
        z_inf_expr = limites["e"]
        z_sup_expr = limites["f"]

        y_inf_func = sp.lambdify(x, sp.sympify(y_inf_expr), modules=["numpy"])
        y_sup_func = sp.lambdify(x, sp.sympify(y_sup_expr), modules=["numpy"])
        z_inf_func = sp.lambdify([x, y], sp.sympify(z_inf_expr), modules=["numpy"])
        z_sup_func = sp.lambdify([x, y], sp.sympify(z_sup_expr), modules=["numpy"])

        X = np.linspace(x_inf, x_sup, 20)
        Y_low = y_inf_func(X)
        Y_high = y_sup_func(X)

        from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
        fig = plt.figure(figsize=(8, 7))
        ax = fig.add_subplot(111, projection='3d')

        # Superficies laterales (bordes)
        for i in range(len(X)):
            y0 = Y_low[i]
            y1 = Y_high[i]
            y_arr = np.linspace(y0, y1, 20)
            x_arr = np.full_like(y_arr, X[i])
            z_inf_arr = z_inf_func(X[i], y_arr)
            z_sup_arr = z_sup_func(X[i], y_arr)
            ax.plot(x_arr, y_arr, z_inf_arr, color='red', alpha=0.7, linewidth=1)
            ax.plot(x_arr, y_arr, z_sup_arr, color='blue', alpha=0.7, linewidth=1)
            ax.plot([X[i]]*2, [y0, y1], [z_inf_func(X[i], y0), z_inf_func(X[i], y1)], 'r--', alpha=0.5)
            ax.plot([X[i]]*2, [y0, y1], [z_sup_func(X[i], y0), z_sup_func(X[i], y1)], 'b--', alpha=0.5)

        # Caras en y = y_inf(x), y = y_sup(x)
        Y = np.linspace(np.min(Y_low), np.max(Y_high), 20)
        for j in range(len(Y)):
            x_arr = np.linspace(x_inf, x_sup, 20)
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
        img_path = f"static/triple_{np.random.randint(1e6)}.png"
        plt.savefig(img_path)
        plt.close(fig)
        return img_path

    else:
        return ""