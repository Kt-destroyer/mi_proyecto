import io
import os
import re
import numpy as np
import matplotlib.pyplot as plt
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sympy import symbols, lambdify, sympify, integrate
import sympy

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
        expr = sympify(corregir_funciones(req.expresion), locals={"sin": sympy.sin, "cos": sympy.cos, "exp": sympy.exp, "log": sympy.log})
        result = float(integrate(expr, (x, req.limite_inf, req.limite_sup)).evalf())
    except Exception as e:
        return JSONResponse(status_code=400, content={"detail": f"Error en la expresión: {e}"})
    try:
        f = lambdify(x, expr, modules=["numpy"])
        x_vals = np.linspace(req.limite_inf, req.limite_sup, 400)
        y_vals = f(x_vals)
        fig, ax = plt.subplots(figsize=(7,5))
        ax.plot(x_vals, y_vals, "b", label=f"f(x)={req.expresion}")
        ax.fill_between(x_vals, y_vals, color="skyblue", alpha=0.5)
        ax.set_xlabel("x", fontsize=14)
        ax.set_ylabel("f(x)", fontsize=14)
        ax.set_title(f"Integral de {req.expresion}\n", fontsize=16)
        ax.axhline(0, color='black', linewidth=1.5)
        ax.axvline(0, color='black', linewidth=1.5)
        plt.tight_layout()
        img_bytes = io.BytesIO()
        plt.savefig(img_bytes, format="png")
        plt.close(fig)
        img_bytes.seek(0)
        img_path = f"static/simple_{np.random.randint(1e6)}.png"
        with open(img_path, "wb") as fimg:
            fimg.write(img_bytes.read())
    except Exception as e:
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

        expr = sympify(corregir_funciones(req.expresion), locals={"sin": sympy.sin, "cos": sympy.cos, "exp": sympy.exp, "log": sympy.log})
        y_inf_expr = sympify(corregir_funciones(req.y_inf), locals={"x": x, "sin": sympy.sin, "cos": sympy.cos, "exp": sympy.exp, "log": sympy.log})
        y_sup_expr = sympify(corregir_funciones(req.y_sup), locals={"x": x, "sin": sympy.sin, "cos": sympy.cos, "exp": sympy.exp, "log": sympy.log})

        # Validación de los límites funcionales
        for xi in [req.x_inf, req.x_sup]:
            try:
                yi0 = float(y_inf_expr.subs(x, xi))
                yi1 = float(y_sup_expr.subs(x, xi))
            except Exception:
                return JSONResponse(status_code=400, content={"detail": "No se pueden evaluar los límites funcionales de y. ¿Ingresaste bien x en los límites?"})
            if yi0 > yi1:
                return JSONResponse(status_code=400, content={"detail": "El límite inferior de y es mayor que el superior para algún x."})

        result = float(integrate(expr, (x, req.x_inf, req.x_sup), (y, y_inf_expr, y_sup_expr)).evalf())
    except Exception as e:
        return JSONResponse(status_code=400, content={"detail": f"Error en la expresión: {e}"})

    # --------- GRAFICADO MEJORADO PARA FUNCIÓN DE LÍMITES ---------
    try:
        fig, ax = plt.subplots(figsize=(7,5))
        ax.set_aspect('equal')
        ax.axhline(0, color='black', linewidth=2)
        ax.axvline(0, color='black', linewidth=2)
        ax.arrow(req.x_sup, 0, 0.2, 0, head_width=0.25, head_length=0.2, fc='k', ec='k')
        ax.arrow(0, req.x_sup+1, 0, 0.2, head_width=0.25, head_length=0.2, fc='k', ec='k')
        ax.text(req.x_sup+0.4, -0.2, 'x', fontsize=16)
        ax.text(-0.2, req.x_sup+1.2, 'y', fontsize=16)

        # ----------- GRAFICAR REGIÓN FUNCIONAL -------------
        X = np.linspace(req.x_inf, req.x_sup, 200)
        Y_inf = lambdify(x, y_inf_expr, modules=["numpy"])
        Y_sup = lambdify(x, y_sup_expr, modules=["numpy"])
        Y1 = Y_inf(X)
        Y2 = Y_sup(X)
        # Curvas límite
        ax.plot(X, Y1, 'r--', linewidth=2, label='y inferior')
        ax.plot(X, Y2, 'r--', linewidth=2, label='y superior')
        # Líneas verticales en los extremos para cerrar la región
        ax.plot([X[0], X[0]], [Y1[0], Y2[0]], 'r--', linewidth=2)
        ax.plot([X[-1], X[-1]], [Y1[-1], Y2[-1]], 'r--', linewidth=2)
        # Rellenar la región funcional
        ax.fill_between(X, Y1, Y2, color='red', alpha=0.09)
        ax.set_title("2D Coordinate System\n(límites de integración en rojo)", fontsize=15)
        ax.set_xlim(min(0, req.x_inf)-1, req.x_sup+2)
        y_min = min(np.min(Y1), np.min(Y2), 0) - 1
        y_max = max(np.max(Y1), np.max(Y2), 0) + 2
        ax.set_ylim(y_min, y_max)
        plt.tight_layout()
        img_bytes = io.BytesIO()
        plt.savefig(img_bytes, format="png")
        plt.close(fig)
        img_bytes.seek(0)
        img_path = f"static/doble_{np.random.randint(1e6)}.png"
        with open(img_path, "wb") as fimg:
            fimg.write(img_bytes.read())
    except Exception as e:
        return JSONResponse(status_code=400, content={"detail": f"No se pudo graficar (región 2D): {e}"})
    return {"resultado": result, "grafica": img_path}

