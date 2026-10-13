import {
  type FormEvent,
  type ReactNode,
  useEffect,
  useId,
  useRef,
  useState,
} from "react";
import { Link } from "react-router";
import { authMessage } from "../lib/auth";

export type AuthField = {
  name: string;
  label: string;
  type?: "email" | "password" | "text";
  autoComplete?: string;
  code?: boolean;
};

export function AuthShell({
  title,
  description,
  children,
}: {
  title: string;
  description?: string;
  children: ReactNode;
}) {
  return (
    <main id="contenido" className="shell auth-shell">
      <header className="topline">
        <Link className="brand" to="/">
          Abogalia
        </Link>
        <Link to="/acceso">Acceso</Link>
      </header>
      <section className="auth-card" aria-labelledby="auth-title">
        <h1 id="auth-title">{title}</h1>
        {description ? <p>{description}</p> : null}
        {children}
      </section>
    </main>
  );
}

export function AuthForm({
  fields,
  submitLabel,
  onSubmit,
  onSuccess,
  successMessage,
  children,
}: {
  fields: AuthField[];
  submitLabel: string;
  onSubmit: (
    values: Record<string, string>,
    signal: AbortSignal,
  ) => Promise<void>;
  onSuccess?: () => void;
  successMessage?: string;
  children?: ReactNode;
}) {
  const id = useId();
  const formRef = useRef<HTMLFormElement>(null);
  const statusRef = useRef<HTMLParagraphElement>(null);
  const active = useRef(false);
  const inFlight = useRef(false);
  const pending = useRef<{
    controller: AbortController;
    values: Record<string, string>;
  } | null>(null);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");
  const [failed, setFailed] = useState(false);
  const [visible, setVisible] = useState(false);
  const [mismatch, setMismatch] = useState(false);
  useEffect(() => {
    active.current = true;
    const form = formRef.current;
    const clear = () => {
      pending.current?.controller.abort();
      if (pending.current)
        for (const name of Object.keys(pending.current.values))
          delete pending.current.values[name];
      pending.current = null;
      form?.reset();
    };
    window.addEventListener("pagehide", clear);
    return () => {
      active.current = false;
      window.removeEventListener("pagehide", clear);
      clear();
    };
  }, []);
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (inFlight.current) return;
    const form = event.currentTarget;
    const data = new FormData(form);
    const values: Record<string, string> = {};
    for (const field of fields) {
      values[field.name] = String(data.get(field.name) ?? "");
      data.delete(field.name);
    }
    // Inputs retain email only; secret values exist solely for the pending request.
    for (const field of fields) {
      if (field.type === "password" || field.code) {
        const input = form.elements.namedItem(field.name);
        if (input instanceof HTMLInputElement) input.value = "";
      }
    }
    if (
      values.repeat_password !== undefined &&
      values.repeat_password !== (values.password ?? values.new_password)
    ) {
      for (const field of fields)
        if (field.type === "password" || field.code) delete values[field.name];
      setMismatch(true);
      setFailed(true);
      setMessage("Las contraseñas no coinciden. Escríbelas de nuevo.");
      requestAnimationFrame(() =>
        form
          .querySelector<HTMLInputElement>('input[autocomplete="new-password"]')
          ?.focus(),
      );
      return;
    }
    delete values.repeat_password;
    inFlight.current = true;
    const controller = new AbortController();
    pending.current = { controller, values };
    setBusy(true);
    setMessage("");
    setFailed(false);
    setMismatch(false);
    try {
      await onSubmit(values, controller.signal);
      if (active.current) {
        setMessage(successMessage ?? "Solicitud completada.");
        setVisible(false);
        onSuccess?.();
      }
    } catch (error) {
      if (active.current) {
        setFailed(true);
        setMessage(authMessage(error));
      }
    } finally {
      for (const field of fields)
        if (field.type === "password" || field.code) delete values[field.name];
      inFlight.current = false;
      pending.current = null;
      if (active.current) {
        setBusy(false);
        requestAnimationFrame(() => statusRef.current?.focus());
      }
    }
  }
  return (
    <form
      ref={formRef}
      onSubmit={submit}
      className="auth-form"
      aria-busy={busy}
    >
      {fields.map((field) => (
        <div className="auth-field" key={field.name}>
          <label htmlFor={`${id}-${field.name}`}>{field.label}</label>
          <input
            id={`${id}-${field.name}`}
            name={field.name}
            required
            type={
              field.type === "password" && visible
                ? "text"
                : (field.type ?? "text")
            }
            autoComplete={field.autoComplete}
            maxLength={
              field.code ? 6 : field.type === "email" ? 254 : undefined
            }
            inputMode={field.code ? "numeric" : undefined}
            pattern={field.code ? "[0-9]{6}" : undefined}
            aria-invalid={
              mismatch && field.type === "password" ? true : undefined
            }
            aria-describedby={
              mismatch && field.type === "password"
                ? `${id}-status`
                : field.code
                  ? `${id}-code-help`
                  : undefined
            }
          />
          {field.code ? (
            <p id={`${id}-code-help`} className="note">
              Introduce los seis dígitos del código, incluidos los ceros
              iniciales.
            </p>
          ) : null}
        </div>
      ))}
      {fields.some((field) => field.type === "password") ? (
        <button
          className="secondary"
          type="button"
          aria-pressed={visible}
          onClick={() => setVisible(!visible)}
        >
          {visible ? "Ocultar contraseñas" : "Mostrar contraseñas"}
        </button>
      ) : null}
      {children}
      <button type="submit" disabled={busy}>
        {busy ? "Procesando…" : submitLabel}
      </button>
      <p
        id={`${id}-status`}
        ref={statusRef}
        tabIndex={-1}
        className={failed ? "auth-message error" : "auth-message"}
        role={failed ? "alert" : "status"}
      >
        {message}
      </p>
    </form>
  );
}

export const emailField: AuthField = {
  name: "email",
  label: "Correo electrónico",
  type: "email",
  autoComplete: "email",
};
export const passwordField: AuthField = {
  name: "password",
  label: "Contraseña",
  type: "password",
  autoComplete: "current-password",
};
export const newPasswordField: AuthField = {
  name: "new_password",
  label: "Nueva contraseña",
  type: "password",
  autoComplete: "new-password",
};
export const repeatField: AuthField = {
  name: "repeat_password",
  label: "Repite tu contraseña",
  type: "password",
  autoComplete: "new-password",
};
export const codeField: AuthField = {
  name: "code",
  label: "Código",
  code: true,
  autoComplete: "one-time-code",
};
