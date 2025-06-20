import React, { useState } from "react";
import axios from "axios";
import Grid from "@mui/material/Grid"; // Importa Grid así para máxima compatibilidad

import {
  Box,
  Button,
  Container,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Typography,
  Paper
} from "@mui/material";

const BACKEND_URL = "http://localhost:8000";

type TipoIntegral = "simple" | "doble" | "triple";

export default function App() {
  const [tipo, setTipo] = useState<TipoIntegral>("simple");
  const [expresion, setExpresion] = useState("");
  // Simple
  const [limiteInf, setLimiteInf] = useState("");
  const [limiteSup, setLimiteSup] = useState("");
  // Doble
  const [xInf, setXInf] = useState("");
  const [xSup, setXSup] = useState("");
  const [yInf, setYInf] = useState(""); // puede ser número o función
  const [ySup, setYSup] = useState(""); // puede ser número o función
  // Triple
  const [txInf, setTxInf] = useState("");
  const [txSup, setTxSup] = useState("");
  const [tyInf, setTyInf] = useState("");
  const [tySup, setTySup] = useState("");
  const [tzInf, setTzInf] = useState("");
  const [tzSup, setTzSup] = useState("");

  const [resultado, setResultado] = useState<number | null>(null);
  const [graficaUrl, setGraficaUrl] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [expLatex, setExpLatex] = useState<string | null>(null);

  const handleTipoChange = (e: any) => {
    setTipo(e.target.value);
    setResultado(null);
    setGraficaUrl(null);
    setError(null);
    setExpLatex(null);
  };

  const calcular = async (e: React.FormEvent) => {
    e.preventDefault();
    setResultado(null);
    setGraficaUrl(null);
    setError(null);
    setExpLatex(null);

    let res: any = undefined; // Declarar res siempre
    try {
      if (tipo === "simple") {
        res = await axios.post(`${BACKEND_URL}/simple`, {
          expresion,
          limite_inf: parseFloat(limiteInf),
          limite_sup: parseFloat(limiteSup),
        });
      } else if (tipo === "doble") {
        res = await axios.post(`${BACKEND_URL}/doble`, {
          expresion,
          x_inf: parseFloat(xInf),
          x_sup: parseFloat(xSup),
          y_inf: isNaN(Number(yInf)) ? yInf : parseFloat(yInf),
          y_sup: isNaN(Number(ySup)) ? ySup : parseFloat(ySup),
        });
      } else if (tipo === "triple") {
        res = await axios.post(`${BACKEND_URL}/triple`, {
          expresion,
          x_inf: parseFloat(txInf),
          x_sup: parseFloat(txSup),
          y_inf: isNaN(Number(tyInf)) ? tyInf : parseFloat(tyInf),
          y_sup: isNaN(Number(tySup)) ? tySup : parseFloat(tySup),
          z_inf: parseFloat(tzInf),
          z_sup: parseFloat(tzSup),
        });
      }
      if (res) {
        setResultado(res.data.resultado);

        // Asegura que no haya doble barra y que grafica exista
        setGraficaUrl(
          res.data.grafica
            ? res.data.grafica.startsWith("http")
              ? res.data.grafica
              : `${BACKEND_URL}/${res.data.grafica.replace(/^\/+/, "")}`
            : null
        );
        setExpLatex(res.data.expresion_latex || null);
      }
    } catch (err: any) {
      setError(
        err?.response?.data?.detail || "Error al calcular la integral"
      );
    }
  };

  return (
    <Container maxWidth="md" sx={{ py: 6 }}>
      <Paper elevation={4} sx={{ p: 4, borderRadius: 3 }}>
        <Typography variant="h4" fontWeight={700} gutterBottom color="primary">
          Calculadora de Integrales
        </Typography>
        <Typography variant="subtitle1" gutterBottom>
          Elige el tipo de integral, ingresa la expresión y los límites. Puedes usar funciones para límites internos en integrales dobles/triples (ej: <b>sin(x)</b>).
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
            placeholder={tipo === "simple" ? "ej: x**2 + 3" : "ej: x*y + y**2"}
          />

          {/* Campos dinámicos según el tipo */}
          {tipo === "simple" && (
            <Grid container spacing={2} sx={{ mb: 2 }}>
              <Grid item xs={6}>
                <TextField
                  label="Límite inferior"
                  fullWidth
                  required
                  value={limiteInf}
                  onChange={e => setLimiteInf(e.target.value)}
                  type="number"
                />
              </Grid>
              <Grid item xs={6}>
                <TextField
                  label="Límite superior"
                  fullWidth
                  required
                  value={limiteSup}
                  onChange={e => setLimiteSup(e.target.value)}
                  type="number"
                />
              </Grid>
            </Grid>
          )}

          {tipo === "doble" && (
            <Grid container spacing={2} sx={{ mb: 2 }}>
              <Grid item xs={6}>
                <TextField
                  label="x inferior"
                  fullWidth
                  required
                  value={xInf}
                  onChange={e => setXInf(e.target.value)}
                  type="number"
                />
              </Grid>
              <Grid item xs={6}>
                <TextField
                  label="x superior"
                  fullWidth
                  required
                  value={xSup}
                  onChange={e => setXSup(e.target.value)}
                  type="number"
                />
              </Grid>
              <Grid item xs={6}>
                <TextField
                  label="y inferior (número o función de x)"
                  fullWidth
                  required
                  value={yInf}
                  onChange={e => setYInf(e.target.value)}
                  placeholder="ej: 0 o x"
                />
              </Grid>
              <Grid item xs={6}>
                <TextField
                  label="y superior (número o función de x)"
                  fullWidth
                  required
                  value={ySup}
                  onChange={e => setYSup(e.target.value)}
                  placeholder="ej: 1 o x**2"
                />
              </Grid>
            </Grid>
          )}

          {tipo === "triple" && (
            <Grid container spacing={2} sx={{ mb: 2 }}>
              <Grid item xs={4}>
                <TextField
                  label="x inferior"
                  fullWidth
                  required
                  value={txInf}
                  onChange={e => setTxInf(e.target.value)}
                  type="number"
                />
              </Grid>
              <Grid item xs={4}>
                <TextField
                  label="x superior"
                  fullWidth
                  required
                  value={txSup}
                  onChange={e => setTxSup(e.target.value)}
                  type="number"
                />
              </Grid>
              <Grid item xs={4}>
                <TextField
                  label="y inferior (número o función de x)"
                  fullWidth
                  required
                  value={tyInf}
                  onChange={e => setTyInf(e.target.value)}
                  placeholder="ej: 0 o x"
                />
              </Grid>
              <Grid item xs={4}>
                <TextField
                  label="y superior (número o función de x)"
                  fullWidth
                  required
                  value={tySup}
                  onChange={e => setTySup(e.target.value)}
                  placeholder="ej: 1 o x**2"
                />
              </Grid>
              <Grid item xs={4}>
                <TextField
                  label="z inferior (número, recomendado)"
                  fullWidth
                  required
                  value={tzInf}
                  onChange={e => setTzInf(e.target.value)}
                  type="number"
                />
              </Grid>
              <Grid item xs={4}>
                <TextField
                  label="z superior (número, recomendado)"
                  fullWidth
                  required
                  value={tzSup}
                  onChange={e => setTzSup(e.target.value)}
                  type="number"
                />
              </Grid>
            </Grid>
          )}

          <Button variant="contained" color="primary" type="submit" size="large" sx={{ mt: 2 }}>
            Calcular
          </Button>
        </Box>

        {error && (
          <Typography sx={{ mt: 3 }} color="error">
            {error}
          </Typography>
        )}

        {resultado !== null && (
          <Typography variant="h5" sx={{ mt: 4 }}>
            Resultado: <b>{resultado}</b>
          </Typography>
        )}

        {expLatex && (
          <Typography sx={{ mt: 2, fontSize: 18 }}>
            <span>Expresión en LaTeX:</span>
            <pre
              style={{
                background: "#f3f3f3",
                padding: "8px",
                borderRadius: "8px",
                display: "inline-block",
                marginLeft: "10px",
              }}
            >
              {expLatex}
            </pre>
          </Typography>
        )}

        {graficaUrl && (
          <Box sx={{ mt: 3 }}>
            <Typography variant="h6" sx={{ mb: 1 }}>
              Gráfica:
            </Typography>
            <img src={graficaUrl} alt="Gráfica de la integral" style={{ maxWidth: "100%" }} />
          </Box>
        )}
      </Paper>
    </Container>
  );
}