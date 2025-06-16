export default function GraficaIntegral({ url }: { url: string }) {
  return (
    <div className="grafica">
      <img 
        src={`http://localhost:8000/${url}`} 
        alt="Gráfica de la integral"
        onError={(e) => {
          (e.target as HTMLImageElement).style.display = 'none';
        }}
      />
    </div>
  );
}