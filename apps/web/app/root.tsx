import type { ReactNode } from "react";
import {
  isRouteErrorResponse,
  Links,
  Meta,
  Outlet,
  Scripts,
  ScrollRestoration,
  useRouteError,
} from "react-router";
import "./styles.css";

export function Layout({ children }: { children: ReactNode }) {
  return (
    <html lang="es-MX">
      <head>
        <meta charSet="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <Meta />
        <Links />
      </head>
      <body>
        <a className="skip-link" href="#contenido">
          Ir al contenido
        </a>
        {children}
        <ScrollRestoration />
        <Scripts />
      </body>
    </html>
  );
}

export default function App() {
  return <Outlet />;
}

export function ErrorBoundary() {
  const error = useRouteError();
  const isNotFound = isRouteErrorResponse(error) && error.status === 404;

  return (
    <main id="contenido" className="shell">
      <p className="brand">Legalia</p>
      <h1>
        {isNotFound
          ? "No encontramos esa página"
          : "No pudimos abrir esta página"}
      </h1>
      <p>Vuelve al inicio para continuar.</p>
      <a href="/">Ir al inicio</a>
    </main>
  );
}
