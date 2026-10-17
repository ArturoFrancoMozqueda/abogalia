/** Native Node 24 tests: synthetic HTTP/ASSETS only, never network or env files. */
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";
import worker, { APPROVED_API_ORIGINS, createWorker } from "./index.ts";

const WEB = "https://legalia-public-synthetic.example.invalid";
const API = "https://legalia-public-synthetic.fly.dev";
const noAssets = {
  fetch: async () => {
    throw new Error("Assets must not be reached");
  },
};
const environment = { ASSETS: noAssets, LEGALIA_API_ORIGIN: API };
const request = (path, options) => new Request(WEB + path, options);
function noStore(response) {
  assert.equal(response.headers.get("Cache-Control"), "private, no-store");
  assert.equal(response.headers.get("CDN-Cache-Control"), "no-store");
  assert.equal(
    response.headers.get("Cloudflare-CDN-Cache-Control"),
    "no-store",
  );
}

test("production allowlist confines requests to the provisioned Legalia API", async () => {
  assert.deepEqual(APPROVED_API_ORIGINS, ["https://legalia-api.fly.dev"]);
  const response = await worker.fetch(
    request("/api/auth/session"),
    environment,
  );
  assert.equal(response.status, 503);
  noStore(response);
});
for (const value of [
  "",
  "https://different.fly.dev",
  "http://legalia-public-synthetic.fly.dev",
  "https://legalia-public-synthetic.fly.dev.evil.invalid",
  "https://user@legalia-public-synthetic.fly.dev",
  API + "/",
  API + ":443",
  API + "/path",
  API + "?target=https://evil.invalid",
  API + "#x",
]) {
  test(
    "unapproved/noncanonical backend fails before any fetch: case " +
      (value.length || 0),
    async () => {
      let calls = 0;
      const target = createWorker([API], async () => {
        calls++;
        throw new Error();
      });
      assert.equal(
        (
          await target.fetch(request("/api/auth/session"), {
            ...environment,
            LEGALIA_API_ORIGIN: value,
          })
        ).status,
        503,
      );
      assert.equal(calls, 0);
    },
  );
}

test("http frontend API request fails closed", async () => {
  let calls = 0;
  const target = createWorker([API], async () => {
    calls++;
    throw new Error();
  });
  assert.equal(
    (
      await target.fetch(
        new Request("http://public-synthetic.invalid/api/auth/session"),
        environment,
      )
    ).status,
    503,
  );
  assert.equal(calls, 0);
});

test("API navigation never falls back to assets and preserves API status/body", async () => {
  const target = createWorker(
    [API],
    async () =>
      new Response('{"error":{"code":"RESOURCE_UNAVAILABLE"}}', {
        status: 404,
        headers: {
          "Content-Type": "application/json",
          "Cache-Control": "public, max-age=86400",
        },
      }),
  );
  const result = await target.fetch(
    request("/api/professional/missing", {
      headers: { "Sec-Fetch-Mode": "navigate" },
    }),
    environment,
  );
  assert.equal(result.status, 404);
  assert.equal(result.headers.get("Content-Type"), "application/json");
  noStore(result);
  assert.equal((await result.json()).error.code, "RESOURCE_UNAVAILABLE");
});

