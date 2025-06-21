import React, { useState } from "react";
import axios from "axios";

const backendUrl = process.env.REACT_APP_BACKEND_URL || "http://localhost:8000";

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

  const advertenciaMultiplicacion =
    "Recuerda: Para multiplicar debes usar el símbolo *, por ejemplo 1+cos(2*x) y NO 1+cos(2x).";

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setResultado(null);
    setGrafica(null);

    let endpoint = "";
    let data = {};

    if (tipo === "Simple") {
      endpoint = "/simple";
      data = {
        expresion: expresion,
        limite_inf: parseFloat(limiteInf),
        limite_sup: parseFloat(limiteSup),
      };
    } else if (tipo === "Doble") {
      endpoint = "/doble";
      data = {
        expresion: expresion,
        x_inf: parseFloat(limiteInf),
        x_sup: parseFloat(limiteSup),
        y_inf: yInf,
        y_sup: ySup,
      };
    } else if (tipo === "Triple") {
      endpoint = "/triple";
      data = {
        expresion: expresion,
        x_inf: parseFloat(limiteInf),
        x_sup: parseFloat(limiteSup),
        y_inf: yInf,
        y_sup: ySup,
        z_inf: zInf,
        z_sup: zSup,
      };
    }

    try {
      const res = await axios.post(`${backendUrl}${endpoint}`, data);
      setResultado(res.data.resultado);
      setGrafica(res.data.grafica);
    } catch (err) {
      if (
        err.response &&
        err.response.data &&
        err.response.data.detail
      ) {
        setError(err.response.data.detail);
      } else {
        setError("Error inesperado. Intenta nuevamente.");
      }
    }
  };

  return (
    <div style={{ maxWidth: 800, margin: "0 auto", padding: 24 }}>
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
          <img
            src={`${backendUrl}/${grafica.replace(/\\/g, "/")}`}
            alt="Gráfica de la integral"
            style={{ maxWidth: 600, border: "1px solid #888", marginTop: 12 }}
          />
        </div>
      )}

      <h3>Ejemplos de expresiones y límites:</h3>
      <table style={{ width: "100%", borderCollapse: "collapse" }}>
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