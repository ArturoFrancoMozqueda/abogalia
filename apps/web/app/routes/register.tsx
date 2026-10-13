import { Link } from "react-router";
import {
  AuthForm,
  AuthShell,
  codeField,
  emailField,
  passwordField,
  repeatField,
} from "../components/auth-form";
import { authPost, readAccepted } from "../lib/auth";

export function meta() {
  return [
    { title: "Crear cuenta | Abogalia" },
    { name: "robots", content: "noindex, nofollow" },
    { name: "referrer", content: "no-referrer" },
  ];
}

export default function Register() {
  return (
    <AuthShell
      title="Crear cuenta"
      description="Crea una cuenta para consultar tus servicios. El alta profesional se revisa por separado."
    >
      <AuthForm
        fields={[
          emailField,
          { ...passwordField, autoComplete: "new-password" },
          repeatField,
        ]}
        submitLabel="Crear cuenta"
        onSubmit={async (values, signal) => {
          readAccepted(await authPost("register", values, signal));
        }}
        successMessage="Si podemos completar el registro con ese correo, recibirás las instrucciones para confirmar tu cuenta."
      />
      <section className="auth-section" aria-labelledby="confirm-title">
        <h2 id="confirm-title">Confirmar correo</h2>
        <p>Si ya recibiste un código de confirmación, introdúcelo aquí.</p>
        <AuthForm
          fields={[emailField, codeField]}
          submitLabel="Confirmar correo"
          onSubmit={async (values, signal) => {
            await authPost("confirm", values, signal);
          }}
          successMessage="Correo confirmado. Ya puedes entrar. El alta profesional se revisa por separado."
        />
      </section>
      <Link to="/acceso">Ya tengo cuenta</Link>
    </AuthShell>
  );
}
