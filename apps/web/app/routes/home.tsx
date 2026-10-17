import { Link } from "react-router";

export function meta() {
  return [
    { title: "Legalia | Atención legal clara y continua" },
    {
      name: "description",
      content:
        "Estamos construyendo Legalia para facilitar una atención legal clara y continua en México.",
    },
  ];
}

export default function Home() {
  return (
    <main id="contenido" className="shell">
      <header className="topline">
        <span className="brand">Legalia</span>
        <span className="badge">En desarrollo</span>
        <Link to="/acceso">Entrar</Link>
      </header>
      <section className="intro" aria-labelledby="titulo">
        <p className="eyebrow">Un camino más claro</p>
        <h1 id="titulo">Atención legal clara y continua.</h1>
        <p className="lead">
          Estamos construyendo un espacio para encontrar atención profesional,
          entender las condiciones del servicio y saber qué sigue.
        </p>
        <p>Legalia todavía no está disponible para contratar servicios.</p>
        <p>
          <Link to="/registro">Crear cuenta</Link>
        </p>
      </section>
      {import.meta.env.DEV ? (
        <footer className="footer">
          <Link to="/dev/conexion">Comprobar la conexión local con la API</Link>
        </footer>
      ) : null}
    </main>
  );
}
