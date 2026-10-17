export type SessionView =
  | { authenticated: false }
  | {
      authenticated: true;
      user: { id: string; email: string; assurance: "aal1" | "aal2" };
    };

export type Factor = { id: string; status: "verified" | "unverified" };
export type Enrollment = {
  factor_id: string;
  totp: { secret: string; uri: string };
};

const messages: Record<string, string> = {
  AUTHENTICATION_REQUIRED: "Tu sesión terminó. Vuelve a entrar.",
  INVALID_CREDENTIALS:
    "No pudimos iniciar sesión con esos datos. Revisa tu correo y contraseña.",
  INVALID_CODE: "El código no es válido o ya venció.",
  REQUEST_FORBIDDEN: "No pudimos validar la solicitud. Inténtalo de nuevo.",
  MFA_REQUIRED: "Completa la verificación en dos pasos para continuar.",
  FEATURE_UNAVAILABLE: "Esta función aún no está disponible.",
  INVALID_REQUEST: "Revisa los datos de la solicitud.",
  RATE_LIMITED: "Espera un momento antes de volver a intentarlo.",
  AUTH_UNAVAILABLE:
    "El acceso no está disponible temporalmente. Inténtalo más tarde.",
};

export class AuthError extends Error {
  constructor(
    public readonly code: string,
    public readonly status: number,
  ) {
    super(
      Object.hasOwn(messages, code)
        ? messages[code]
        : "No pudimos completar la solicitud. Inténtalo de nuevo.",
    );
    this.name = "AuthError";
  }
}

export function authMessage(error: unknown): string {
  return error instanceof AuthError
    ? error.message
    : "No pudimos conectar. Inténtalo de nuevo.";
}

function object(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null;
}

let csrf: string | null = null;
let csrfPending: Promise<string> | null = null;

async function request(path: string, init?: RequestInit): Promise<unknown> {
  const response = await fetch(`/api/auth/${path}`, {
    ...init,
    credentials: "same-origin",
    cache: "no-store",
    referrerPolicy: "no-referrer",
    redirect: "error",
    signal: init?.signal
      ? AbortSignal.any([init.signal, AbortSignal.timeout(15000)])
      : AbortSignal.timeout(15000),
  });
  if (!response.ok) {
    const payload: unknown = await response.json().catch(() => null);
    const code =
      object(payload) &&
      object(payload.error) &&
      typeof payload.error.code === "string"
        ? payload.error.code
        : "UNEXPECTED_RESPONSE";
    if (code === "REQUEST_FORBIDDEN" || code === "AUTHENTICATION_REQUIRED")
      csrf = null;
    throw new AuthError(code, response.status);
  }
  return response.status === 204 ? null : response.json();
}

async function getCsrf(): Promise<string> {
  if (csrf) return csrf;
  if (!csrfPending) {
    csrfPending = request("csrf")
      .then((value) => {
        if (
          !object(value) ||
          typeof value.csrf_token !== "string" ||
          !value.csrf_token
        ) {
          throw new AuthError("UNEXPECTED_RESPONSE", 0);
        }
        csrf = value.csrf_token;
        return csrf;
      })
      .finally(() => {
        csrfPending = null;
      });
  }
  return csrfPending;
}

export function resetCsrf(): void {
  csrf = null;
}

export async function authPost(
  path: string,
  body: Record<string, unknown>,
  signal?: AbortSignal,
): Promise<unknown> {
  const token = await getCsrf();
  signal?.throwIfAborted();
  try {
    return await request(path, {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-CSRF-Token": token },
      body: JSON.stringify(body),
      signal,
    });
  } finally {
    if (["login", "mfa/verify", "logout", "recover/complete"].includes(path)) {
      resetCsrf();
      // A fresh bootstrap never retries the preceding mutation.
      await getCsrf().catch(() => {
        resetCsrf();
      });
    }
  }
}

export function readSession(value: unknown): SessionView {
  if (object(value) && value.authenticated === false)
    return { authenticated: false };
  if (
    object(value) &&
    value.authenticated === true &&
    object(value.user) &&
    typeof value.user.id === "string" &&
    typeof value.user.email === "string" &&
    (value.user.assurance === "aal1" || value.user.assurance === "aal2")
  ) {
    return {
      authenticated: true,
      user: {
        id: value.user.id,
        email: value.user.email,
        assurance: value.user.assurance,
      },
    };
  }
  throw new AuthError("UNEXPECTED_RESPONSE", 0);
}

export async function getSession(): Promise<SessionView> {
  return readSession(await request("session"));
}

export async function getFactors(): Promise<Factor[]> {
  const value = await request("mfa/factors");
  if (!object(value) || !Array.isArray(value.factors))
    throw new AuthError("UNEXPECTED_RESPONSE", 0);
  return value.factors.map((factor: unknown) => {
    if (
      !object(factor) ||
      typeof factor.id !== "string" ||
      (factor.status !== "verified" && factor.status !== "unverified")
    ) {
      throw new AuthError("UNEXPECTED_RESPONSE", 0);
    }
    return { id: factor.id, status: factor.status };
  });
}

export function readEnrollment(value: unknown): Enrollment {
  if (
    !object(value) ||
    typeof value.factor_id !== "string" ||
    !object(value.totp) ||
    typeof value.totp.secret !== "string" ||
    typeof value.totp.uri !== "string" ||
    !value.totp.uri.startsWith("otpauth://totp/")
  )
    throw new AuthError("UNEXPECTED_RESPONSE", 0);
  // Deliberately discard provider SVG/QR; render manual configuration as text.
  return {
    factor_id: value.factor_id,
    totp: { secret: value.totp.secret, uri: value.totp.uri },
  };
}

export function readChallenge(value: unknown): string {
  if (
    !object(value) ||
    typeof value.challenge_id !== "string" ||
    typeof value.expires_at !== "number" ||
    value.expires_at * 1000 <= Date.now()
  ) {
    throw new AuthError("INVALID_CODE", 401);
  }
  return value.challenge_id;
}

export function readAccepted(value: unknown): void {
  if (!object(value) || value.accepted !== true)
    throw new AuthError("UNEXPECTED_RESPONSE", 0);
}
