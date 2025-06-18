
import React, { useState } from "react";
import axios from "axios";
import { MathJax, MathJaxContext } from "better-react-mathjax";
import "./App.css";

const config = {
  loader: { load: ["input/asciimath", "input/tex"] },
};

const App: React.FC = () => {
  const [latex, setLatex] = useState("\\int_0^1 x^2 dx");
  const [result, setResult] = useState("");
  const [loading, setLoading] = useState(false);

  const calcularIntegral = async () => {
    setLoading(true);
    try {
      const res = await axios.post("http://localhost:8000/calcular", { latex });
      setResult(res.data.resultado);
    } catch (error) {
      setResult("Error consultando el backend");
    }
    setLoading(false);
  };

  return (
    <MathJaxContext config={config}>
      <div className="container">
        <h1>Calculadora de Integrales</h1>
        <div>
          <label>Expresión en LaTeX:</label>
          <input
            type="text"
            value={latex}
            onChange={(e) => setLatex(e.target.value)}
            className="input"
          />
          <button onClick={calcularIntegral} disabled={loading}>
            {loading ? "Calculando..." : "Calcular"}
          </button>
        </div>
        <div>
          <strong>Vista previa:</strong>
          <div className="preview">
            <MathJax dynamic inline>{`\\(${latex}\\)`}</MathJax>
          </div>
        </div>
        <div>
          <strong>Resultado:</strong>
          <div className="preview">
            <MathJax dynamic inline>{result ? `\\(${result}\\)` : ""}</MathJax>
          </div>
        </div>
      </div>
    </MathJaxContext>
  );
};

export default App;