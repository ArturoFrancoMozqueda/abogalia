/** Static build plus same-origin API gateway. No credentials or logging. */
export const APPROVED_API_ORIGINS: readonly string[] = Object.freeze([]);

export type WorkerEnv = {
  ASSETS: { fetch(request: Request): Promise<Response> };
  LEGALIA_API_ORIGIN?: string;
};
type UpstreamInit = RequestInit & {
  cf: { cacheTtl: number; cacheEverything: boolean };
};
type UpstreamFetch = (
  request: Request,
  init: UpstreamInit,
) => Promise<Response>;
const PRIVATE_ROUTES = new Set([
  "/acceso",
  "/registro",
  "/recuperar",
  "/cuenta",
  "/profesional",
  "/profesional/contextos",
]);
const NO_STORE = "private, no-store";
const REQUEST_HEADERS = [
  "accept",
  "content-type",
  "origin",
  "cookie",
  "x-csrf-token",
  "sec-fetch-site",
  "sec-fetch-mode",
  "sec-fetch-dest",
];
const HOP_HEADERS = [
  "connection",
  "keep-alive",
  "proxy-authenticate",
  "proxy-authorization",
  "te",
  "trailer",
  "transfer-encoding",
  "upgrade",
];
function privateHeaders(headers = new Headers()): Headers {
  headers.set("Cache-Control", NO_STORE);
  headers.set("CDN-Cache-Control", "no-store");
  headers.set("Cloudflare-CDN-Cache-Control", "no-store");
  headers.set("Pragma", "no-cache");
  headers.set("X-Content-Type-Options", "nosniff");
  headers.set("Referrer-Policy", "no-referrer");
  return headers;
}
function unavailable(status = 503): Response {
  return new Response(
    JSON.stringify({
      error: {
        code: status === 403 ? "REQUEST_FORBIDDEN" : "GATEWAY_UNAVAILABLE",
        message:
          status === 403
            ? "No pudimos validar la solicitud."
            : "La operación no está disponible temporalmente.",
      },
    }),
    {
      status,
      headers: privateHeaders(
        new Headers({ "Content-Type": "application/json" }),
      ),
    },
  );
}
function approvedOrigin(
  value: unknown,
  approved: readonly string[],
): string | null {
  if (typeof value !== "string" || !approved.includes(value)) return null;
  try {
    const url = new URL(value);
    if (
      url.protocol !== "https:" ||
      url.username ||
      url.password ||
      url.port ||
      url.origin !== value ||
      !/^[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.fly\.dev$/.test(url.hostname)
    )
      return null;
    return url.origin;
  } catch {
    return null;
  }
}

// Explicit injection is for synthetic tests; the default export uses the empty
// reviewed list above until A0 records the actually provisioned Legalia origin.
export function createWorker(
  approved: readonly string[] = APPROVED_API_ORIGINS,
  upstreamFetch: UpstreamFetch = fetch,
) {
  const origins = Object.freeze([...approved]);
  return {
    async fetch(request: Request, env: WorkerEnv): Promise<Response> {
      const incoming = new URL(request.url);
      const api =
        incoming.pathname === "/api" || incoming.pathname.startsWith("/api/");
      if (api) {
        if (request.headers.has("authorization")) return unavailable(403);
        const origin = approvedOrigin(env.LEGALIA_API_ORIGIN, origins);
        if (!origin || incoming.protocol !== "https:") return unavailable();
        const headers = new Headers();
        for (const name of REQUEST_HEADERS) {
          const value = request.headers.get(name);
          if (value !== null) headers.set(name, value);
        }
        // Assignment preserves path/query without letting // or query choose a host.
        const target = new URL(origin);
        target.pathname = incoming.pathname;
        target.search = incoming.search;
        const init: RequestInit & { duplex?: "half" } = {
          method: request.method,
          headers,
          redirect: "manual",
          signal: AbortSignal.any([request.signal, AbortSignal.timeout(15000)]),
        };
        if (request.method !== "GET" && request.method !== "HEAD") {
          init.body = request.body;
          init.duplex = "half";
        }
        try {
          init.signal?.throwIfAborted();
          const response = await upstreamFetch(new Request(target, init), {
            redirect: "manual",
            cache: "no-store",
            cf: { cacheTtl: 0, cacheEverything: false },
          });
          // Neither follow upstream redirects with credentials nor leak Location to browser.
          if (response.status >= 300 && response.status < 400) {
            await response.body?.cancel().catch(() => {});
            return unavailable(502);
          }
          const outgoing = privateHeaders(new Headers(response.headers));
          for (const name of HOP_HEADERS) outgoing.delete(name);
          for (const name of [...outgoing.keys()])
            if (name.startsWith("access-control-")) outgoing.delete(name);
          outgoing.delete("Location");
          outgoing.delete("Content-Location");
          return new Response(response.body, {
            status: response.status,
            headers: outgoing,
          });
        } catch {
          return unavailable(502);
        }
      }
      if (request.method !== "GET" && request.method !== "HEAD")
        return new Response(null, {
          status: 405,
          headers: { Allow: "GET, HEAD", "Cache-Control": NO_STORE },
        });
      const shell = PRIVATE_ROUTES.has(incoming.pathname);
      const asset = new URL(incoming.origin);
      asset.pathname = shell
        ? "/__spa-fallback.html"
        : incoming.pathname === "/"
          ? "/index.html"
          : incoming.pathname;
      try {
        // Do not forward cookies, Authorization, query or identity headers to assets.
        const response = await env.ASSETS.fetch(
          new Request(asset, { method: request.method }),
        );
        const headers = shell
          ? privateHeaders(new Headers(response.headers))
          : new Headers(response.headers);
        headers.set("X-Content-Type-Options", "nosniff");
        headers.set("Referrer-Policy", "no-referrer");
        return new Response(response.body, {
          status: response.status,
          headers,
        });
      } catch {
        return unavailable();
      }
    },
  };
}
export default createWorker();
