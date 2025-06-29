import React, { useState } from "react";
import axios from "axios";
import "./App.css";
import {
  Box,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Typography,
  Paper
} from "@mui/material";
import Plot from "react-plotly.js";

// Google Fonts import for Montserrat and Roboto Slab
const fontLink = document.createElement("link");
fontLink.href = "https://fonts.googleapis.com/css?family=Montserrat:400,700|Roboto+Slab:400,700&display=swap";
fontLink.rel = "stylesheet";
document.head.appendChild(fontLink);

const BACKEND_URL = "http://localhost:8000";

type TipoIntegral = "simple" | "doble" | "triple";

function tieneFuncionesSinParentesis(expr: string) {
  const funciones = ['sin', 'cos', 'tan', 'log', 'exp', 'sqrt', 'abs', 'sec', 'csc', 'cot'];
  for (const f of funciones) {
    const regex = new RegExp(`\\b${f}\\s+[a-zA-Z0-9]`, "i");
    if (regex.test(expr)) {
      return true;
    }
  }
  return false;
}

function ManualDeUso() {
  return (
    <div>
      <h3>Manual de uso</h3>
      <ul>
        <li>
          <b>Variables permitidas:</b> Usa <b>x</b> para integrales simples, <b>x, y</b> para dobles, y <b>x, y, z</b> para triples.
        </li>
        <li>
          <b>Funciones permitidas:</b> <code>sin</code>, <code>cos</code>, <code>tan</code>, <code>exp</code>, <code>log</code>, <code>sqrt</code>, <code>abs</code>, <code>sec</code>, <code>csc</code>, <code>cot</code>.
        </li>
        <li>
          <b>Notación natural:</b> Puedes escribir <code>2x</code>, <code>x^2</code> y el sistema los corrige automáticamente.
        </li>
        <li>
          <b>Límites funcionales:</b> Para límites internos dependientes, escribe por ejemplo <code>y: [x, sqrt(x)]</code> o <code>z: [x+y, x+y+1]</code>.
        </li>
        <li>
          <b>Dominio válido:</b> Asegúrate que el límite superior sea mayor que el inferior para todo el rango.
        </li>
        <li>
          <b>Errores comunes:</b> Si ves resultados 0 o infinitos, revisa la sintaxis y los dominios, evita cosas como:
          <ul>
            <li>
              Si la función tiene discontinuidades (por ejemplo, <code>sec(x)</code>, <code>tan(x)</code>, <code>1/(x-a)</code> en el intervalo), puede aparecer: <i>"La función tiene discontinuidades en el intervalo de integración. El resultado puede ser indefinido o incorrecto."</i>
            </li>
            <li>
              Si usas variables no permitidas, verás: <i>"Variables no permitidas: ..."</i>
            </li>
            <li>
              Si la expresión tiene error de sintaxis, verás: <i>"Error en la expresión ingresada. Revisa paréntesis y sintaxis."</i>
            </li>
            <li>
              Si el dominio de la función es inválido en el intervalo (por ejemplo, raíz de negativo, logaritmo de cero/negativo), verás: <i>"El resultado de la integral es infinito o indefinido. Cambia los límites o la función."</i>
            </li>
            <li>
              Si los límites son iguales o están invertidos, recibirás mensajes específicos para corregirlos.
            </li>
          </ul>
        </li>
        
         
        
      </ul>
      <h4>Ejemplos de expresiones y límites:</h4>
      <table className="ejemplos-tabla">
        <thead>
          <tr>
            <th>Tipo</th>
            <th>Expresión</th>
            <th>Límites x</th>
            <th>Límites y</th>
            <th>Límites z</th>
            <th>Descripción</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>Simple</td>
            <td>x**2 + 3</td>
            <td>[0, 2]</td>
            <td>-</td>
            <td>-</td>
            <td>Integral de x<sup>2</sup>+3 de 0 a 2</td>
          </tr>
          <tr>
            <td>Doble</td>
            <td>x*y</td>
            <td>[0, 1]</td>
            <td>[x, x+2]</td>
            <td>-</td>
            <td>Doble integral con límites funcionales en y</td>
          </tr>
          <tr>
            <td>Doble</td>
            <td>sin(x) + cos(y)</td>
            <td>[0, 1]</td>
            <td>[0, 3]</td>
            <td>-</td>
            <td>Funciones trigonométricas</td>
          </tr>
          <tr>
            <td>Triple</td>
            <td>x*y*z</td>
            <td>[0, 1]</td>
            <td>[x, x+1]</td>
            <td>[x+y, x+y+1]</td>
            <td>Triple integral con límites dependientes</td>
          </tr>
          <tr>
            <td>Triple</td>
            <td>exp(-x**2-y**2-z**2)</td>
            <td>[0, 1]</td>
            <td>[0, 1]</td>
            <td>[0, 1]</td>
            <td>Exponenciales en triple integral</td>
          </tr>
          <tr>
            <td>Doble</td>
            <td>sqrt(x*y)</td>
            <td>[0, 1]</td>
            <td>[0, sqrt(x)]</td>
            <td>-</td>
            <td>Raíz cuadrada, límite funcional</td>
          </tr>
          <tr>
            <td>Doble</td>
            <td>abs(x-y)</td>
            <td>[0, 2]</td>
            <td>[x, 2]</td>
            <td>-</td>
            <td>Valor absoluto, límite dependiente</td>
          </tr>
          <tr>
            <td>Doble</td>
            <td>x**2 + sin(y)*cos(x)</td>
            <td>[0, pi]</td>
            <td>[0, 2*pi]</td>
            <td>-</td>
            <td>Polinomio y funciones trigonométricas</td>
          </tr>
          <tr>
            <td>Triple</td>
            <td>sin(x*y*z)</td>
            <td>[0, pi]</td>
            <td>[0, pi/2]</td>
            <td>[0, 2]</td>
            <td>Trigonométrica en triple integral</td>
          </tr>
        </tbody>
      </table>
    </div>
  );
}

