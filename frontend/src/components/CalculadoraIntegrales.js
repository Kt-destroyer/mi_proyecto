import React, { useState } from "react";
import axios from "axios";
import Plot from "react-plotly.js";
import { backendUrl } from "../config";

// --- AUXILIAR: Preprocesador de expresiones matemáticas ---
function preprocesarExpresion(expr) {
  let r = expr;
 
  r = r.replace(/(\d)([a-zA-Z])/g, '$1*$2');
  r = r.replace(/([a-zA-Z])(\d)/g, '$1*$2');
  // sin x -> sin(x)
  r = r.replace(/(sin|cos|tan|exp|log|sqrt|sec|csc|cot)\s*\(\s*([^)]+)\s*\)/g, '$1($2)'); 
  r = r.replace(/(sin|cos|tan|exp|log|sqrt|sec|csc|cot)\s+([a-zA-Z0-9]+)/g, '$1($2)');
  // ^ to **
  r = r.replace(/(\w+)\s*\^\s*(\w+)/g, '$1**$2');
  return r;
}

// --- Tabla de ejemplos y manual de uso ---
const ejemplos = [
  {
    tipo: "Simple",
    expresion: "x**2 + 3",
    limites_x: "[0, 2]",
    limites_y: "-",
    limites_z: "-",
    descripcion: "Integral de x²+3 de 0 a 2",
  },
  {
    tipo: "Doble",
    expresion: "x*y",
    limites_x: "[0, 1]",
    limites_y: "[x, x+2]",
    limites_z: "-",
    descripcion: "Doble integral con límites funcionales en y",
  },
  {
    tipo: "Doble",
    expresion: "sin(x) + cos(y)",
    limites_x: "[0, 1]",
    limites_y: "[0, 3]",
    limites_z: "-",
    descripcion: "Funciones trigonométricas",
  },
  {
    tipo: "Triple",
    expresion: "x*y*z",
    limites_x: "[0, 1]",
    limites_y: "[x, x+1]",
    limites_z: "[x+y, x+y+1]",
    descripcion: "Triple integral con límites dependientes",
  },
  {
    tipo: "Triple",
    expresion: "exp(-x**2-y**2-z**2)",
    limites_x: "[0, 1]",
    limites_y: "[0, 1]",
    limites_z: "[0, 1]",
    descripcion: "Exponenciales en triple integral",
  },
];

