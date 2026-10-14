import { useCallback, useEffect, useRef, useState } from "react";
import { Link, useNavigate } from "react-router";
import { AuthForm, AuthShell, codeField } from "../components/auth-form";
import {
  AuthError,
  authMessage,
  authPost,
  type Enrollment,
  type Factor,
  getFactors,
  getSession,
  readChallenge,
  readEnrollment,
  readSession,
  type SessionView,
} from "../lib/auth";

export function meta() {
  return [
    { title: "Mi cuenta | Legalia" },
    { name: "robots", content: "noindex, nofollow" },
    { name: "referrer", content: "no-referrer" },
  ];
}

export default function Account() {
  const navigate = useNavigate();
  const alive = useRef(false);
  const locked = useRef(false);
  const sessionRequest = useRef(0);
  const globalButton = useRef<HTMLButtonElement>(null);
  const confirmButton = useRef<HTMLButtonElement>(null);
  const statusRef = useRef<HTMLParagraphElement>(null);
  const [session, setSession] = useState<SessionView | null>(null);
  const [factors, setFactors] = useState<Factor[] | null>(null);
  const [factorId, setFactorId] = useState("");
  const [enrollment, setEnrollment] = useState<Enrollment | null>(null);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [globalConfirm, setGlobalConfirm] = useState(false);

  const clearPrivate = useCallback(() => {
    setSession(null);
    setEnrollment(null);
    setFactors(null);
    setFactorId("");
  }, []);

  const loadFactors = useCallback(async () => {
    const result = await getFactors();
    if (alive.current) {
      setFactors(result);
      setFactorId(
        result.find((factor) => factor.status === "verified")?.id ??
          result[0]?.id ??
          "",
      );
    }
  }, []);

  const loadSession = useCallback(async () => {
    const generation = ++sessionRequest.current;
    setError("");
    setSession(null);
    setEnrollment(null);
    setFactors(null);
    try {
      const result = await getSession();
      if (!alive.current || sessionRequest.current !== generation) return;
      if (!result.authenticated) {
        await navigate("/acceso", { replace: true });
        return;
      }
      setSession(result);
      await loadFactors();
    } catch (failure) {
      if (alive.current && sessionRequest.current === generation) {
        if (
          failure instanceof AuthError &&
          failure.code === "AUTHENTICATION_REQUIRED"
        )
          clearPrivate();
        setError(authMessage(failure));
      }
    }
  }, [clearPrivate, loadFactors, navigate]);

  useEffect(() => {
    alive.current = true;
    void loadSession();
    const conceal = () => {
      if (document.visibilityState === "hidden") setEnrollment(null);
    };
    const hidePrivate = () => {
      sessionRequest.current++;
      setSession(null);
      setEnrollment(null);
      setFactors(null);
      setFactorId("");
    };
    const restore = (event: PageTransitionEvent) => {
      if (event.persisted) void loadSession();
    };
    document.addEventListener("visibilitychange", conceal);
    window.addEventListener("pagehide", hidePrivate);
    window.addEventListener("pageshow", restore);
    return () => {
      alive.current = false;
      sessionRequest.current++;
      document.removeEventListener("visibilitychange", conceal);
      window.removeEventListener("pagehide", hidePrivate);
      window.removeEventListener("pageshow", restore);
    };
  }, [loadSession]);

  useEffect(() => {
    if (globalConfirm) confirmButton.current?.focus();
  }, [globalConfirm]);

  async function handleAction(action: () => Promise<void>) {
    if (locked.current) return;
    locked.current = true;
    setBusy(true);
    setError("");
    setMessage("");
    try {
      await action();
    } catch (failure) {
      if (alive.current) {
        setEnrollment(null);
        setError(authMessage(failure));
        if (
          failure instanceof AuthError &&
          failure.code === "AUTHENTICATION_REQUIRED"
        )
          await loadSession();
      }
    } finally {
      locked.current = false;
      if (alive.current) {
        setBusy(false);
        requestAnimationFrame(() => statusRef.current?.focus());
      }
    }
  }

  async function logout(scope: "local" | "global") {
    await handleAction(async () => {
      try {
        await authPost("logout", { scope });
        if (alive.current) {
          setSession(null);
          setEnrollment(null);
          setFactors(null);
          setFactorId("");
          setMessage(
            scope === "global"
              ? "Sesiones cerradas en todos los dispositivos."
              : "Sesión cerrada.",
          );
          setGlobalConfirm(false);
        }
      } catch (failure) {
        if (alive.current) {
          // A provider failure can occur after the API has revoked this browser.
          setSession(null);
          setEnrollment(null);
          setFactors(null);
          setFactorId("");
          setGlobalConfirm(false);
          setError(
            failure instanceof AuthError && failure.status === 503
              ? "No pudimos confirmar el cierre completo; la sesión de este dispositivo puede haberse retirado. Se ocultó la información de esta pantalla. Vuelve a entrar para gestionar tus sesiones."
              : "No pudimos confirmar el cierre. Se ocultó la información de esta pantalla; vuelve a entrar para comprobar tu sesión.",
          );
        }
      }
    });
  }

  return (
    <AuthShell
      title="Mi cuenta"
      description="Consulta tu sesión y la verificación en dos pasos."
    >
      {session?.authenticated ? (
        <>
          <p>
            <strong>Cuenta:</strong> {session.user.email}
          </p>
          <p>Sesión activa.</p>
          <section className="auth-section" aria-labelledby="mfa-title">
            <h2 id="mfa-title">Verificación en dos pasos</h2>
            <p>
              {session.user.assurance === "aal2"
                ? "Verificación adicional completada para esta sesión."
                : "Completa este paso antes de realizar acciones profesionales privadas."}
            </p>
            <p className="note">
              La verificación en dos pasos protege tu cuenta. El alta
              profesional y los permisos se revisan por separado.
            </p>
            {factors === null ? (
              <button
                className="secondary"
                disabled={busy}
                onClick={() => void handleAction(loadFactors)}
              >
                Cargar métodos de verificación
              </button>
            ) : null}
            {factors && factors.length > 0 ? (
              <>
                <label htmlFor="factor">Aplicación autenticadora</label>
                <select
                  id="factor"
                  value={factorId}
                  disabled={busy}
                  onChange={(event) => {
                    setFactorId(event.target.value);
                    setEnrollment(null);
                  }}
                >
                  {factors.map((factor, index) => (
                    <option value={factor.id} key={factor.id}>
                      Método {index + 1} —{" "}
                      {factor.status === "verified"
                        ? "configurado"
                        : "pendiente de verificación"}
                    </option>
                  ))}
                </select>
              </>
            ) : null}
            {enrollment ? (
              <div className="auth-setup">
                <h3>Configura tu aplicación autenticadora</h3>
                <p>
                  Introduce esta clave en tu aplicación y selecciona códigos
                  basados en tiempo. Guárdala antes de verificar: se ocultará al
                  terminar o abandonar esta pantalla.
                </p>
                <p>
                  <strong>Clave de configuración:</strong>
                </p>
                <code className="auth-secret">{enrollment.totp.secret}</code>
                <details>
                  <summary>Configuración manual alternativa</summary>
                  <p className="note">
                    Si tu aplicación permite importar una dirección de
                    configuración, introdúcela directamente en la aplicación
                    autenticadora.
                  </p>
                  <code className="auth-secret">{enrollment.totp.uri}</code>
                </details>
                <button
                  className="secondary"
                  onClick={() => setEnrollment(null)}
                >
                  Ocultar configuración
                </button>
              </div>
            ) : null}
            {factors?.length === 0 ? (
              <button
                disabled={busy}
                onClick={() =>
                  void handleAction(async () => {
                    const setup = readEnrollment(
                      await authPost("mfa/enroll", {}),
                    );
                    if (
                      alive.current &&
                      document.visibilityState === "visible"
                    ) {
                      setEnrollment(setup);
                      setFactorId(setup.factor_id);
                      setFactors([
                        { id: setup.factor_id, status: "unverified" },
                      ]);
                    }
                  })
                }
              >
                Configurar aplicación autenticadora
              </button>
            ) : null}
            {factorId ? (
              <AuthForm
                fields={[codeField]}
                submitLabel="Verificar código"
                successMessage="Verificación adicional completada."
                onSubmit={async (values, signal) => {
                  if (locked.current)
                    throw new AuthError("REQUEST_FORBIDDEN", 403);
                  locked.current = true;
                  setBusy(true);
                  try {
                    const challenge = readChallenge(
                      await authPost(
                        "mfa/challenge",
                        { factor_id: factorId },
                        signal,
                      ),
                    );
                    const elevated = readSession(
                      await authPost(
                        "mfa/verify",
                        {
                          factor_id: factorId,
                          challenge_id: challenge,
                          code: values.code,
                        },
                        signal,
                      ),
                    );
                    if (
                      !elevated.authenticated ||
                      elevated.user.assurance !== "aal2" ||
                      elevated.user.id !== session.user.id
                    )
                      throw new AuthError("UNEXPECTED_RESPONSE", 0);
                    if (alive.current) {
                      setSession(elevated);
                      await loadFactors();
                    }
                  } catch (failure) {
                    if (
                      alive.current &&
                      failure instanceof AuthError &&
                      failure.code === "AUTHENTICATION_REQUIRED"
                    ) {
                      clearPrivate();
                      setError(authMessage(failure));
                    }
                    throw failure;
                  } finally {
                    locked.current = false;
                    if (alive.current) {
                      setBusy(false);
                      setEnrollment(null);
                    }
                  }
                }}
              />
            ) : null}
            <p className="note">
              La recuperación y retirada de métodos de verificación aún no están
              disponibles.
            </p>
          </section>
          <section className="auth-section" aria-labelledby="logout-title">
            <h2 id="logout-title">Cerrar sesión</h2>
            <div className="auth-actions">
              <button disabled={busy} onClick={() => void logout("local")}>
                Cerrar sesión en este dispositivo
              </button>
              <button
                ref={globalButton}
                className="secondary"
                disabled={busy}
                onClick={() => setGlobalConfirm(true)}
              >
                Cerrar sesión en todos los dispositivos
              </button>
            </div>
            {globalConfirm ? (
              <div
                className="auth-confirm"
                role="group"
                aria-label="Confirmar cierre en todos los dispositivos"
              >
                <p>
                  Se cerrarán las sesiones de esta cuenta en tus dispositivos.
                </p>
                <button
                  ref={confirmButton}
                  disabled={busy}
                  onClick={() => void logout("global")}
                >
                  Cerrar todas
                </button>{" "}
                <button
                  className="secondary"
                  disabled={busy}
                  onClick={() => {
                    setGlobalConfirm(false);
                    globalButton.current?.focus();
                  }}
                >
                  Cancelar
                </button>
              </div>
            ) : null}
          </section>
        </>
      ) : !error && !message ? (
        <p role="status">Comprobando tu sesión…</p>
      ) : null}
      <p
        tabIndex={-1}
        ref={statusRef}
        className={error ? "auth-message error" : "auth-message"}
        role={error ? "alert" : "status"}
      >
        {error || message}
      </p>
      {error && !session ? (
        <button
          className="secondary"
          disabled={busy}
          onClick={() => void loadSession()}
        >
          Comprobar sesión de nuevo
        </button>
      ) : null}
      {!session && (error || message) ? (
        <p>
          <Link to="/acceso">Volver a acceso</Link>
        </p>
      ) : null}
    </AuthShell>
  );
}
