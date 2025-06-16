import sympy as sp
import numpy as np
from scipy.integrate import quad, dblquad, tplquad
from .graficas import generar_grafica

def calcular_integral(tipo: str, expresion: str, limites: dict):
    """
    Calcula integrales simples, dobles o triples.
    Retorna: {"valor": float, "grafica": "ruta/imagen.png"}
    """
    x, y, z = sp.symbols('x y z')
    resultado = None

    try:
        if tipo == "simple":
            # Integral definida simple
            expr = sp.sympify(expresion)
            f = sp.lambdify(x, expr, modules=['numpy'])
            resultado, _ = quad(f, limites["a"], limites["b"])

        elif tipo == "doble":
            # Integral doble
            expr = sp.sympify(expresion)
            f = sp.lambdify((x, y), expr, modules=['numpy'])
            resultado, _ = dblquad(
                f, limites["a"], limites["b"],
                lambda x: limites["c"], lambda x: limites["d"]
            )

        elif tipo == "triple":
            # Integral triple
            expr = sp.sympify(expresion)
            f = sp.lambdify((x, y, z), expr, modules=['numpy'])
            resultado, _ = tplquad(
                f, limites["a"], limites["b"],
                lambda x: limites["c"], lambda x: limites["d"],
                lambda x, y: limites["e"], lambda x, y: limites["f"]
            )

        # Generar gráfica (opcional)
        ruta_grafica = generar_grafica(tipo, expresion, limites)

        return {
            "valor": float(resultado),
            "grafica": ruta_grafica
        }

    except Exception as e:
        return {"error": str(e)}