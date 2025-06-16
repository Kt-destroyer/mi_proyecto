interface ResultadoIntegral {
  valor: number;
  grafica: string;
  expresion_latex?: string;
}

type TipoIntegral = 'simple' | 'doble' | 'triple';