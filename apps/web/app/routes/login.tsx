import { Link, useNavigate } from "react-router";
import {
  AuthForm,
  AuthShell,
  emailField,
  passwordField,
} from "../components/auth-form";
import { AuthError, authPost, readSession } from "../lib/auth";

export function meta() {
  return [
    { title: "Entrar | Abogalia" },
    { name: "robots", content: "noindex, nofollow" },
    { name: "referrer", content: "no-referrer" },
  ];
}

export default function Login() {
  const navigate = useNavigate();
  return (
    <AuthShell
      title="Entrar"
      description="Entra para consultar tu cuenta y tus servicios."
    >
      <AuthForm
        fields={[emailField, passwordField]}
        submitLabel="Entrar"
        onSubmit={async (values, signal) => {
          const session = readSession(await authPost("login", values, signal));
          if (!session.authenticated)
            throw new AuthError("INVALID_CREDENTIALS", 401);
        }}
        onSuccess={() => {
          void navigate("/cuenta", { replace: true });
        }}
      />
      <nav className="auth-links" aria-label="Opciones de acceso">
        <Link to="/registro">Crear cuenta</Link>
        <Link to="/recuperar">Recuperar acceso</Link>
      </nav>
    </AuthShell>
  );
}
