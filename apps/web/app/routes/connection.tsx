import { useState } from "react";
import { Link } from "react-router";

type Connection = "idle" | "checking" | "connected" | "failed";

export function meta() {
  return [
    { title: "Comprobación local | Abogalia" },
    { name: "robots", content: "noindex" },
  ];
}

export default function ConnectionCheck() {
  const [connection, setConnection] = useState<Connection>("idle");

  async function checkConnection() {
    setConnection("checking");
    try {
      const response = await fetch("/api/health", {
        cache: "no-store",
        signal: AbortSignal.timeout(5000),
      });
      if (!response.ok) throw new Error("API unavailable");
      const result: unknown = await response.json();
      if (
        typeof result !== "object" ||
        result === null ||
        !("status" in result) ||
        result.status !== "ok" ||
        !("service" in result) ||
        result.service !== "abogalia-api"
      ) {
        throw new Error("Unexpected API response");
      }
      setConnection("connected");
    } catch {
      setConnection("failed");
    }
  }

  const messages: Record<Connection, string> = {
    idle: "Comprueba que el frontend puede comunicarse con la API local.",
    checking: "Comprobando conexión…",
    connected: "Conexión con FastAPI comprobada.",
    failed:
      "No pudimos conectar. Comprueba que la API local esté encendida y vuelve a intentar.",
  };

  return (
    <main id="contenido" className="shell">
      <Link to="/" className="brand">
        Abogalia
      </Link>
      <section className="intro" aria-labelledby="titulo">
        <p className="eyebrow">Solo en desarrollo</p>
        <h1 id="titulo">Comprobación de conexión</h1>
        <p role="status" aria-live="polite">
          {messages[connection]}
        </p>
        <button
          type="button"
          onClick={checkConnection}
          disabled={connection === "checking"}
        >
          {connection === "checking" ? "Comprobando…" : "Comprobar API"}
        </button>
        <p className="note">
          Esta comprobación confirma la conexión HTTP. No verifica la base de
          datos, autenticación ni permisos del producto.
        </p>
      </section>
    </main>
  );
}
