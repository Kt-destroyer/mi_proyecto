import io
import os
import re
import numpy as np

# ---- MATPLOTLIB SERVER FIX ----
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
# ---- FIN FIX ----

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sympy import symbols, lambdify, sympify, integrate
import sympy

from app.calculo.integrales import calcular_integral
from app.calculo.graficas import generar_grafica  # Corrige si tu ruta es diferente

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if not os.path.exists("static"):
    os.makedirs("static")

def corregir_funciones(expr: str) -> str:
    funciones = ["sin", "cos", "tan", "log", "exp", "sqrt", "sec", "csc", "cot"]
    for f in funciones:
        expr = re.sub(rf"{f}\s+\(", f + "(", expr)
    return expr

# Diccionario global para sympify/lambdify con trigonométricas extendidas
sympy_func_dict = {
    "sin": sympy.sin, "cos": sympy.cos, "tan": sympy.tan,
    "log": sympy.log, "exp": sympy.exp, "sqrt": sympy.sqrt,
    "sec": sympy.sec, "csc": sympy.csc, "cot": sympy.cot
}

class SimpleIntegralRequest(BaseModel):
    expresion: str
    limite_inf: float
    limite_sup: float

class DobleIntegralRequest(BaseModel):
    expresion: str
    x_inf: float
    x_sup: float
    y_inf: str
    y_sup: str

class TripleIntegralRequest(BaseModel):
    expresion: str
    x_inf: float
    x_sup: float
    y_inf: str
    y_sup: str
    z_inf: str
    z_sup: str

@app.post("/simple")
def integral_simple(req: SimpleIntegralRequest):
    x = symbols("x")
    try:
        if req.limite_inf == req.limite_sup:
            return JSONResponse(status_code=400, content={"detail": "Los límites superior e inferior de integración son iguales."})
        if req.limite_inf > req.limite_sup:
            return JSONResponse(status_code=400, content={"detail": "El límite inferior es mayor que el superior. Por favor invierte los límites."})
        expr = sympify(
            corregir_funciones(req.expresion),
            locals=sympy_func_dict
        )
        result = float(integrate(expr, (x, req.limite_inf, req.limite_sup)).evalf())
    except Exception as e:
        print("Error en el cálculo:", e)
        return JSONResponse(status_code=400, content={"detail": f"Error en la expresión: {e}"})
    try:
        limites = {
            "a": req.limite_inf,
            "b": req.limite_sup
        }
        img_path = generar_grafica("simple", corregir_funciones(req.expresion), limites)
    except Exception as e:
        print("Error al graficar:", e)
        return JSONResponse(status_code=400, content={"detail": f"No se pudo graficar: {e}"})
    return {"resultado": result, "grafica": img_path}

@app.post("/doble")
def integral_doble(req: DobleIntegralRequest):
    x, y = symbols("x y")
    try:
        if req.x_inf == req.x_sup:
            return JSONResponse(status_code=400, content={"detail": "Los límites superior e inferior de integración para x son iguales."})
        if req.x_inf > req.x_sup:
            return JSONResponse(status_code=400, content={"detail": "El límite inferior de x es mayor que el superior. Por favor invierte los límites."})

        limites = {
            "a": req.x_inf,
            "b": req.x_sup,
            "c": corregir_funciones(req.y_inf),
            "d": corregir_funciones(req.y_sup)
        }
        resultado = calcular_integral("doble", corregir_funciones(req.expresion), limites)
        if "error" in resultado:
            print("Error en el cálculo doble:", resultado["error"])
            return JSONResponse(status_code=400, content={"detail": f"Error en la expresión: {resultado['error']}"})

        try:
            img_path = generar_grafica("doble", corregir_funciones(req.expresion), limites)
        except Exception as e:
            print("Error al graficar doble:", e)
            return JSONResponse(status_code=400, content={"detail": f"No se pudo graficar (región 2D): {e}"})

        return {"resultado": resultado["valor"], "grafica": img_path}
    except Exception as e:
        print("Error inesperado en el endpoint doble:", e)
        return JSONResponse(status_code=400, content={"detail": f"Error inesperado: {e}"})

@app.post("/triple")
def integral_triple(req: TripleIntegralRequest):
    x, y, z = symbols("x y z")
    try:
        if req.x_inf == req.x_sup:
            return JSONResponse(status_code=400, content={"detail": "Los límites superior e inferior de integración para x son iguales."})
        if req.x_inf > req.x_sup:
            return JSONResponse(status_code=400, content={"detail": "El límite inferior de x es mayor que el superior. Por favor invierte los límites."})

        limites = {
            "a": req.x_inf,
            "b": req.x_sup,
            "c": corregir_funciones(req.y_inf),
            "d": corregir_funciones(req.y_sup),
            "e": corregir_funciones(req.z_inf),
            "f": corregir_funciones(req.z_sup)
        }
        resultado = calcular_integral("triple", corregir_funciones(req.expresion), limites)
        if "error" in resultado:
            print("Error en el cálculo triple:", resultado["error"])
            return JSONResponse(status_code=400, content={"detail": f"Error en la expresión: {resultado['error']}"})

        try:
            img_path = generar_grafica("triple", corregir_funciones(req.expresion), limites)
        except Exception as e:
            print("Error al graficar triple:", e)
            return JSONResponse(status_code=400, content={"detail": f"No se pudo graficar (región 3D): {e}"})

        return {"resultado": resultado["valor"], "grafica": img_path}
    except Exception as e:
        print("Error inesperado en el endpoint triple:", e)
        return JSONResponse(status_code=400, content={"detail": f"Error inesperado: {e}"})

from fastapi.staticfiles import StaticFiles
app.mount("/static", StaticFiles(directory="static"), name="static")