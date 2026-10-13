import { Link } from "react-router";

export function meta() {
  return [
    { title: "Abogalia | Atención legal clara y continua" },
    {
      name: "description",
      content:
        "Estamos construyendo Abogalia para facilitar una atención legal clara y continua en México.",
    },
  ];
}

export default function Home() {
  return (
    <main id="contenido" className="shell">
      <header className="topline">
        <span className="brand">Abogalia</span>
        <span className="badge">En desarrollo</span>
      </header>
      <section className="intro" aria-labelledby="titulo">
        <p className="eyebrow">Un camino más claro</p>
        <h1 id="titulo">Atención legal clara y continua.</h1>
        <p className="lead">
          Estamos construyendo un espacio para encontrar atención profesional,
          entender las condiciones del servicio y saber qué sigue.
        </p>
        <p>Abogalia todavía no está disponible para contratar servicios.</p>
      </section>
      {import.meta.env.DEV ? (
        <footer className="footer">
          <Link to="/dev/conexion">Comprobar la conexión local con la API</Link>
        </footer>
      ) : null}
    </main>
  );
}
