import os
import math
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.calculo.integrales import calcular_integral, parse_limit_string
from app.calculo.graficas import generar_grafica
from app.utils.math_parser import validar_expr_con_variables, parse_math_expr, preprocess_math_expr

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
    limite_inf: str
    limite_sup: str

class DobleIntegralRequest(BaseModel):
    expresion: str
    x_inf: str
    x_sup: str
    y_inf: str
    y_sup: str

class TripleIntegralRequest(BaseModel):
    expresion: str
    x_inf: str
    x_sup: str
    y_inf: str
    y_sup: str
    z_inf: str
    z_sup: str

def parse_limite(valor):
    # Intenta convertir a float, si no se puede, es una expresión de variable
    try:
        return float(valor)
    except Exception:
        # Preprocesa cualquier string de función antes de parsear
        return str(parse_math_expr(valor))

@app.post("/simple")
def integral_simple(req: SimpleIntegralRequest):
    try:
        a = parse_limit_string(req.limite_inf)
        b = parse_limit_string(req.limite_sup)
        if a == b:
            return JSONResponse(status_code=400, content={"detail": "Los límites superior e inferior de integración son iguales."})
        if a > b:
            return JSONResponse(status_code=400, content={"detail": "El límite inferior es mayor que el superior. Por favor invierte los límites."})

        try:
            # Preprocesamiento explícito aquí también
            expr = validar_expr_con_variables(preprocess_math_expr(req.expresion), {"x"})
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
            limites_grafica = {
                "a": float(a),
                "b": float(b)
            }
            grafica = generar_grafica("simple", str(expr), limites_grafica)
        except Exception as e:
            print("Error al graficar:", e)
            grafica = ""
        if isinstance(grafica, str) and (grafica.endswith(".png") or grafica.startswith("http")):
            grafica_out = grafica
        else:
            grafica_out = None
        return {"valor": valor, "grafica": grafica_out}
    except Exception as e:
        print("Error en el endpoint simple:", e)
        return JSONResponse(status_code=400, content={"detail": f"Error inesperado: {e}"})

@app.post("/doble")
def integral_doble(req: DobleIntegralRequest):
    try:
        a = parse_limit_string(req.x_inf)
        b = parse_limit_string(req.x_sup)
        if a == b:
            return JSONResponse(status_code=400, content={"detail": "Los límites superior e inferior de integración para x son iguales."})
        if a > b:
            return JSONResponse(status_code=400, content={"detail": "El límite inferior de x es mayor que el superior. Por favor invierte los límites."})

        try:
            expr = validar_expr_con_variables(preprocess_math_expr(req.expresion), {"x", "y"})
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
            limites_grafica = {
                "a": float(a),
                "b": float(b),
                "c": y_inf_expr,
                "d": y_sup_expr
            }
            grafica = generar_grafica("doble", str(expr), limites_grafica)
        except Exception as e:
            print("Error al graficar doble:", e)
            grafica = ""
        if isinstance(grafica, str) and (grafica.endswith(".png") or grafica.startswith("http")):
            grafica_out = grafica
        else:
            grafica_out = None
        return {"valor": valor, "grafica": grafica_out}
    except Exception as e:
        print("Error inesperado en el endpoint doble:", e)
        return JSONResponse(status_code=400, content={"detail": f"Error inesperado: {e}"})

@app.post("/triple")
def integral_triple(req: TripleIntegralRequest):
    try:
        a = parse_limit_string(req.x_inf)
        b = parse_limit_string(req.x_sup)
        if a == b:
            return JSONResponse(status_code=400, content={"detail": "Los límites superior e inferior de integración para x son iguales."})
        if a > b:
            return JSONResponse(status_code=400, content={"detail": "El límite inferior de x es mayor que el superior. Por favor invierte los límites."})

        try:
            expr = validar_expr_con_variables(preprocess_math_expr(req.expresion), {"x", "y", "z"})
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
        try:
            limites_grafica = {
                "a": float(a),
                "b": float(b),
                "c": y_inf_expr,
                "d": y_sup_expr,
                "e": z_inf_expr,
                "f": z_sup_expr
            }
            grafica = generar_grafica("triple", str(expr), limites_grafica)
        except Exception as e:
            print("Error al graficar triple:", e)
            grafica = ""
        if isinstance(grafica, str) and (grafica.endswith(".png") or grafica.startswith("http")):
            grafica_out = grafica
        else:
            grafica_out = None
        return {"valor": valor, "grafica": grafica_out}
    except Exception as e:
        print("Error inesperado en el endpoint triple:", e)
        return JSONResponse(status_code=400, content={"detail": f"Error inesperado: {e}"})

from fastapi.staticfiles import StaticFiles
app.mount("/static", StaticFiles(directory="static"), name="static")