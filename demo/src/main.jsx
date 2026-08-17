import React, { useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import { Archive, CalendarDays, FileText, Folder, Moon, Play, ShieldCheck } from "lucide-react";
import "./styles.css";

const initialFiles = [
  { name: "Portada_A.indd", modified: "04:02", type: "InDesign" },
  { name: "Economia_03.indd", modified: "03:41", type: "InDesign" },
  { name: "Avisos.pdf", modified: "03:18", type: "PDF" },
  { name: "Notas.txt", modified: "02:55", type: "Texto" },
];

const monthNames = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"];

function formatDate(value) {
  const [year, month, day] = value.split("-");
  return `${day}-${month}-${year}`;
}

function App() {
  const [date, setDate] = useState("2026-08-17");
  const [history, setHistory] = useState([]);
  const [mode, setMode] = useState("dry-run");
  const [ran, setRan] = useState(false);

  const destination = useMemo(() => {
    const d = new Date(`${date}T12:00:00`);
    return `C:\\Demo\\Paginas diario\\respaldo\\${monthNames[d.getMonth()]}\\${String(d.getDate()).padStart(2, "0")}`;
  }, [date]);

  const eligible = initialFiles.filter((file) => file.type === "InDesign");

  function runSimulation() {
    const stamp = new Date().toLocaleTimeString("es-CL", { hour: "2-digit", minute: "2-digit" });
    setHistory((current) => [
      ...eligible.map((file) => ({
        time: stamp,
        text: mode === "dry-run" ? `DRY-RUN · ${file.name} sería movido` : `${file.name} movido al respaldo`,
      })),
      ...current,
    ]);
    setRan(true);
  }

  return (
    <main className="app-shell">
      <section className="hero">
        <div>
          <span className="eyebrow"><Moon size={14}/> Flujo nocturno · Windows</span>
          <h1>Organizador de respaldos</h1>
          <p>Simula cómo los archivos InDesign de una jornada nocturna se archivan por fecha de cierre, después de un periodo sin actividad.</p>
        </div>
        <div className="safe-note"><ShieldCheck size={20}/><div><strong>Demo visual</strong><span>No mueve archivos reales.</span></div></div>
      </section>

      <section className="toolbar card">
        <label><span>Fecha ficticia de cierre</span><div className="input-wrap"><CalendarDays size={17}/><input type="date" value={date} onChange={(event) => { setDate(event.target.value); setRan(false); }}/></div></label>
        <label><span>Modo</span><select value={mode} onChange={(event) => setMode(event.target.value)}><option value="dry-run">Dry-run</option><option value="run">Ejecución simulada</option></select></label>
        <button onClick={runSimulation}><Play size={17}/> Simular</button>
      </section>

      <section className="flow-grid">
        <article className="card pane">
          <header><div className="icon"><Folder size={20}/></div><div><span>Origen ficticio</span><strong>Paginas diario</strong></div></header>
          <code>C:\\Demo\\Paginas diario</code>
          <div className="file-list">
            {initialFiles.map((file) => <div className={`file ${file.type === "InDesign" ? "eligible" : "muted"}`} key={file.name}><FileText size={17}/><div><strong>{file.name}</strong><span>{file.type} · {file.modified}</span></div><em>{file.type === "InDesign" ? "Coincide" : "Ignorado"}</em></div>)}
          </div>
        </article>

        <article className="card pane destination">
          <header><div className="icon"><Archive size={20}/></div><div><span>Destino calculado</span><strong>{monthNames[new Date(`${date}T12:00:00`).getMonth()]} / {date.slice(-2)}</strong></div></header>
          <code>{destination}</code>
          <div className="status-box"><span>Jornada</span><strong>19:00 del día anterior → 06:59</strong><span>Regla de seguridad</span><strong>≥ 2 horas sin actividad</strong><span>Fecha probada</span><strong>{formatDate(date)}</strong></div>
          {ran && <div className="result">{mode === "dry-run" ? "Simulación completada: ningún archivo fue movido." : `${eligible.length} archivos serían movidos en una ejecución real.`}</div>}
        </article>
      </section>

      <section className="card history">
        <header><div><span>Historial de la demo</span><strong>Movimientos simulados</strong></div></header>
        {history.length === 0 ? <p className="empty">Ejecuta una simulación para ver el historial.</p> : history.map((item, index) => <div className="history-row" key={`${item.time}-${index}`}><span>{item.time}</span><p>{item.text}</p></div>)}
      </section>
    </main>
  );
}

createRoot(document.getElementById("root")).render(<App />);
