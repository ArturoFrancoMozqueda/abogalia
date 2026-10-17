# ADR-003: Supabase Auth como proveedor de identidad

Status: Approved, 2026-10-12. Integración pendiente.

## Context

Abogalia usará React y FastAPI y tendrá recursos propios en Supabase. Se comparó identidad administrada con adaptar la autenticación propia de Kova o añadir un proveedor separado. Arturo eligió expresamente Supabase Auth en la pregunta del primer bloque.

## Decision

Usar Supabase Auth para la identidad de usuarios del producto, dentro del proyecto propio de Abogalia. FastAPI comprobará autenticación y autorización de sus operaciones. La elección de proveedor no aprueba todavía métodos de registro, roles, permisos, MFA, políticas de sesión ni modelos de propiedad y membresía.

## Alternatives

- Adaptar autenticación propia de Kova, con mantenimiento de sesiones, recuperación y controles propios.
- Clerk como proveedor independiente, con integración y límites de su plan por verificar.

## Why

Supabase Auth ofrece identidad, sesiones y recuperación en la suite de datos elegida, reduciendo componentes separados que administrar. La integración y el flujo completo deben comprobarse; tener un usuario autenticado no otorga por sí solo acceso a datos de otro cliente o despacho.

## Consequences

Separar las identidades de clientes de la identidad administrativa posprojectsupport. Validar credenciales en la API mediante mecanismos oficiales y diseñar permisos por recurso antes de crear tablas. No copiar usuarios ni sesiones de Kova. Correo, URLs de recuperación y callbacks dependen de las URLs de Abogalia y su remitente propio.

## Risks

Una integración incorrecta puede aceptar credenciales no válidas, prolongar sesiones indebidamente o confundir autenticación con acceso autorizado. La implementación de Identity tendrá checkpoint específico y pruebas de sesión y aislamiento. No usar metadatos editables por el usuario como fuente de autorización.

## Revisit when

Requisitos de identidad, recuperación, integración o costo medidos justifiquen reconsiderar el proveedor. Cambiar el hosting de React o FastAPI no implica cambiar automáticamente Supabase Auth.

Fuente técnica: [Supabase Auth](https://supabase.com/docs/guides/auth). Alcance del bloque: [checkpoint de repositorio y base vacía](../checkpoints/repository-and-empty-database.md).
