/** Prepared projection only. No logger, request access, storage or transmission. */
const OUTCOMES = [
  "backend_unavailable",
  "upstream_redirect_blocked",
  "origin_configuration_invalid",
] as const;
type Outcome = (typeof OUTCOMES)[number];
export type GatewayEvent = Readonly<{
  schema_version: 1;
  component: "web_gateway";
  outcome: Outcome;
}>;

export function buildGatewayEvent(outcome: unknown): GatewayEvent | null {
  // Do not stringify unknown values or copy fields from a request/error object.
  if (typeof outcome !== "string") return null;
  const allowed = OUTCOMES.find((value) => value === outcome);
  if (!allowed) return null;
  return Object.freeze({
    schema_version: 1,
    component: "web_gateway",
    outcome: allowed,
  });
}
