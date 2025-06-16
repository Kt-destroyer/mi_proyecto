import { useState } from 'react';
import axios from 'axios';
import GraficaIntegral from './GraficaIntegral';

export default function Calculadora() {
  const [expresion, setExpresion] = useState('x^2');
  const [resultado, setResultado] = useState<ResultadoIntegral | null>(null);
  const [cargando, setCargando] = useState(false);

  const calcular = async (tipo: TipoIntegral) => {
    try {
      setCargando(true);
      const { data } = await axios.post(`http://localhost:8000/${tipo}`, {
        expresion: expresion.replace(/\^/g, '**'),
        limite_inf: 0,
        limite_sup: 1
      });
      setResultado(data);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setCargando(false);
    }
  };

  return (
    <div className="calculadora">
      <h1>Calculadora de Integrales</h1>
      <input
        type="text"
        value={expresion}
        onChange={(e) => setExpresion(e.target.value)}
        placeholder="Ej: x^2 + sin(x)"
      />
      
      <div className="botones">
        <button onClick={() => calcular('simple')} disabled={cargando}>
          {cargando ? 'Calculando...' : 'Integral Simple'}
        </button>
        {/* Botones para doble/triple */}
      </div>

      {resultado && (
        <div className="resultado">
          <h3>Resultado: {resultado.valor.toFixed(4)}</h3>
          <GraficaIntegral url={resultado.grafica} />
        </div>
      )}
    </div>
  );
}