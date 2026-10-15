import {
  type FormEvent,
  useCallback,
  useEffect,
  useRef,
  useState,
} from "react";
import { Link, useNavigate } from "react-router";
import { AuthError, getSession } from "../lib/auth";
import {
  type PrivateDraft,
  professionalMessage,
  requestPrivateDraft,
} from "../lib/professional-contexts";
import { AuthShell } from "./auth-form";

export function ProfessionalDraft({
  contextsOnly = false,
}: {
  contextsOnly?: boolean;
}) {
  const navigate = useNavigate();
  const [draft, setDraft] = useState<PrivateDraft | null>(null);
  const [busy, setBusy] = useState(true);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [gate, setGate] = useState<"access" | "mfa" | null>(null);
  const [stale, setStale] = useState(false);
  const [confirm, setConfirm] = useState(false);
  const alive = useRef(false);
  const locked = useRef(false);
  const sequence = useRef(0);
  const controller = useRef<AbortController | null>(null);
  const form = useRef<HTMLFormElement>(null);
  const status = useRef<HTMLParagraphElement>(null);
  const confirmation = useRef<HTMLButtonElement>(null);
  const clear = useCallback(() => {
    setDraft(null);
    setConfirm(false);
    form.current?.reset();
  }, []);
  const fail = useCallback(
    (failure: unknown) => {
      setError(professionalMessage(failure));
      setStale(true);
      setConfirm(false);
      if (
        failure instanceof AuthError &&
        (failure.status === 401 || failure.code === "MFA_REQUIRED")
      ) {
        clear();
        setGate(failure.code === "MFA_REQUIRED" ? "mfa" : "access");
      }
    },
    [clear],
  );
  const load = useCallback(async () => {
    if (locked.current) return;
    locked.current = true;
    const generation = ++sequence.current;
    controller.current?.abort();
    const pending = new AbortController();
    controller.current = pending;
    setBusy(true);
    clear();
    setError("");
    setMessage("");
    setGate(null);
    try {
      const session = await getSession();
      if (!alive.current || generation !== sequence.current) return;
      if (!session.authenticated) {
        setGate("access");
        await navigate("/acceso", { replace: true });
        return;
      }
      if (session.user.assurance !== "aal2") {
        setGate("mfa");
        return;
      }
      const result = await requestPrivateDraft(pending.signal);
      if (alive.current && generation === sequence.current) {
        setDraft(result);
        setStale(false);
      }
    } catch (failure) {
      if (alive.current && generation === sequence.current) fail(failure);
    } finally {
      if (generation === sequence.current) locked.current = false;
      if (alive.current && generation === sequence.current) {
        setBusy(false);
        requestAnimationFrame(() => status.current?.focus());
      }
    }
  }, [clear, fail, navigate]);
  useEffect(() => {
    alive.current = true;
    void load();
    const conceal = () => {
      sequence.current++;
      locked.current = false;
      controller.current?.abort();
      clear();
      setStale(true);
    };
    const restore = (event: PageTransitionEvent) => {
      if (event.persisted) void load();
    };
    window.addEventListener("pagehide", conceal);
    window.addEventListener("pageshow", restore);
    return () => {
      alive.current = false;
      conceal();
      window.removeEventListener("pagehide", conceal);
      window.removeEventListener("pageshow", restore);
    };
  }, [clear, load]);
  useEffect(() => {
    if (confirm) confirmation.current?.focus();
  }, [confirm]);
  async function mutate(body: Record<string, unknown>, withdraw = false) {
    if (locked.current || !draft || stale) return;
    locked.current = true;
    setBusy(true);
    setError("");
    setMessage("");
    const generation = ++sequence.current;
    const pending = new AbortController();
    controller.current = pending;
    try {
      const result = await requestPrivateDraft(
        pending.signal,
        withdraw || !draft.profile ? "POST" : "PATCH",
        body,
        withdraw,
      );
      if (alive.current && generation === sequence.current) {
        setDraft(result);
        setConfirm(false);
        form.current?.reset();
        setMessage(
          withdraw
            ? "Perfil retirado y práctica cerrada. El plazo de conservación aprobado es de 30 días; el retiro no confirma borrado físico."
            : "Borrador privado guardado. Tu práctica sigue inactiva.",
        );
      }
    } catch (failure) {
      if (alive.current && generation === sequence.current) fail(failure);
    } finally {
      if (generation === sequence.current) locked.current = false;
      if (alive.current && generation === sequence.current) {
        setBusy(false);
        requestAnimationFrame(() => status.current?.focus());
      }
    }
  }
  function save(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const values = new FormData(event.currentTarget);
    const fields = {
      display_name: String(values.get("display_name") ?? ""),
      declared_area: String(values.get("declared_area") ?? "").trim() || null,
    };
    void mutate(
      draft?.profile
        ? { expected_version: draft.profile.version, fields }
        : fields,
    );
  }
  const profile = draft?.profile;
  const canEdit = !profile || profile.allowed_actions.includes("edit");
  const canWithdraw = profile?.allowed_actions.includes("withdraw") ?? false;
  const practice = draft?.practice_context;
  return (
    <AuthShell
      title={
        contextsOnly ? "Mis contextos profesionales" : "Mi perfil profesional"
      }
      description="Borrador privado. Guardarlo no habilita atención profesional ni acredita identidad o cédula."
    >
      <nav className="auth-links" aria-label="Área profesional">
        <Link to="/cuenta">Mi cuenta</Link>
        <Link to={contextsOnly ? "/profesional" : "/profesional/contextos"}>
          {contextsOnly ? "Mi perfil" : "Mis contextos"}
        </Link>
      </nav>
      <p
        ref={status}
        tabIndex={-1}
        role={error ? "alert" : "status"}
        className={error ? "auth-message error" : "auth-message"}
      >
        {error || message || (busy ? "Cargando…" : "")}
      </p>
      {gate === "mfa" ? (
        <p>
          <Link to="/cuenta">Completar verificación en dos pasos</Link> para
          acceder al área privada.
        </p>
      ) : gate === "access" ? (
        <p>
          <Link to="/acceso">Volver a entrar</Link>
        </p>
      ) : null}
      {!busy && !gate ? (
        <button className="secondary" type="button" onClick={() => void load()}>
          Actualizar información
        </button>
      ) : null}
      {draft && !gate ? (
        <>
          {practice ? (
            <section aria-labelledby="practice-title">
              <h2 id="practice-title">Práctica propia</h2>
              <p>{practice.title}</p>
              <p>
                {practice.state === "preparing"
                  ? "Inactiva: en preparación. Sin permisos de trabajo profesional."
                  : "Cerrada. Sin permisos de trabajo profesional."}
              </p>
            </section>
          ) : contextsOnly ? (
            <p>
              Aún no tienes una práctica preparada.{" "}
              <Link to="/profesional">Crear borrador privado</Link>.
            </p>
          ) : null}
          {profile?.state === "withdrawn" ? (
            <p>
              Tu perfil está retirado. No se puede restaurar desde esta
              pantalla.
            </p>
          ) : !contextsOnly ? (
            <form
              key={profile ? `${profile.id}-${profile.version}` : "new"}
              ref={form}
              onSubmit={save}
              className="auth-form"
              aria-busy={busy}
            >
              <div className="auth-field">
                <label htmlFor="professional-name">Nombre para mostrar</label>
                <input
                  id="professional-name"
                  name="display_name"
                  required
                  maxLength={120}
                  autoComplete="name"
                  defaultValue={profile?.fields.display_name ?? ""}
                  disabled={busy || stale || !canEdit}
                  aria-describedby="professional-help"
                />
              </div>
              <div className="auth-field">
                <label htmlFor="professional-area">
                  Área declarada (opcional)
                </label>
                <input
                  id="professional-area"
                  name="declared_area"
                  maxLength={240}
                  autoComplete="off"
                  defaultValue={profile?.fields.declared_area ?? ""}
                  disabled={busy || stale || !canEdit}
                  aria-describedby="professional-help"
                />
              </div>
              <p id="professional-help" className="note">
                Estos datos son privados y no se publican. El plazo aprobado es
                de 30 días desde la última edición real; consultar no reinicia
                el plazo. La ejecución periódica del borrado sigue pendiente.
              </p>
              <button disabled={busy || stale || !canEdit} type="submit">
                {busy ? "Guardando…" : "Guardar borrador privado"}
              </button>
            </form>
          ) : null}
          {profile?.state === "draft" &&
          practice &&
          canWithdraw &&
          !contextsOnly ? (
            <section aria-labelledby="withdraw-title">
              <h2 id="withdraw-title">Retirar perfil</h2>
              <p>
                También cerrará tu práctica en preparación. Los plazos aprobados
                son 30 días de datos desde el retiro y 90 días de historia
                mínima. El retiro es inmediato; el borrado físico no está
                confirmado.
              </p>
              {confirm ? (
                <>
                  <p>¿Retirar el perfil y cerrar la práctica?</p>
                  <button
                    ref={confirmation}
                    disabled={busy || stale}
                    type="button"
                    onClick={() =>
                      void mutate(
                        {
                          expected_version: profile.version,
                          expected_context_version: practice.version,
                        },
                        true,
                      )
                    }
                  >
                    Confirmar retiro
                  </button>
                  <button
                    className="secondary"
                    disabled={busy}
                    type="button"
                    onClick={() => setConfirm(false)}
                  >
                    Cancelar
                  </button>
                </>
              ) : (
                <button
                  className="secondary"
                  disabled={busy || stale}
                  type="button"
                  onClick={() => setConfirm(true)}
                >
                  Retirar perfil y práctica
                </button>
              )}
            </section>
          ) : null}
        </>
      ) : null}
    </AuthShell>
  );
}
