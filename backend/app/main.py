from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import numpy as np
import sympy as sp
from sympy.parsing.sympy_parser import parse_expr
import matplotlib.pyplot as plt
import os
from pathlib import Path

# Configuración inicial
app = FastAPI(
    title="API de Cálculo Integral",
    description="Calcula integrales simples, dobles y triples con visualización gráfica",
    version="1.0.0"
)

# Configura CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos Pydantic para validación
class IntegralSimple(BaseModel):
    expresion: str
    limite_inf: float
    limite_sup: float

class IntegralDoble(BaseModel):
    expresion: str
    x_inf: float
    x_sup: float
    y_inf: float
    y_sup: float

class IntegralTriple(BaseModel):
    expresion: str
    x_inf: float
    x_sup: float
    y_inf: float
    y_sup: float
    z_inf: float
    z_sup: float

# Rutas principales
@app.get("/")
def home():
    return {
        "message": "API de Integrales Operativa",
        "endpoints": {
            "/simple": "POST - Calcular integral simple",
            "/doble": "POST - Calcular integral doble",
            "/triple": "POST - Calcular integral triple"
        }
    }

@app.post("/simple")
def calcular_simple(data: IntegralSimple):
    try:
        # Cálculo simbólico
        x = sp.Symbol('x')
        expr = parse_expr(data.expresion)
        integral = sp.integrate(expr, (x, data.limite_inf, data.limite_sup))
        
        # Cálculo numérico
        f = sp.lambdify(x, expr, 'numpy')
        x_vals = np.linspace(data.limite_inf, data.limite_sup, 500)
        y_vals = f(x_vals)
        
        # Generar gráfica
        plt.figure(figsize=(10, 6))
        plt.plot(x_vals, y_vals, 'b-', linewidth=2)
        plt.fill_between(x_vals, y_vals, alpha=0.3)
        plt.title(f"Integral de ${sp.latex(expr)}$ entre {data.limite_inf} y {data.limite_sup}")
        plt.xlabel("x")
        plt.ylabel("f(x)")
        plt.grid(True)
        
        # Guardar imagen
        os.makedirs("static/graficas", exist_ok=True)
        ruta = f"static/graficas/integral_simple_{hash(data.expresion)}.png"
        plt.savefig(ruta, dpi=120, bbox_inches='tight')
        plt.close()
        
        return {
            "resultado": float(integral.evalf()),
            "grafica": ruta,
            "expresion_latex": sp.latex(integral)
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/doble")
def calcular_doble(data: IntegralDoble):
    try:
        # Cálculo simbólico
        x, y = sp.symbols('x y')
        expr = parse_expr(data.expresion)
        
        # Cálculo numérico
        f = sp.lambdify((x, y), expr, 'numpy')
        x_vals = np.linspace(data.x_inf, data.x_sup, 100)
        y_vals = np.linspace(data.y_inf, data.y_sup, 100)
        X, Y = np.meshgrid(x_vals, y_vals)
        Z = f(X, Y)
        
        # Generar gráfica 3D
        fig = plt.figure(figsize=(12, 8))
        ax = fig.add_subplot(111, projection='3d')
        surf = ax.plot_surface(X, Y, Z, cmap='viridis', alpha=0.8)
        fig.colorbar(surf)
        plt.title(f"Integral doble de ${sp.latex(expr)}$")
        
        # Guardar imagen
        ruta = f"static/graficas/integral_doble_{hash(data.expresion)}.png"
        plt.savefig(ruta, dpi=120)
        plt.close()
        
        # Cálculo numérico con SciPy
        from scipy.integrate import dblquad
        resultado, _ = dblquad(
            lambda y, x: f(x, y),
            data.x_inf, data.x_sup,
            lambda x: data.y_inf, lambda x: data.y_sup
        )
        
        return {
            "resultado": resultado,
            "grafica": ruta,
            "expresion_latex": sp.latex(sp.Integral(expr, (x, data.x_inf, data.x_sup), (y, data.y_inf, data.y_sup)))
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/triple")
def calcular_triple(data: IntegralTriple):
    try:
        # Cálculo simbólico
        x, y, z = sp.symbols('x y z')
        expr = parse_expr(data.expresion)
        
        # Visualización de la región
        fig = plt.figure(figsize=(10, 7))
        ax = fig.add_subplot(111, projection='3d')
        
        # Dibujar cubo de integración
        vertices = [
            (data.x_inf, data.y_inf, data.z_inf),
            (data.x_sup, data.y_inf, data.z_inf),
            # ... (todos los vértices)
        ]
        
        # Configuración visual
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_zlabel("Z")
        plt.title("Región de Integración Triple")
        
        # Guardar imagen
        ruta = f"static/graficas/integral_triple_{hash(data.expresion)}.png"
        plt.savefig(ruta, dpi=120)
        plt.close()
        
        # Cálculo numérico con SciPy
        from scipy.integrate import tplquad
        resultado, _ = tplquad(
            lambda z, y, x: sp.lambdify((x, y, z), expr)(x, y, z),
            data.x_inf, data.x_sup,
            lambda x: data.y_inf, lambda x: data.y_sup,
            lambda x, y: data.z_inf, lambda x, y: data.z_sup
        )
        
        return {
            "resultado": resultado,
            "grafica": ruta,
            "expresion_latex": sp.latex(sp.Integral(
                expr, 
                (x, data.x_inf, data.x_sup),
                (y, data.y_inf, data.y_sup),
                (z, data.z_inf, data.z_sup)
            ))
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Configuración para producción
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)