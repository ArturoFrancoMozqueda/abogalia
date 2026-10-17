import { AuthError, resetCsrf } from "./auth";

export type DraftFields = {
  display_name: string;
  declared_area: string | null;
};
export type PrivateProfile = {
  id: string;
  version: number;
  state: "draft" | "withdrawn";
  fields: DraftFields;
  publication: "private";
  review: null;
  allowed_actions: string[];
};
export type PrivatePractice = {
  id: string;
  version: number;
  kind: "practice";
  title: string;
  state: "preparing" | "closed";
  capabilities: string[];
  allowed_actions: string[];
};
export type PrivateDraft = {
  profile: PrivateProfile | null;
  practice_context: PrivatePractice | null;
};

function object(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null;
}
function strings(value: unknown): value is string[] {
  return (
    Array.isArray(value) && value.every((entry) => typeof entry === "string")
  );
}
function version(value: unknown): value is number {
  return typeof value === "number" && Number.isInteger(value) && value > 0;
}
export function readPrivateDraft(value: unknown): PrivateDraft {
  if (!object(value)) throw new AuthError("UNEXPECTED_RESPONSE", 0);
  if (value.profile === null && value.practice_context === null)
    return { profile: null, practice_context: null };
  const p = value.profile;
  const c = value.practice_context;
  if (
    !object(p) ||
    !object(c) ||
    typeof p.id !== "string" ||
    !version(p.version) ||
    (p.state !== "draft" && p.state !== "withdrawn") ||
    !object(p.fields) ||
    typeof p.fields.display_name !== "string" ||
    (p.fields.declared_area !== null &&
      typeof p.fields.declared_area !== "string") ||
    p.publication !== "private" ||
    p.review !== null ||
    !strings(p.allowed_actions) ||
    typeof c.id !== "string" ||
    !version(c.version) ||
    c.kind !== "practice" ||
    typeof c.title !== "string" ||
    !strings(c.capabilities) ||
    c.capabilities.length !== 0 ||
    !strings(c.allowed_actions) ||
    !(
      (p.state === "draft" && c.state === "preparing") ||
      (p.state === "withdrawn" && c.state === "closed")
    )
  )
    throw new AuthError("UNEXPECTED_RESPONSE", 0);
  return {
    profile: {
      id: p.id,
      version: p.version,
      state: p.state,
      fields: {
        display_name: p.fields.display_name,
        declared_area: p.fields.declared_area,
      },
      publication: "private",
      review: null,
      allowed_actions: p.allowed_actions,
    },
    practice_context: {
      id: c.id,
      version: c.version,
      kind: "practice",
      title: c.title,
      state: c.state,
      capabilities: [],
      allowed_actions: c.allowed_actions,
    },
  };
}
export function professionalMessage(error: unknown): string {
  const messages: Record<string, string> = {
    VERSION_CONFLICT: "La información cambió. Actualiza antes de continuar.",
    STATE_CONFLICT:
      "Esta acción no está disponible en el estado actual. Actualiza antes de continuar.",
    RESOURCE_UNAVAILABLE: "La información solicitada no está disponible.",
    PROFESSIONAL_UNAVAILABLE: "La operación no está disponible temporalmente.",
    MFA_REQUIRED:
      "Completa la verificación en dos pasos en Mi cuenta para continuar.",
    AUTHENTICATION_REQUIRED: "Tu sesión terminó. Vuelve a entrar.",
    INVALID_REQUEST: "Revisa los datos de la solicitud.",
    REQUEST_FORBIDDEN:
      "No pudimos validar la solicitud. Actualiza antes de continuar.",
    FEATURE_UNAVAILABLE: "Esta función aún no está disponible.",
    RATE_LIMITED: "Espera un momento antes de volver a intentarlo.",
  };
  return error instanceof AuthError
    ? Object.hasOwn(messages, error.code)
      ? messages[error.code]
      : "No pudimos completar la solicitud. Actualiza antes de continuar."
    : "No pudimos confirmar el resultado. Actualiza antes de continuar.";
}
async function json(response: Response): Promise<unknown> {
  const value: unknown = await response.json().catch(() => null);
  if (!response.ok) {
    if (response.status === 401 || response.status === 403) resetCsrf();
    throw new AuthError(
      object(value) &&
        object(value.error) &&
        typeof value.error.code === "string"
        ? value.error.code
        : "UNEXPECTED_RESPONSE",
      response.status,
    );
  }
  return value;
}
export async function requestPrivateDraft(
  signal: AbortSignal,
  method: "GET" | "POST" | "PATCH" = "GET",
  body?: Record<string, unknown>,
  withdraw = false,
): Promise<PrivateDraft> {
  const headers: Record<string, string> = {};
  const options = {
    credentials: "same-origin",
    cache: "no-store",
    redirect: "error",
    referrerPolicy: "no-referrer",
  } as const;
  const bounded = AbortSignal.any([signal, AbortSignal.timeout(15000)]);
  if (method !== "GET") {
    const csrf = await json(
      await fetch("/api/auth/csrf", { ...options, signal: bounded }),
    );
    if (
      !object(csrf) ||
      typeof csrf.csrf_token !== "string" ||
      !csrf.csrf_token
    )
      throw new AuthError("UNEXPECTED_RESPONSE", 0);
    headers["X-CSRF-Token"] = csrf.csrf_token;
    headers["Content-Type"] = "application/json";
  }
  signal.throwIfAborted();
  return readPrivateDraft(
    await json(
      await fetch(`/api/professional/profile${withdraw ? "/withdraw" : ""}`, {
        ...options,
        signal: bounded,
        method,
        headers,
        ...(body ? { body: JSON.stringify(body) } : {}),
      }),
    ),
  );
}
