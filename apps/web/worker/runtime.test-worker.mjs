/** workerd-only regression tests; loopback fixture, no provider or user data. */
import { createWorker } from "./index.ts";

const WEB = "https://synthetic.invalid";
const API = "https://synthetic.fly.dev";
function require(value) {
  if (!value) throw new Error("Synthetic assertion failed");
}
function privateResponse(response) {
  require(response.headers.get("Cache-Control") === "private, no-store");
  require(response.headers.get("Cloudflare-CDN-Cache-Control") === "no-store");
}
export default {
  async fetch(request, bindings) {
    if (new URL(request.url).pathname === "/ready")
      return new Response("ready");
    const passed = [];
    const nativeFetch = async (req, init) => {
      const target = new URL(req.url);
      require(target.origin === API);
      // Preserve actual fetch options: workerd must reject invalid cache settings.
      return fetch(
        new Request(bindings.FIXTURE_ORIGIN + target.pathname, req),
        init,
      );
    };
    const worker = createWorker([API], nativeFetch);
    const env = {
      LEGALIA_API_ORIGIN: API,
      ASSETS: {
        fetch: async (req) => {
          require([...req.headers].length === 0);
          require(new URL(req.url).search === "");
          return new Response("synthetic shell", {
            status:
              new URL(req.url).pathname === "/__spa-fallback.html" ? 200 : 404,
          });
        },
      },
    };
    const call = (path, init) =>
      worker.fetch(new Request(WEB + path, init), env);
    const check = async (name, test) => {
      await test();
      passed.push(name);
    };
    try {
      await check("native-fetch-cache-contract", async () => {
        const response = await call("/api/health");
        require(response.status === 200);
        privateResponse(response);
        require((await response.json()).ok === true);
      });
      await check("stream-and-header-boundary", async () => {
        const response = await call("/api/echo", {
          method: "POST",
          body: "PUBLIC_SYNTHETIC_BODY",
          headers: {
            "Content-Type": "application/json",
            Cookie: "synthetic=PUBLIC_FIXTURE",
            Origin: WEB,
            "X-CSRF-Token": "PUBLIC_FIXTURE",
            "X-Forwarded-Host": "untrusted.invalid",
          },
        });
        require(response.status === 200);
        const body = await response.json();
        require(
          body.body &&
            body.cookie &&
            body.csrf &&
            body.origin &&
            body.noForwarded,
        );
        privateResponse(response);
      });
      await check("separate-set-cookie", async () => {
        const response = await call("/api/cookies");
        require(response.headers.getSetCookie().length === 2);
        require(
          response.headers.getSetCookie().some((v) => v.includes("Expires=")),
        );
        require(response.headers.get("Access-Control-Allow-Origin") === null);
        privateResponse(response);
      });
      await check("redirect-fails-closed", async () => {
        const response = await call("/api/redirect");
        require(response.status === 502 && !response.headers.has("Location"));
        privateResponse(response);
      });
      await check("authorization-rejected", async () => {
        for (const value of ["", "PUBLIC_SYNTHETIC"]) {
          const response = await call("/api/health", {
            headers: { Authorization: value },
          });
          require(response.status === 403);
        }
      });
      await check("private-shell-excludes-credentials", async () => {
        const response = await call("/registro?synthetic=value", {
          headers: {
            Cookie: "PUBLIC_FIXTURE",
            Authorization: "PUBLIC_FIXTURE",
          },
        });
        require(response.status === 200);
        privateResponse(response);
        require((await response.text()) === "synthetic shell");
      });
      await check("unknown-route-and-mutation", async () => {
        require((await call("/unknown")).status === 404);
        require(
          (await call("/registro", { method: "POST", body: "{}" })).status ===
            405,
        );
      });
      await check("unapproved-origin", async () => {
        require(
          (
            await worker.fetch(new Request(WEB + "/api/health"), {
              ...env,
              LEGALIA_API_ORIGIN: "https://unapproved.fly.dev",
            })
          ).status === 503,
        );
      });
      await check("cancelled-request", async () => {
        const controller = new AbortController();
        controller.abort();
        require(
          (await call("/api/health", { signal: controller.signal })).status ===
            502,
        );
      });
      return Response.json({ passed: passed.length, failed: 0 });
    } catch {
      return Response.json(
        { passed: passed.length, failed: 1 },
        { status: 500 },
      );
    }
  },
};
