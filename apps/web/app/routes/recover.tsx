import { Link } from "react-router";
import {
  AuthForm,
  AuthShell,
  codeField,
  emailField,
  newPasswordField,
  repeatField,
} from "../components/auth-form";
import { authPost, readAccepted } from "../lib/auth";

export function meta() {
  return [
    { title: "Recuperar acceso | Abogalia" },
    { name: "robots", content: "noindex, nofollow" },
    { name: "referrer", content: "no-referrer" },
  ];
}

export default function Recover() {
  return (
    <AuthShell
      title="Recuperar acceso"
      description="Solicita instrucciones para cambiar tu contraseña."
    >
      <AuthForm
        fields={[emailField]}
        submitLabel="Solicitar recuperación"
        onSubmit={async (values, signal) => {
          readAccepted(await authPost("recover", values, signal));
        }}
        successMessage="Si hay una cuenta que pueda recuperarse con ese correo, recibirás las instrucciones."
      />
      <section className="auth-section" aria-labelledby="recover-title">
        <h2 id="recover-title">Cambiar contraseña con un código</h2>
        <p>Introduce el código recibido por correo y tu nueva contraseña.</p>
        <AuthForm
          fields={[emailField, codeField, newPasswordField, repeatField]}
          submitLabel="Cambiar contraseña"
          onSubmit={async (values, signal) => {
            await authPost("recover/complete", values, signal);
          }}
          successMessage="Contraseña actualizada. Vuelve a entrar."
        />
        <p className="note">
          Si la operación se interrumpe después de enviar el código, la
          contraseña puede haber cambiado. Intenta entrar con la nueva
          contraseña antes de solicitar otro código.
        </p>
      </section>
      <Link to="/acceso">Volver a acceso</Link>
    </AuthShell>
  );
}
