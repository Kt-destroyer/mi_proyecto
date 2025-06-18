from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Union
import sympy as sp

from app.calculo.integrales import calcular_integral

app = FastAPI(
    title="API de Cálculo Integral (Método de Simpson, límites variables)",
    description="Calcula integrales simples, dobles y triples con visualización gráfica usando el método de Simpson y límites variables",
    version="2.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class IntegralSimple(BaseModel):
    expresion: str
    limite_inf: float
    limite_sup: float

class IntegralDoble(BaseModel):
    expresion: str
    x_inf: float
    x_sup: float
    y_inf: Union[float, str]
    y_sup: Union[float, str]

class IntegralTriple(BaseModel):
    expresion: str
    x_inf: float
    x_sup: float
    y_inf: float
    y_sup: float
    z_inf: float
    z_sup: float

@app.get("/")
def home():
    return {
        "message": "API de Integrales Operativa (Simpson, límites variables)",
        "endpoints": {
            "/simple": "POST - Calcular integral simple",
            "/doble": "POST - Calcular integral doble (límites de y pueden ser función de x)",
            "/triple": "POST - Calcular integral triple"
        }
    }

@app.post("/simple")
def calcular_simple(data: IntegralSimple):
    try:
        limites = {
            "a": data.limite_inf,
            "b": data.limite_sup
        }
        resultado = calcular_integral("simple", data.expresion, limites)
        if "error" in resultado:
            raise HTTPException(status_code=400, detail=resultado["error"])
        return {
            "resultado": resultado["valor"],
            "grafica": resultado["grafica"],
            "expresion_latex": sp.latex(sp.sympify(data.expresion))
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/doble")
def calcular_doble(data: IntegralDoble):
    try:
        limites = {
            "a": data.x_inf,
            "b": data.x_sup,
            "c": data.y_inf,
            "d": data.y_sup
        }
        resultado = calcular_integral("doble", data.expresion, limites)
        if "error" in resultado:
            raise HTTPException(status_code=400, detail=resultado["error"])

        # Para LaTeX, convierte límites string a expresiones si es necesario
        y_inf_latex = data.y_inf if isinstance(data.y_inf, float) \
            else sp.latex(sp.sympify(data.y_inf))
        y_sup_latex = data.y_sup if isinstance(data.y_sup, float) \
            else sp.latex(sp.sympify(data.y_sup))

        return {
            "resultado": resultado["valor"],
            "grafica": resultado["grafica"],
            "expresion_latex": sp.latex(
                sp.Integral(
                    sp.sympify(data.expresion),
                    (sp.Symbol('x'), data.x_inf, data.x_sup),
                    (sp.Symbol('y'), y_inf_latex, y_sup_latex)
                )
            )
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/triple")
def calcular_triple(data: IntegralTriple):
    try:
        limites = {
            "a": data.x_inf,
            "b": data.x_sup,
            "c": data.y_inf,
            "d": data.y_sup,
            "e": data.z_inf,
            "f": data.z_sup
        }
        resultado = calcular_integral("triple", data.expresion, limites)
        if "error" in resultado:
            raise HTTPException(status_code=400, detail=resultado["error"])
        return {
            "resultado": resultado["valor"],
            "grafica": resultado["grafica"],
            "expresion_latex": sp.latex(
                sp.Integral(
                    sp.sympify(data.expresion),
                    (sp.Symbol('x'), data.x_inf, data.x_sup),
                    (sp.Symbol('y'), data.y_inf, data.y_sup),
                    (sp.Symbol('z'), data.z_inf, data.z_sup)
                )
            )
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Servir archivos estáticos para ver las gráficas en el frontend
from fastapi.staticfiles import StaticFiles
app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)