test("fixed host/path/query and original Origin/cookie/CSRF/SecFetch survive; spoofed identity headers do not", async () => {
  let seen;
  const target = createWorker([API], async (upstream, options) => {
    seen = upstream;
    assert.equal(options.redirect, "manual");
    assert.equal(options.cache, "no-store");
    // Workers rejects a cf.cacheTtl override when cache is no-store.
    assert.equal(options.cf, undefined);
    assert.equal(upstream.redirect, "manual");
    assert.equal(await upstream.text(), '{"public_synthetic":true}');
    return new Response('{"accepted":true}', {
      headers: { "Content-Type": "application/json" },
    });
  });
  const original = request("/api/auth/login?target=https://evil.invalid", {
    method: "POST",
    body: '{"public_synthetic":true}',
    headers: {
      Origin: WEB,
      Cookie: "__Host-abogalia_session=PUBLIC_SYNTHETIC_NOT_CREDENTIAL",
      "X-CSRF-Token": "PUBLIC_SYNTHETIC_NOT_CREDENTIAL",
      "Content-Type": "application/json",
      "Sec-Fetch-Site": "same-origin",
      "Sec-Fetch-Mode": "cors",
      "Sec-Fetch-Dest": "empty",
      Forwarded: "for=public-synthetic;host=evil.invalid",
      "X-Forwarded-Host": "evil.invalid",
      "X-Forwarded-Proto": "http",
      "X-Forwarded-For": "192.0.2.5",
      "X-Real-IP": "192.0.2.5",
      "Fly-Client-IP": "192.0.2.5",
      "CF-Connecting-IP": "192.0.2.5",
      "True-Client-IP": "192.0.2.5",
      Host: "evil.invalid",
      Connection: "keep-alive",
    },
  });
  assert.equal((await target.fetch(original, environment)).status, 200);
  const url = new URL(seen.url);
  assert.equal(url.origin, API);
  assert.equal(url.pathname, "/api/auth/login");
  assert.equal(url.searchParams.get("target"), "https://evil.invalid");
  for (const header of [
    "origin",
    "cookie",
    "x-csrf-token",
    "sec-fetch-site",
    "sec-fetch-mode",
    "sec-fetch-dest",
  ])
    assert.equal(seen.headers.get(header), original.headers.get(header));
  for (const header of [
    "forwarded",
    "x-forwarded-for",
    "x-forwarded-host",
    "x-forwarded-proto",
    "x-real-ip",
    "fly-client-ip",
    "cf-connecting-ip",
    "true-client-ip",
    "authorization",
    "host",
    "connection",
  ])
    assert.equal(seen.headers.has(header), false);
});

test("no Origin or SecFetch is invented when absent", async () => {
  const target = createWorker([API], async (upstream) => {
    assert.equal(upstream.headers.has("origin"), false);
    assert.equal(upstream.headers.has("sec-fetch-site"), false);
    return new Response(null, { status: 204 });
  });
  assert.equal(
    (await target.fetch(request("/api/auth/csrf"), environment)).status,
    204,
  );
});

test("two Set-Cookie lines including expiry comma and __Host attributes preserved independently", async () => {
  const headers = new Headers();
  headers.append(
    "Set-Cookie",
    "__Host-abogalia_session=PUBLIC_SYNTHETIC; Path=/; Secure; HttpOnly; SameSite=Lax",
  );
  headers.append(
    "Set-Cookie",
    "__Host-abogalia_csrf=; Expires=Thu, 01 Jan 1970 00:00:00 GMT; Path=/; Secure; SameSite=Lax",
  );
  headers.set("Connection", "keep-alive");
  headers.set("Access-Control-Allow-Origin", "*");
  const target = createWorker(
    [API],
    async () => new Response("{}", { headers }),
  );
  const result = await target.fetch(request("/api/auth/logout"), environment);
  assert.deepEqual(result.headers.getSetCookie(), headers.getSetCookie());
  assert.equal(result.headers.has("Connection"), false);
  assert.equal(result.headers.has("Access-Control-Allow-Origin"), false);
  noStore(result);
});

for (const status of [301, 302, 303, 307, 308]) {
  test(
    "redirect rejected without next fetch or Location/Set-Cookie leakage: " +
      status,
    async () => {
      let calls = 0;
      const target = createWorker([API], async () => {
        calls++;
        return new Response(null, {
          status,
          headers: {
            Location: "https://evil.invalid",
            "Set-Cookie": "PUBLIC_SYNTHETIC",
          },
        });
      });
      const result = await target.fetch(
        request("/api/auth/session"),
        environment,
      );
      assert.equal(result.status, 502);
      assert.equal(calls, 1);
      assert.equal(result.headers.has("Location"), false);
      assert.equal(result.headers.has("Set-Cookie"), false);
      noStore(result);
    },
  );
}

test("upstream network failure is fixed redacted JSON without retry", async () => {
  let calls = 0;
  const target = createWorker([API], async () => {
    calls++;
    throw new Error("PUBLIC_SYNTHETIC_RAW_DETAIL");
  });
  const result = await target.fetch(request("/api/auth/session"), environment);
  assert.equal(result.status, 502);
  assert.equal(calls, 1);
  noStore(result);
  assert.equal((await result.text()).includes("RAW_DETAIL"), false);
});

