import matplotlib.pyplot as plt
import numpy as np
import sympy as sp
import os
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D

def generar_grafica(tipo: str, expresion: str, limites: dict):
    """
    Genera gráficas para integrales y las guarda en ./static/graficas/
    
    Args:
        tipo: "simple", "doble" o "triple"
        expresion: Expresión matemática como string (ej: "x**2 + y")
        limites: Diccionario con límites de integración
        
    Returns:
        str: Ruta relativa del archivo de imagen generado
    """
    try:
        # Configuración inicial
        os.makedirs("static/graficas", exist_ok=True)
        ruta = f"static/graficas/integral_{tipo}_{hash(expresion)}.png"
        x, y, z = sp.symbols('x y z')
        
        plt.close('all')  # Cerrar figuras previas

        if tipo == "simple":
            # Gráfica 2D para integral simple
            expr = sp.sympify(expresion)
            f = sp.lambdify(x, expr, modules=['numpy'])
            
            x_vals = np.linspace(limites["a"], limites["b"], 500)
            y_vals = f(x_vals)
            
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.plot(x_vals, y_vals, 'b-', linewidth=2)
            ax.fill_between(x_vals, y_vals, alpha=0.3)
            ax.set_title(f"Integral de ${sp.latex(expr)}$ entre {limites['a']} y {limites['b']}")
            ax.set_xlabel("x")
            ax.set_ylabel("f(x)")
            ax.grid(True)

        elif tipo == "doble":
            # Gráfica 3D para integral doble
            expr = sp.sympify(expresion)
            f = sp.lambdify((x, y), expr, modules=['numpy'])
            
            x_vals = np.linspace(limites["a"], limites["b"], 100)
            y_vals = np.linspace(limites["c"], limites["d"], 100)
            X, Y = np.meshgrid(x_vals, y_vals)
            Z = f(X, Y)
            
            fig = plt.figure(figsize=(12, 8))
            ax = fig.add_subplot(111, projection='3d')
            surf = ax.plot_surface(X, Y, Z, cmap=cm.viridis, alpha=0.8)
            fig.colorbar(surf)
            ax.set_title(f"Integral doble de ${sp.latex(expr)}$")
            ax.set_xlabel("x")
            ax.set_ylabel("y")
            ax.set_zlabel("f(x,y)")

        elif tipo == "triple":
            # Visualización de región para integral triple
            expr = sp.sympify(expresion)
            
            fig = plt.figure(figsize=(10, 7))
            ax = fig.add_subplot(111, projection='3d')
            
            # Crear cubo para representar los límites
            x = [limites["a"], limites["b"]]
            y = [limites["c"], limites["d"]]
            z = [limites["e"], limites["f"]]
            
            # Dibujar los límites del volumen
            for xi in x:
                for yi in y:
                    ax.plot([xi, xi], [yi, yi], z, 'b-')
            for xi in x:
                for zi in z:
                    ax.plot([xi, xi], y, [zi, zi], 'b-')
            for yi in y:
                for zi in z:
                    ax.plot(x, [yi, yi], [zi, zi], 'b-')
            
            ax.set_title(f"Región de integración para ${sp.latex(expr)}$")
            ax.set_xlabel("x")
            ax.set_ylabel("y")
            ax.set_zlabel("z")

        else:
            raise ValueError(f"Tipo de integral no soportada: {tipo}")

        plt.tight_layout()
        plt.savefig(ruta, dpi=150, bbox_inches='tight')
        plt.close()
        
        return ruta

    except Exception as e:
        print(f"Error al generar gráfica: {str(e)}")
        return None