function ManualDeUso() {
  return (
    <div>
      <h3>Manual de uso y ejemplos</h3>
      <ul style={{ marginBottom: 20 }}>
        <li>
          <b>Para que sirve cada integral:</b> 
        </li>
        <li>
          <b>Simple:</b> Área bajo la curva en un intervalo.
        </li>
        <li>
          <b>Doble:</b> Área de una región plana definida por límites numéricos o funcionales.
        </li>
        <li>
          <b>Triple:</b> Volumen dentro de una región cúbica o definida por funciones.
        </li>
        <li>
          <b>Variables permitidas:</b> Usa <b>x</b> para integrales simples, <b>x</b> y <b>y</b> para dobles, y <b>x, y, z</b> para triples.
        </li>
        <li>
          <b>Funciones permitidas:</b> <code>sin</code>, <code>cos</code>, <code>tan</code>, <code>exp</code>, <code>log</code>, <code>sqrt</code>, <code>sec</code>, <code>csc</code>, <code>cot</code>.
        </li>
        <li>
          <b>Notación natural:</b> Puedes escribir <code>2x</code>, <code>x^2</code>, <code>sin x</code> y el sistema los corrige automáticamente.
        </li>
        <li>
          <b>Límites funcionales:</b> Para límites internos dependientes, escribe por ejemplo <code>y: [x, x+2]</code> o <code>z: [x+y, x+y+1]</code>.
        </li>
        <li>
          <b>Dominio válido:</b> Asegúrate que el límite superior sea mayor que el inferior para todo el rango.
        </li>
        <li>
          <b>Errores comunes:</b> Si ves resultados 0 o infinitos, revisa la sintaxis y los dominios.
        </li>
        <li>
          <b>Visualización:</b> Puedes alternar entre gráfica interactiva (Plotly) y estática (PNG) usando el switch de visualización.
        </li>
      </ul>
      <h4>Ejemplos de expresiones y límites:</h4>
      <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.97em" }}>
        <thead>
          <tr style={{ borderBottom: "1px solid #888" }}>
            <th>Tipo</th>
            <th>Expresión</th>
            <th>Límites x</th>
            <th>Límites y</th>
            <th>Límites z</th>
            <th>Descripción</th>
          </tr>
        </thead>
        <tbody>
          {ejemplos.map((ej, i) => (
            <tr key={i} style={{ borderBottom: "1px solid #ddd" }}>
              <td>{ej.tipo}</td>
              <td>{ej.expresion}</td>
              <td>{ej.limites_x}</td>
              <td>{ej.limites_y}</td>
              <td>{ej.limites_z}</td>
              <td>{ej.descripcion}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default function CalculadoraIntegrales() {
  const [tipo, setTipo] = useState("Simple");
  const [expresion, setExpresion] = useState("");
  const [limiteInf, setLimiteInf] = useState("");
  const [limiteSup, setLimiteSup] = useState("");
  const [yInf, setYInf] = useState("");
  const [ySup, setYSup] = useState("");
  const [zInf, setZInf] = useState("");
  const [zSup, setZSup] = useState("");
  const [resultado, setResultado] = useState(null);
  const [grafica, setGrafica] = useState(null);
  const [error, setError] = useState(null);
  const [modoInteractivo, setModoInteractivo] = useState(true);

  const advertenciaMultiplicacion =
    "Puedes escribir expresiones con notación natural: 2x, sin x, x^2. El sistema las corrige automáticamente.";

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setResultado(null);
    setGrafica(null);

    let endpoint = "";
    let data = {};

    // Preprocesa expresión y límites
    const expProc = preprocesarExpresion(expresion);
    const yInfProc = preprocesarExpresion(yInf);
    const ySupProc = preprocesarExpresion(ySup);
    const zInfProc = preprocesarExpresion(zInf);
    const zSupProc = preprocesarExpresion(zSup);

    // --- FIX: No uses parseFloat, manda los límites como string ---
    if (tipo === "Simple") {
      endpoint = "/simple";
      data = {
        expresion: expProc,
        limite_inf: limiteInf, // string, permite "pi", "e", etc.
        limite_sup: limiteSup,
        modo_interactivo: modoInteractivo,
      };
    } else if (tipo === "Doble") {
      endpoint = "/doble";
      data = {
        expresion: expProc,
        x_inf: limiteInf,
        x_sup: limiteSup,
        y_inf: yInfProc,
        y_sup: ySupProc,
        modo_interactivo: modoInteractivo,
      };
    } else if (tipo === "Triple") {
      endpoint = "/triple";
      data = {
        expresion: expProc,
        x_inf: limiteInf,
        x_sup: limiteSup,
        y_inf: yInfProc,
        y_sup: ySupProc,
        z_inf: zInfProc,
        z_sup: zSupProc,
        modo_interactivo: modoInteractivo,
      };
    }

    try {
      const res = await axios.post(`${backendUrl}${endpoint}`, data);
      setResultado(res.data.valor || res.data.resultado);
      setGrafica(res.data.grafica);
    } catch (err) {
      if (
        err.response &&
        err.response.data &&
        (err.response.data.error || err.response.data.detail)
      ) {
        setError(err.response.data.error || err.response.data.detail);
      } else {
        setError("Error inesperado. Intenta nuevamente.");
      }
    }
  };

  function renderGrafica() {
    if (!grafica) return null;
    if (typeof grafica === "string" && grafica.endsWith(".png")) {
      return (
        <img
          src={`${backendUrl}/${grafica.replace(/\\/g, "/")}`}
          alt="Gráfica de la integral"
          style={{ maxWidth: 600, border: "1px solid #888", marginTop: 12 }}
        />
      );
    }
    if (typeof grafica === "object" && grafica.data) {
      return (
        <Plot
          data={grafica.data}
          layout={grafica.layout}
          config={{ responsive: true }}
          style={{ maxWidth: 700, margin: "0 auto", marginTop: 12 }}
        />
      );
    }
    return null;
  }

  // --- UI dividida en dos cuadros ---
  return (
    <div className="contenedor-flex" style={{
      display: "flex",
      gap: 40,
      alignItems: "flex-start",
      justifyContent: "center",
      flexWrap: "wrap"
    }}>
      {/* Panel de la calculadora */}
      <div className="calcu-panel" style={{
        flex: "1 1 380px",
        minWidth: 340,
        maxWidth: 480
      }}>
        <h2 style={{ textAlign: "center" }}>Calculadora de Integrales</h2>
        <p style={{ textAlign: "center" }}>
          Elige el tipo de integral, ingresa la expresión y los límites.<br />
          Puedes usar funciones para límites internos en integrales dobles/triples (<b>ej: sin(x)</b>).
        </p>
        <form onSubmit={handleSubmit} style={{ marginBottom: 24 }}>
          <div>
            <label>
              Tipo de integral{" "}
              <select
                value={tipo}
                onChange={(e) => {
                  setTipo(e.target.value);
                  setError(null);
                  setResultado(null);
                  setGrafica(null);
                }}
              >
                <option>Simple</option>
                <option>Doble</option>
                <option>Triple</option>
              </select>
            </label>
            <label style={{ marginLeft: 20 }}>
              Visualización interactiva{" "}
              <input
                type="checkbox"
                checked={modoInteractivo}
                onChange={() => setModoInteractivo((prev) => !prev)}
              />
            </label>
          </div>
          <div style={{ margin: "8px 0" }}>
            <label>
              Expresión*{" "}
              <input
                type="text"
                value={expresion}
                placeholder="Ej: x**2 + 3"
                onChange={(e) => setExpresion(e.target.value)}
                style={{ width: 220 }}
                required
              />
            </label>
            <div style={{ color: "#b85c00", fontSize: "0.95em", marginTop: 2 }}>
              {advertenciaMultiplicacion}
            </div>
          </div>
          <div style={{ margin: "8px 0" }}>
            <label>
              Límite inferior*{" "}
              <input
                type="text"
                value={limiteInf}
                onChange={(e) => setLimiteInf(e.target.value)}
                style={{ width: 60 }}
                required
              />
            </label>
            <label style={{ marginLeft: 16 }}>
              Límite superior*{" "}
              <input
                type="text"
                value={limiteSup}
                onChange={(e) => setLimiteSup(e.target.value)}
                style={{ width: 60 }}
                required
              />
            </label>
          </div>
          {(tipo === "Doble" || tipo === "Triple") && (
            <div style={{ margin: "8px 0" }}>
              <label>
                Límite y inferior{" "}
                <input
                  type="text"
                  value={yInf}
                  onChange={(e) => setYInf(e.target.value)}
                  style={{ width: 80 }}
                  placeholder="Ej: x"
                  required={tipo !== "Simple"}
                />
              </label>
              <label style={{ marginLeft: 16 }}>
                Límite y superior{" "}
                <input
                  type="text"
                  value={ySup}
                  onChange={(e) => setYSup(e.target.value)}
                  style={{ width: 80 }}
                  placeholder="Ej: x+2"
                  required={tipo !== "Simple"}
                />
              </label>
            </div>
          )}
          {tipo === "Triple" && (
            <div style={{ margin: "8px 0" }}>
              <label>
                Límite z inferior{" "}
                <input
                  type="text"
                  value={zInf}
                  onChange={(e) => setZInf(e.target.value)}
                  style={{ width: 80 }}
                  placeholder="Ej: x+y"
                  required
                />
              </label>
              <label style={{ marginLeft: 16 }}>
                Límite z superior{" "}
                <input
                  type="text"
                  value={zSup}
                  onChange={(e) => setZSup(e.target.value)}
                  style={{ width: 80 }}
                  placeholder="Ej: x+y+1"
                  required
                />
              </label>
            </div>
          )}
          <button type="submit" style={{ marginTop: 12, padding: "6px 20px" }}>
            CALCULAR
          </button>
        </form>
        {error && (
          <div style={{ color: "red", marginBottom: 16, textAlign: "center" }}>
            {error}
          </div>
        )}
        {resultado !== null && (
          <div style={{ marginBottom: 12 }}>
            <b>Resultado:</b> {resultado}
          </div>
        )}
        {grafica && (
          <div>
            {renderGrafica()}
          </div>
        )}
      </div>
      {/* Panel del manual y ejemplos */}
      <div className="manual-panel" style={{
        flex: "1 1 350px",
        minWidth: 320,
        maxWidth: 480,
        background: "#f7f7f7",
        borderRadius: 12,
        padding: 24,
        boxShadow: "0 0 5px #ddd"
      }}>
        <ManualDeUso />
      </div>
    </div>
  );
}