for (const [path, asset, privateRoute] of [
  ["/", "/index.html", false],
  ["/cuenta", "/__spa-fallback.html", true],
  ["/profesional/contextos", "/__spa-fallback.html", true],
  ["/assets/public-synthetic.js", "/assets/public-synthetic.js", false],
]) {
  test(
    "static route uses correct build asset without credentials: " + path,
    async () => {
      const target = createWorker();
      const result = await target.fetch(
        request(path + "?private=PUBLIC_SYNTHETIC", {
          headers: {
            Cookie: "PUBLIC_SYNTHETIC",
            Authorization: "PUBLIC_SYNTHETIC",
          },
        }),
        {
          ASSETS: {
            fetch: async (assetRequest) => {
              assert.equal(new URL(assetRequest.url).pathname, asset);
              assert.equal(new URL(assetRequest.url).search, "");
              assert.equal([...assetRequest.headers].length, 0);
              return new Response("PUBLIC SYNTHETIC STATIC", {
                headers: { "Content-Type": "text/html" },
              });
            },
          },
        },
      );
      assert.equal(result.status, 200);
      if (privateRoute) noStore(result);
    },
  );
}

test("unknown route stays asset404 and static mutation does not reach binding", async () => {
  let calls = 0;
  const env = {
    ASSETS: {
      fetch: async () => {
        calls++;
        return new Response(null, { status: 404 });
      },
    },
  };
  assert.equal((await worker.fetch(request("/missing"), env)).status, 404);
  assert.equal(
    (
      await worker.fetch(
        request("/cuenta", { method: "POST", body: "PUBLIC SYNTHETIC" }),
        env,
      )
    ).status,
    405,
  );
  assert.equal(calls, 1);
});

test("versioned Wrangler template bypasses only public assets, preserves private routing and closed destinations", () => {
  const source = readFileSync(
    new URL("../wrangler.jsonc", import.meta.url),
    "utf8",
  );
  const config = JSON.parse(source.replace(/^\s*\/\/.*$/gm, ""));
  assert.deepEqual(config.assets, {
    directory: "build/client",
    binding: "ASSETS",
    run_worker_first: ["/*", "!/assets/*"],
    html_handling: "none",
    not_found_handling: "none",
  });
  assert.equal(config.workers_dev, false);
  assert.equal(config.preview_urls, false);
  assert.equal(config.observability.enabled, false);
  assert.equal(config.vars.LEGALIA_API_ORIGIN, "");
  assert.equal(Object.hasOwn(config, "account_id"), false);
});

test("cancelled API request cannot reach upstream or assets", async () => {
  const controller = new AbortController();
  controller.abort();
  let calls = 0;
  const target = createWorker([API], async () => {
    calls++;
    throw new Error();
  });
  const result = await target.fetch(
    request("/api/auth/session", { signal: controller.signal }),
    environment,
  );
  assert.equal(result.status, 502);
  assert.equal(calls, 0);
  noStore(result);
});

test("presence of Authorization is rejected before fetch even with valid browser cookie and CSRF", async () => {
  let calls = 0;
  const target = createWorker([API], async () => {
    calls++;
    return new Response("{}");
  });
  for (const value of ["PUBLIC_SYNTHETIC_NOT_CREDENTIAL", ""]) {
    const result = await target.fetch(
      request("/api/auth/login", {
        method: "POST",
        body: "{}",
        headers: {
          Authorization: value,
          Cookie: "__Host-abogalia_session=PUBLIC_SYNTHETIC_NOT_CREDENTIAL",
          "X-CSRF-Token": "PUBLIC_SYNTHETIC_NOT_CREDENTIAL",
          Origin: WEB,
        },
      }),
      environment,
    );
    assert.equal(result.status, 403);
    assert.equal(calls, 0);
    noStore(result);
    const body = await result.json();
    assert.equal(body.error.code, "REQUEST_FORBIDDEN");
    assert.equal(JSON.stringify(body).includes("PUBLIC_SYNTHETIC"), false);
  }
});
