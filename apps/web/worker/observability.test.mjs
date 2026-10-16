/** Fixed synthetic inputs only; the projection never receives real request data. */
import assert from "node:assert/strict";
import test from "node:test";
import { buildGatewayEvent } from "./observability.ts";

test("operational projection contains only fixed fields and allowlisted outcomes", () => {
  for (const outcome of [
    "backend_unavailable",
    "upstream_redirect_blocked",
    "origin_configuration_invalid",
  ]) {
    const result = buildGatewayEvent(outcome);
    assert.deepEqual(result, {
      schema_version: 1,
      component: "web_gateway",
      outcome,
    });
    assert.equal(Object.isFrozen(result), true);
    assert.ok(JSON.stringify(result).length < 160);
  }
});

test("operational projection rejects request-like content without inspecting it", () => {
  const hostile = {
    toString() {
      throw new Error("Must never be called");
    },
  };
  for (const input of [
    null,
    undefined,
    500,
    hostile,
    [],
    {
      outcome: "backend_unavailable",
      url: "https://synthetic.invalid/private",
    },
    "backend_unavailable?email=synthetic@example.invalid",
    "PUBLIC_SYNTHETIC_VALUE",
  ])
    assert.equal(buildGatewayEvent(input), null);
});

test("production and template disable all collection and preserve query redaction", async () => {
  const { readFile } = await import("node:fs/promises");
  for (const name of ["../wrangler.production.jsonc", "../wrangler.jsonc"]) {
    const source = await readFile(new URL(name, import.meta.url), "utf8");
    const config = JSON.parse(source.replace(/^\s*\/\/.*$/gm, ""));
    assert.equal(config.observability.enabled, false);
    assert.equal(config.observability.redact_query_string, true);
    assert.deepEqual(config.observability.logs, {
      enabled: false,
      invocation_logs: false,
      persist: false,
    });
    assert.deepEqual(config.observability.traces, {
      enabled: false,
      persist: false,
    });
    assert.deepEqual(config.assets.run_worker_first, ["/*", "!/assets/*"]);
  }
});
