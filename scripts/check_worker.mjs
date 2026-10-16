/** Local Workers validation. Clean environment, loopback fixtures, no credentials. */
import { spawn } from "node:child_process";
import { mkdtemp, readFile, rm, writeFile } from "node:fs/promises";
import { createServer } from "node:http";
import { tmpdir } from "node:os";
import { dirname, join, resolve } from "node:path";
import { setTimeout as delay } from "node:timers/promises";
import { fileURLToPath } from "node:url";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const temporary = await mkdtemp(join(tmpdir(), "legalia-worker-check-"));
const cleanEnv = {
  PATH: `${dirname(process.execPath)}:/usr/bin:/bin`,
  HOME: temporary,
  XDG_CONFIG_HOME: temporary,
  CLOUDFLARE_LOAD_DEV_VARS_FROM_DOT_ENV: "false",
  WRANGLER_SEND_METRICS: "false",
  NO_COLOR: "1",
};
const cli = join(root, "apps/web/node_modules/wrangler/bin/wrangler.js");
const run = (args) =>
  new Promise((resolveRun, reject) => {
    const child = spawn(process.execPath, args, {
      cwd: root,
      env: cleanEnv,
      stdio: "ignore",
    });
    child.on("error", reject);
    child.on("exit", (code) =>
      code === 0 ? resolveRun() : reject(new Error("Check failed")),
    );
  });
const listen = (server) =>
  new Promise((accept, reject) => {
    server.once("error", reject);
    server.listen(0, "127.0.0.1", () => accept(server.address().port));
  });
let dev;
let backend;
let stage = "types";
try {
  await run([
    cli,
    "types",
    "apps/web/worker/worker-configuration.d.ts",
    ...(process.argv.includes("--update-types") ? [] : ["--check"]),
    "--config",
    "apps/web/wrangler.production.jsonc",
    "--env-file",
    "/dev/null",
  ]);
  await run([
    join(root, "apps/web/node_modules/typescript/bin/tsc"),
    "-p",
    join(root, "apps/web/worker/tsconfig.json"),
  ]);
  stage = "node-tests";
  await run([
    "--test",
    "--test-reporter=dot",
    "apps/web/worker/index.test.mjs",
  ]);
  stage = "workerd";
  backend = createServer(async (req, res) => {
    if (req.url === "/api/redirect") {
      res.writeHead(302, { Location: "https://never-follow.invalid" });
      res.end();
      return;
    }
    if (req.url === "/api/cookies") {
      res.setHeader("Set-Cookie", [
        "__Host-synthetic_session=PUBLIC_FIXTURE; Secure; HttpOnly; Path=/; SameSite=Strict",
        "__Host-synthetic_csrf=; Secure; Path=/; SameSite=Strict; Expires=Thu, 01 Jan 1970 00:00:00 GMT",
      ]);
      res.setHeader("Access-Control-Allow-Origin", "*");
    }
    let body = "";
    for await (const chunk of req) body += chunk;
    res.setHeader("Content-Type", "application/json");
    res.end(
      JSON.stringify({
        ok: true,
        body: body === "PUBLIC_SYNTHETIC_BODY",
        cookie: req.headers.cookie === "synthetic=PUBLIC_FIXTURE",
        csrf: req.headers["x-csrf-token"] === "PUBLIC_FIXTURE",
        origin: req.headers.origin === "https://synthetic.invalid",
        noForwarded: !req.headers["x-forwarded-host"],
      }),
    );
  });
  const backendPort = await listen(backend);
  const reserve = createServer();
  const workerPort = await listen(reserve);
  await new Promise((done) => reserve.close(done));
  // Read only reviewed public configuration; never copy secrets or production bindings.
  const production = JSON.parse(
    await readFile(join(root, "apps/web/wrangler.production.jsonc"), "utf8"),
  );
  const config = join(temporary, "wrangler.jsonc");
  await writeFile(
    config,
    JSON.stringify({
      name: "legalia-synthetic-local-test",
      main: join(root, "apps/web/worker/runtime.test-worker.mjs"),
      compatibility_date: production.compatibility_date,
      compatibility_flags: production.compatibility_flags || [],
      observability: { enabled: false },
      workers_dev: false,
      vars: { FIXTURE_ORIGIN: `http://127.0.0.1:${backendPort}` },
    }),
  );
  dev = spawn(
    process.execPath,
    [
      cli,
      "dev",
      "--local",
      "--ip",
      "127.0.0.1",
      "--port",
      String(workerPort),
      "--config",
      config,
      "--env-file",
      "/dev/null",
      "--log-level",
      "none",
    ],
    { cwd: temporary, env: cleanEnv, stdio: "ignore", detached: true },
  );
  let ready = false;
  for (let i = 0; i < 80; i++) {
    if (dev.exitCode !== null) throw new Error("Runtime exited");
    try {
      ready = (
        await fetch(`http://127.0.0.1:${workerPort}/ready`, {
          signal: AbortSignal.timeout(500),
        })
      ).ok;
    } catch {
      /* Local server not ready yet. */
    }
    if (ready) break;
    await delay(250);
  }
  if (!ready) throw new Error("Runtime unavailable");
  const response = await fetch(`http://127.0.0.1:${workerPort}/run`, {
    signal: AbortSignal.timeout(15000),
  });
  const result = await response.json();
  if (!response.ok || result.passed !== 9 || result.failed !== 0)
    throw new Error("Runtime regression");
  console.log(
    JSON.stringify({
      status: "passed",
      generated_types: true,
      node_tests: 30,
      workerd_tests: 9,
    }),
  );
} catch {
  console.log(
    JSON.stringify({ status: "failed", stage, diagnostics: "suppressed" }),
  );
  process.exitCode = 1;
} finally {
  if (dev?.pid) {
    const exited = new Promise((done) => dev.once("exit", done));
    try {
      process.kill(-dev.pid, "SIGTERM");
    } catch {
      /* Already stopped. */
    }
    await Promise.race([exited, delay(3000)]);
  }
  backend?.closeAllConnections();
  if (backend) await new Promise((done) => backend.close(done));
  await rm(temporary, { recursive: true, force: true });
}