@app.post("/triple")
def integral_triple(req: TripleIntegralRequest):
    x, y, z = symbols("x y z")
    try:
        if req.x_inf == req.x_sup:
            return JSONResponse(status_code=400, content={"detail": "Los límites superior e inferior de integración para x son iguales."})
        if req.x_inf > req.x_sup:
            return JSONResponse(status_code=400, content={"detail": "El límite inferior de x es mayor que el superior. Por favor invierte los límites."})
        expr = sympify(corregir_funciones(req.expresion), locals={"sin": sympy.sin, "cos": sympy.cos, "exp": sympy.exp, "log": sympy.log})
        y_inf_expr = sympify(corregir_funciones(req.y_inf), locals={"x": x, "sin": sympy.sin, "cos": sympy.cos, "exp": sympy.exp, "log": sympy.log})
        y_sup_expr = sympify(corregir_funciones(req.y_sup), locals={"x": x, "sin": sympy.sin, "cos": sympy.cos, "exp": sympy.exp, "log": sympy.log})
        z_inf_expr = sympify(corregir_funciones(req.z_inf), locals={"x": x, "y": y, "sin": sympy.sin, "cos": sympy.cos, "exp": sympy.exp, "log": sympy.log})
        z_sup_expr = sympify(corregir_funciones(req.z_sup), locals={"x": x, "y": y, "sin": sympy.sin, "cos": sympy.cos, "exp": sympy.exp, "log": sympy.log})

        for xi in [req.x_inf, req.x_sup]:
            try:
                yi0 = float(y_inf_expr.subs(x, xi))
                yi1 = float(y_sup_expr.subs(x, xi))
                if yi0 > yi1:
                    return JSONResponse(status_code=400, content={"detail": "El límite inferior de y es mayor que el superior para algún valor de x. Verifica tus funciones."})
            except Exception:
                return JSONResponse(status_code=400, content={"detail": "Uno de los límites funcionales de y no se puede evaluar numéricamente. Revisa las funciones."})
            for yi in [yi0, yi1]:
                try:
                    zi0 = float(z_inf_expr.subs({x: xi, y: yi}))
                    zi1 = float(z_sup_expr.subs({x: xi, y: yi}))
                    if zi0 > zi1:
                        return JSONResponse(status_code=400, content={"detail": "El límite inferior de z es mayor que el superior para algún valor de (x, y). Verifica tus funciones."})
                except Exception:
                    return JSONResponse(status_code=400, content={"detail": "Uno de los límites funcionales de z no se puede evaluar numéricamente. Revisa las funciones."})

        result = float(
            integrate(
                expr,
                (x, req.x_inf, req.x_sup),
                (y, y_inf_expr, y_sup_expr),
                (z, z_inf_expr, z_sup_expr),
            ).evalf()
        )
    except Exception as e:
        return JSONResponse(status_code=400, content={"detail": f"Error en la expresión: {e}"})

    try:
        fig = plt.figure(figsize=(7, 6))
        ax = fig.add_subplot(111, projection='3d')
        ax.plot([0, 2], [0, 0], [0, 0], color="black", linewidth=2)  # x
        ax.plot([0, 0], [0, 2], [0, 0], color="black", linewidth=2)  # y
        ax.plot([0, 0], [0, 0], [0, 2], color="black", linewidth=2)  # z
        ax.quiver(2, 0, 0, 0.4, 0, 0, color="black", arrow_length_ratio=0.2)
        ax.quiver(0, 2, 0, 0, 0.4, 0, color="black", arrow_length_ratio=0.2)
        ax.quiver(0, 0, 2, 0, 0, 0.4, color="black", arrow_length_ratio=0.2)
        ax.text(2.5, 0, 0, "x", fontsize=16)
        ax.text(0, 2.5, 0, "y", fontsize=16)
        ax.text(0, 0, 2.5, "z", fontsize=16)
        try:
            X0, X1 = req.x_inf, req.x_sup
            Y_inf = lambdify(x, y_inf_expr, modules=["numpy"])
            Y_sup = lambdify(x, y_sup_expr, modules=["numpy"])
            Z_inf = lambdify([x, y], z_inf_expr, modules=["numpy"])
            Z_sup = lambdify([x, y], z_sup_expr, modules=["numpy"])
            corners = []
            for xi in [X0, X1]:
                for yi in [float(Y_inf(xi)), float(Y_sup(xi))]:
                    for zi in [float(Z_inf(xi, yi)), float(Z_sup(xi, yi))]:
                        corners.append((xi, yi, zi))
            import itertools
            for a, b in itertools.combinations(corners, 2):
                dist = np.sum(np.abs(np.array(a)-np.array(b)))
                if np.isclose(dist, abs(X1-X0)) or np.isclose(dist, abs(float(Y_sup(X1))-float(Y_inf(X0)))) or np.isclose(dist, abs(float(Z_sup(X1, float(Y_sup(X1))))-float(Z_inf(X0, float(Y_inf(X0)))))):
                    ax.plot([a[0], b[0]], [a[1], b[1]], [a[2], b[2]], "r--", linewidth=2)
        except Exception:
            pass
        ax.set_title("3D Coordinate System\n(límites de integración en rojo)", fontsize=15)
        ax.set_xlim([min(0, req.x_inf)-1, req.x_sup+2])
        try:
            y_min = min(float(y_inf_expr.subs(x, req.x_inf)), float(y_inf_expr.subs(x, req.x_sup)), 0) - 1
            y_max = max(float(y_sup_expr.subs(x, req.x_inf)), float(y_sup_expr.subs(x, req.x_sup)), 0) + 2
        except Exception:
            y_min, y_max = -1, 4
        ax.set_ylim([y_min, y_max])
        try:
            z_min = min(
                float(z_inf_expr.subs({x: req.x_inf, y: float(y_inf_expr.subs(x, req.x_inf))})),
                float(z_inf_expr.subs({x: req.x_sup, y: float(y_inf_expr.subs(x, req.x_sup))})),
                0
            ) - 1
            z_max = max(
                float(z_sup_expr.subs({x: req.x_inf, y: float(y_sup_expr.subs(x, req.x_inf))})),
                float(z_sup_expr.subs({x: req.x_sup, y: float(y_sup_expr.subs(x, req.x_sup))})),
                0
            ) + 2
        except Exception:
            z_min, z_max = -1, 4
        ax.set_zlim([z_min, z_max])
        plt.tight_layout()
        img_bytes = io.BytesIO()
        plt.savefig(img_bytes, format="png")
        plt.close(fig)
        img_bytes.seek(0)
        img_path = f"static/triple_{np.random.randint(1e6)}.png"
        with open(img_path, "wb") as fimg:
            fimg.write(img_bytes.read())
    except Exception as e:
        return JSONResponse(status_code=400, content={"detail": f"No se pudo graficar (región 3D): {e}"})
    return {"resultado": result, "grafica": img_path}

from fastapi.staticfiles import StaticFiles
app.mount("/static", StaticFiles(directory="static"), name="static")