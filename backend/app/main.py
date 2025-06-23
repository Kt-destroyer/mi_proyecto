import os
import math
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.calculo.integrales import calcular_integral
from app.calculo.graficas import generar_grafica
from app.utils.math_parser import validar_expr_con_variables, parse_math_expr

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

class SimpleIntegralRequest(BaseModel):
    expresion: str
    limite_inf: float
    limite_sup: float
    modo_interactivo: bool = True

class DobleIntegralRequest(BaseModel):
    expresion: str
    x_inf: float
    x_sup: float
    y_inf: str
    y_sup: str
    modo_interactivo: bool = True

class TripleIntegralRequest(BaseModel):
    expresion: str
    x_inf: float
    x_sup: float
    y_inf: str
    y_sup: str
    z_inf: str
    z_sup: str
    modo_interactivo: bool = True

def parse_limite(valor):
    # Intenta convertir a float, si no se puede, es una expresión de variable
    try:
        return float(valor)
    except Exception:
        return str(parse_math_expr(valor))

@app.post("/simple")
def integral_simple(req: SimpleIntegralRequest):
    try:
        if req.limite_inf == req.limite_sup:
            return JSONResponse(status_code=400, content={"detail": "Los límites superior e inferior de integración son iguales."})
        if req.limite_inf > req.limite_sup:
            return JSONResponse(status_code=400, content={"detail": "El límite inferior es mayor que el superior. Por favor invierte los límites."})

        try:
            expr = validar_expr_con_variables(req.expresion, {"x"})
        except Exception as e:
            return JSONResponse(status_code=400, content={"detail": f"Error en la expresión ingresada. Revisa paréntesis y sintaxis. Detalle: {e}"})

        limites = {
            "a": req.limite_inf,
            "b": req.limite_sup
        }
        resultado = calcular_integral("simple", str(expr), limites)
        if "error" in resultado:
            print("Error en el cálculo simple:", resultado["error"])
            return JSONResponse(status_code=400, content={"detail": f"Error en la expresión: {resultado['error']}"})
        valor = resultado.get("valor", None)
        if valor is not None and not math.isfinite(valor):
            return JSONResponse(status_code=400, content={
                "detail": "El resultado de la integral es infinito o indefinido. Cambia los límites o la función."
            })
        try:
            grafica = generar_grafica("simple", str(expr), limites, modo_interactivo=req.modo_interactivo)
        except Exception as e:
            print("Error al graficar:", e)
            grafica = ""
        return {"valor": valor, "grafica": grafica}
    except Exception as e:
        print("Error en el endpoint simple:", e)
        return JSONResponse(status_code=400, content={"detail": f"Error inesperado: {e}"})

@app.post("/doble")
def integral_doble(req: DobleIntegralRequest):
    try:
        if req.x_inf == req.x_sup:
            return JSONResponse(status_code=400, content={"detail": "Los límites superior e inferior de integración para x son iguales."})
        if req.x_inf > req.x_sup:
            return JSONResponse(status_code=400, content={"detail": "El límite inferior de x es mayor que el superior. Por favor invierte los límites."})

        try:
            expr = validar_expr_con_variables(req.expresion, {"x", "y"})
            y_inf_expr = parse_limite(req.y_inf)
            y_sup_expr = parse_limite(req.y_sup)
        except Exception as e:
            return JSONResponse(status_code=400, content={"detail": f"Error en la expresión ingresada o en los límites de y. Revisa paréntesis y sintaxis. Detalle: {e}"})

        limites = {
            "a": req.x_inf,
            "b": req.x_sup,
            "c": y_inf_expr,
            "d": y_sup_expr
        }
        resultado = calcular_integral("doble", str(expr), limites)
        if "error" in resultado:
            print("Error en el cálculo doble:", resultado["error"])
            return JSONResponse(status_code=400, content={"detail": f"Error en la expresión: {resultado['error']}"})
        valor = resultado.get("valor", None)
        if valor is not None and not math.isfinite(valor):
            return JSONResponse(status_code=400, content={
                "detail": "El resultado de la integral es infinito o indefinido. Cambia los límites o la función."
            })
        try:
            grafica = generar_grafica("doble", str(expr), limites, modo_interactivo=req.modo_interactivo)
        except Exception as e:
            print("Error al graficar doble:", e)
            grafica = ""
        return {"valor": valor, "grafica": grafica}
    except Exception as e:
        print("Error inesperado en el endpoint doble:", e)
        return JSONResponse(status_code=400, content={"detail": f"Error inesperado: {e}"})

@app.post("/triple")
def integral_triple(req: TripleIntegralRequest):
    try:
        if req.x_inf == req.x_sup:
            return JSONResponse(status_code=400, content={"detail": "Los límites superior e inferior de integración para x son iguales."})
        if req.x_inf > req.x_sup:
            return JSONResponse(status_code=400, content={"detail": "El límite inferior de x es mayor que el superior. Por favor invierte los límites."})

        try:
            expr = validar_expr_con_variables(req.expresion, {"x", "y", "z"})
            y_inf_expr = parse_limite(req.y_inf)
            y_sup_expr = parse_limite(req.y_sup)
            z_inf_expr = parse_limite(req.z_inf)
            z_sup_expr = parse_limite(req.z_sup)
        except Exception as e:
            return JSONResponse(status_code=400, content={"detail": f"Error en la expresión ingresada o en los límites de y/z. Revisa paréntesis y sintaxis. Detalle: {e}"})

        limites = {
            "a": req.x_inf,
            "b": req.x_sup,
            "c": y_inf_expr,
            "d": y_sup_expr,
            "e": z_inf_expr,
            "f": z_sup_expr
        }
        resultado = calcular_integral("triple", str(expr), limites)
        if "error" in resultado:
            print("Error en el cálculo triple:", resultado["error"])
            return JSONResponse(status_code=400, content={"detail": f"Error en la expresión: {resultado['error']}"})
        valor = resultado.get("valor", None)
        if valor is not None and not math.isfinite(valor):
            return JSONResponse(status_code=400, content={
                "detail": "El resultado de la integral es infinito o indefinido. Cambia los límites o la función."
            })
        grafica = ""
        try:
            # Intenta generar la gráfica, pero si falla, sigue mostrando el resultado
            grafica = generar_grafica("triple", str(expr), limites, modo_interactivo=req.modo_interactivo)
        except Exception as e:
            print("Error al graficar triple:", e)
            grafica = ""
        return {"valor": valor, "grafica": grafica}
    except Exception as e:
        print("Error inesperado en el endpoint triple:", e)
        return JSONResponse(status_code=400, content={"detail": f"Error inesperado: {e}"})

from fastapi.staticfiles import StaticFiles
app.mount("/static", StaticFiles(directory="static"), name="static")