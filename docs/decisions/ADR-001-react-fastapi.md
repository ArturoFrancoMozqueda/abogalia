# ADR-001: React y FastAPI como stack de aplicación

Status: Approved, 2026-10-12. Implementación pendiente.

## Context

Abogalia se construirá como producto completo por capacidades. Se comparó una aplicación React Router con backend TypeScript integrado en Workers frente a separar frontend React y backend FastAPI, incorporando experiencia verificable de Kova. Arturo expresó preferencia por el segundo camino y confirmó: «Entonces vamos con React y FastAPI».

## Decision

Usar React para la interfaz y FastAPI sobre Python como backend central. La elección aprueba estos componentes del stack, no una copia de Kova, la contratación de recursos ni el diseño de identidad, datos o funcionalidades pendientes.

## Alternatives

- React Router con backend TypeScript integrado en Cloudflare Workers.
- Next.js con backend integrado en Vercel.

## Why

La experiencia adquirida en Kova aporta continuidad de herramientas y diagnóstico. El backend independiente permite organizar reglas de negocio y ofrecer una API a distintas interfaces. La antigüedad o novedad de un framework no fue el criterio de elección.

## Consequences

Frontend y backend tienen artefactos y despliegues separados. Deben coordinar contratos de API, sesión, migraciones y versiones. La suite debe presupuestar cómputo del backend además de hosting web, base, correo y operación. El modo de renderizado del catálogo público y el framework que acompañe a React se decidirán antes de preparar el frontend.

## Risks

Despliegues incompatibles, duplicación de reglas entre frontend y backend, sesión mal integrada y saturación de conexiones. Se propone separar módulos, probar contratos y aislamiento con PostgreSQL real, y desplegar con trazabilidad de versión. No hay pruebas de carga ni código todavía.

## Revisit when

Un requisito o medición demuestre una limitación relevante, o Arturo solicite reconsideración. Un proveedor distinto de hosting no implica automáticamente cambiar React o FastAPI.

Hosting, identidad, datos, tiers, regiones y presupuesto permanecen en discusión en el [checkpoint de base técnica](../checkpoints/platform-foundation.md).