export default function App() {
  const [tipo, setTipo] = useState<TipoIntegral>("simple");
  const [expresion, setExpresion] = useState("");
  const [limiteInf, setLimiteInf] = useState("");
  const [limiteSup, setLimiteSup] = useState("");
  const [xInf, setXInf] = useState("");
  const [xSup, setXSup] = useState("");
  const [yInf, setYInf] = useState("");
  const [ySup, setYSup] = useState("");
  const [txInf, setTxInf] = useState("");
  const [txSup, setTxSup] = useState("");
  const [tyInf, setTyInf] = useState("");
  const [tySup, setTySup] = useState("");
  const [tzInf, setTzInf] = useState("");
  const [tzSup, setTzSup] = useState("");
  const [resultado, setResultado] = useState<number | null>(null);
  const [graficaUrl, setGraficaUrl] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const limpiar = () => {
    setTipo("simple");
    setExpresion("");
    setLimiteInf("");
    setLimiteSup("");
    setXInf(""); setXSup(""); setYInf(""); setYSup("");
    setTxInf(""); setTxSup(""); setTyInf(""); setTySup(""); setTzInf(""); setTzSup("");
    setResultado(null);
    setGraficaUrl(null);
    setError(null);
  };

  const handleTipoChange = (e: any) => {
    setTipo(e.target.value);
    setResultado(null);
    setGraficaUrl(null);
    setError(null);
  };

  function limitesInvalidos(): string | null {
    if (tipo === "simple") {
      if (limiteInf === limiteSup && limiteInf !== "") return "Límites superior e inferior iguales.";
    }
    if (tipo === "doble") {
      if (xInf === xSup && xInf !== "") return "Límites superior e inferior de x iguales.";
    }
    if (tipo === "triple") {
      if (txInf === txSup && txInf !== "") return "Límites superior e inferior de x iguales.";
    }
    return null;
  }

  function traducirErrorBackend(msg: string): string {
    if (msg.toLowerCase().includes("discontinuidad") || msg.toLowerCase().includes("discontinuities")) {
      return "La función tiene discontinuidades en el intervalo de integración. El resultado puede ser indefinido o incorrecto.";
    }
    if (msg.includes("mayor que el superior")) return "El límite inferior es mayor que el superior. Por favor invierte los límites.";
    if (msg.includes("son iguales")) return "Los límites superior e inferior de integración son iguales.";
    if (msg.includes("Error en la expresión")) return "Error en la expresión ingresada. Revisa paréntesis y sintaxis.";
    if (msg.includes("No se pudo graficar")) return "Ocurrió un problema al graficar la región de integración.";
    if (
      msg.includes("cannot convert expression to float") ||
      msg.includes("Cannot convert expression to float")
    )
      return "Uno de los límites o la expresión no es válida. Revisa que los límites sean números o funciones válidas de la variable correspondiente.";
    if (msg.toLowerCase().includes("infinito") || msg.toLowerCase().includes("indefinido")) {
      return "El resultado de la integral es infinito o indefinido. Cambia los límites o la función.";
    }
    if (msg.toLowerCase().includes("variables no permitidas")) {
      return msg;
    }
    // Muestra el mensaje real del backend si no hay coincidencia específica
    return msg;
  }

  const calcular = async (e: React.FormEvent) => {
    e.preventDefault();
    setResultado(null);
    setGraficaUrl(null);
    setError(null);

    // Validaciones frontend
    const errLim = limitesInvalidos();
    if (errLim) {
      setError(errLim);
      return;
    }
    if (tieneFuncionesSinParentesis(expresion)) {
      setError("Por favor escribe las funciones matemáticas con paréntesis. Ejemplo: sin(y), no sin y.");
      return;
    }

    let res: any = undefined;
    try {
      if (tipo === "simple") {
        res = await axios.post(`${BACKEND_URL}/simple`, {
          expresion,
          limite_inf: limiteInf,
          limite_sup: limiteSup,
        });
      } else if (tipo === "doble") {
        res = await axios.post(`${BACKEND_URL}/doble`, {
          expresion,
          x_inf: xInf,
          x_sup: xSup,
          y_inf: yInf,
          y_sup: ySup,
        });
      } else if (tipo === "triple") {
        res = await axios.post(`${BACKEND_URL}/triple`, {
          expresion,
          x_inf: txInf,
          x_sup: txSup,
          y_inf: tyInf,
          y_sup: tySup,
          z_inf: tzInf,
          z_sup: tzSup,
        });
      }
      if (res) {
        setResultado(res.data.valor !== undefined ? res.data.valor : null);
        if (res.data.grafica) {
          if (typeof res.data.grafica === "string") {
            setGraficaUrl(
              res.data.grafica.startsWith("http")
                ? res.data.grafica
                : `${BACKEND_URL}/${res.data.grafica.replace(/^\/+/, "")}`
            );
          } else {
            setGraficaUrl(res.data.grafica);
          }
        } else {
          setGraficaUrl(null);
        }
      }
    } catch (err: any) {
      setError(
        traducirErrorBackend(
          err?.response?.data?.detail || err?.message || "Error al calcular la integral"
        )
      );
    }
  };

  function renderGrafica() {
    if (!graficaUrl) return null;
    if (typeof graficaUrl === "string") {
      return (
        <img
          src={graficaUrl}
          alt="Gráfica de la integral"
          style={{
            maxWidth: "100%",
            borderRadius: "18px",
            boxShadow: "0 4px 24px 0 rgba(0,0,0,0.11)",
            marginTop: 10,
          }}
        />
      );
    }
    if (typeof graficaUrl === "object" && graficaUrl.data) {
      return (
        <div style={{ width: "100%", maxWidth: 700, margin: "0 auto", marginTop: 12, overflow: "auto" }}>
          <Plot
            data={graficaUrl.data}
            layout={{
              ...graficaUrl.layout,
              autosize: true,
              width: "100%",
              height: 400,
              margin: { l: 40, r: 40, b: 40, t: 40 },
            }}
            config={{ responsive: true }}
            style={{ width: "100%", height: 400, minHeight: 360 }}
          />
        </div>
      );
    }
    return null;
  }

  return (
    <div className="app-center" style={{ minHeight: "100vh" }}>
      {resultado === null ? (
        <div className="contenedor-flex">
          {/* Panel izquierdo: calculadora */}
          <div className="calcu-panel">
            {/* ¡AQUÍ papel sin fondo! */}
            <Paper className="app-paper" elevation={8} sx={{ p: 4, background: "transparent" }}>
              <Typography variant="h4" fontWeight={700} gutterBottom align="center" sx={{ fontFamily: "'Roboto Slab', serif" }}>
                Calculadora de Integrales
              </Typography>
              <Typography variant="subtitle1" gutterBottom align="center" sx={{ color: "#333", fontFamily: "'Montserrat',sans-serif" }}>
                Elige el tipo de integral, ingresa la expresión y los límites.<br />
                Puedes usar funciones para límites internos en integrales dobles/triples (<b>ej: sin(x)</b>).
              </Typography>
              <Box component="form" onSubmit={calcular} sx={{ mt: 3 }}>
                <FormControl fullWidth sx={{ mb: 3 }}>
                  <InputLabel>Tipo de integral</InputLabel>
                  <Select value={tipo} label="Tipo de integral" onChange={handleTipoChange}>
                    <MenuItem value="simple">Simple</MenuItem>
                    <MenuItem value="doble">Doble</MenuItem>
                    <MenuItem value="triple">Triple</MenuItem>
                  </Select>
                </FormControl>

                <TextField
                  label="Expresión"
                  fullWidth
                  required
                  variant="outlined"
                  sx={{ mb: 3 }}
                  value={expresion}
                  onChange={e => setExpresion(e.target.value)}
                  placeholder={tipo === "simple" ? "ej: x**2 + 3" : tipo === "doble" ? "ej: x*y + y**2" : "ej: x*y*z"}
                />

                {tipo === "simple" && (
                  <div className="row">
                    <div className="col">
                      <TextField
                        label="Límite inferior (número o expresión, ej: 0, pi, 2*pi, e)"
                        fullWidth
                        required
                        value={limiteInf}
                        onChange={e => setLimiteInf(e.target.value)}
                        type="text"
                      />
                    </div>
                    <div className="col">
                      <TextField
                        label="Límite superior (número o expresión, ej: 1, pi, 2*pi, e)"
                        fullWidth
                        required
                        value={limiteSup}
                        onChange={e => setLimiteSup(e.target.value)}
                        type="text"
                      />
                    </div>
                  </div>
                )}

                {tipo === "doble" && (
                  <>
                    <div className="row">
                      <div className="col">
                        <TextField
                          label="x inferior (número o expresión, ej: 0, pi, 2*pi, e)"
                          fullWidth
                          required
                          value={xInf}
                          onChange={e => setXInf(e.target.value)}
                          type="text"
                        />
                      </div>
                      <div className="col">
                        <TextField
                          label="x superior (número o expresión, ej: 1, pi, 2*pi, e)"
                          fullWidth
                          required
                          value={xSup}
                          onChange={e => setXSup(e.target.value)}
                          type="text"
                        />
                      </div>
                    </div>
                    <div className="row">
                      <div className="col">
                        <TextField
                          label="y inferior (número o función de x)"
                          fullWidth
                          required
                          value={yInf}
                          onChange={e => setYInf(e.target.value)}
                          placeholder="ej: 0 o x"
                        />
                      </div>
                      <div className="col">
                        <TextField
                          label="y superior (número o función de x)"
                          fullWidth
                          required
                          value={ySup}
                          onChange={e => setYSup(e.target.value)}
                          placeholder="ej: 1 o x**2"
                        />
                      </div>
                    </div>
                  </>
                )}

                {tipo === "triple" && (
                  <>
                    <div className="row">
                      <div className="col">
                        <TextField
                          label="x inferior (número o expresión, ej: 0, pi, 2*pi, e)"
                          fullWidth
                          required
                          value={txInf}
                          onChange={e => setTxInf(e.target.value)}
                          type="text"
                        />
                      </div>
                      <div className="col">
                        <TextField
                          label="x superior (número o expresión, ej: 1, pi, 2*pi, e)"
                          fullWidth
                          required
                          value={txSup}
                          onChange={e => setTxSup(e.target.value)}
                          type="text"
                        />
                      </div>
                    </div>
                    <div className="row">
                      <div className="col">
                        <TextField
                          label="y inferior (número o función de x)"
                          fullWidth
                          required
                          value={tyInf}
                          onChange={e => setTyInf(e.target.value)}
                          placeholder="ej: 0 o x"
                        />
                      </div>
                      <div className="col">
                        <TextField
                          label="y superior (número o función de x)"
                          fullWidth
                          required
                          value={tySup}
                          onChange={e => setTySup(e.target.value)}
                          placeholder="ej: 1 o x**2"
                        />
                      </div>
                    </div>
                    <div className="row">
                      <div className="col">
                        <TextField
                          label="z inferior (número o función de x,y)"
                          fullWidth
                          required
                          value={tzInf}
                          onChange={e => setTzInf(e.target.value)}
                          placeholder="ej: 0, x o y"
                        />
                      </div>
                      <div className="col">
                        <TextField
                          label="z superior (número o función de x,y)"
                          fullWidth
                          required
                          value={tzSup}
                          onChange={e => setTzSup(e.target.value)}
                          placeholder="ej: 1 o x**2+y"
                        />
                      </div>
                    </div>
                  </>
                )}

                <Button variant="contained" color="primary" type="submit" size="large" sx={{
                  mt: 2,
                  background: "linear-gradient(90deg, #005f73 0%, #0a9396 100%)"
                }}>
                  Calcular
                </Button>
              </Box>

              {error && (
                <Typography sx={{ mt: 3 }} color="error" align="center">
                  {error}
                </Typography>
              )}
            </Paper>
          </div>
          {/* Panel derecho: manual y ejemplos */}
          <div className="manual-panel">
            <ManualDeUso />
          </div>
        </div>
      ) : (
        // Solo el resultado y la gráfica, centrados
        <div className="calcu-panel" style={{ margin: "0 auto" }}>
          {/* ¡AQUÍ papel sin fondo! */}
          <Paper className="app-paper" elevation={8} sx={{ p: 4, background: "transparent" }}>
            <Box sx={{ mt: 4, textAlign: "center" }} className="resultado-animado">
              <Typography variant="h5" gutterBottom sx={{ fontFamily: "'Roboto Slab', serif" }}>
                El resultado de la integral de&nbsp;
                <b>
                  {tipo === "simple"
                    ? `f(x) = ${expresion}`
                    : tipo === "doble"
                    ? `f(x, y) = ${expresion}`
                    : `f(x, y, z) = ${expresion}`}
                </b>
              </Typography>
              <Typography variant="body1" gutterBottom sx={{ fontFamily: "'Montserrat',sans-serif" }}>
                con límites&nbsp;
                {tipo === "simple"
                  ? `x: [${limiteInf}, ${limiteSup}]`
                  : tipo === "doble"
                  ? `x: [${xInf}, ${xSup}], y: [${yInf}, ${ySup}]`
                  : `x: [${txInf}, ${txSup}], y: [${tyInf}, ${tySup}], z: [${tzInf}, ${tzSup}]`}
                  <span style={{ fontWeight: 600 }}> es:</span>
              </Typography>
              <Typography variant="h4" sx={{ color: "#198754", fontFamily: "'Montserrat',sans-serif" }}>
                <b>{resultado}</b>
              </Typography>
              {graficaUrl && (
                <Box sx={{ mt: 3, textAlign: "center" }}>
                  <Typography variant="h6" sx={{ mb: 1 }}>
                    Gráfica generada:
                  </Typography>
                  {renderGrafica()}
                </Box>
              )}
              <button className="nuevo" onClick={limpiar} type="button">
                ¿Desea calcular otra integral?
              </button>
            </Box>
          </Paper>
        </div>
      )}
    </div>
  );
}