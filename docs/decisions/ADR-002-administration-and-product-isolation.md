# ADR-002: Administración común y espacios propios por producto

Status: Approved, 2026-10-12. Configuración parcial: organización Supabase Abogalia Free creada; restantes espacios pendientes.

## Context

Arturo quiere mantener Kova y Abogalia separadas y evitar iniciar sesión repetidamente al trabajar con plugins y MCPs. Tras comparar usuarios independientes con organizaciones propias bajo un mismo usuario, confirmó usar posprojectsupport para administrar los servicios y espacios separados para Abogalia.

## Decision

Usar posprojectsupport como identidad administrativa de servicios, con espacios propios de Abogalia y conexiones reutilizables. Conservar la cuenta personal existente de GitHub para administrar repositorios y la organización propuesta, sin crear otra cuenta personal gratuita ni cambiar su correo por inferencia.

Los datos, credenciales de ejecución y despliegue, dominios, sesiones de clientes, recursos y facturación de Abogalia serán propios. Cada integración debe comprobar su acceso al espacio correcto. La decisión aprueba este modelo administrativo; proveedores, planes, presupuesto, autenticación de clientes y configuración específica siguen pendientes.

## Alternatives

- Usuarios administrativos independientes por producto, con varias conexiones al mismo plugin cuando estén disponibles.
- Recursos compartidos dentro del mismo espacio de Kova, separados únicamente por nombre.

## Why

Administrar espacios independientes con un usuario habitual reduce cambios de sesión y conserva separación de recursos y facturación. Fly recomienda administrar varias organizaciones con un usuario; Cloudflare admite usuarios miembros de varias cuentas y Resend equipos distintos bajo un correo. Supabase separa facturación y planes por organización. Las cuotas gratuitas pueden seguir aplicando al usuario o cuenta y deben verificarse.

## Consequences

Se conserva un acceso humano administrativo común. Los colaboradores futuros reciben acceso al espacio correspondiente mediante sus propias identidades. En Codex se reutilizan conexiones existentes si tienen alcance suficiente; una pertenencia administrativa no garantiza que la autorización del plugin incluya el nuevo espacio. Si hace falta una conexión adicional, comprobar soporte para conservar ambas antes de modificar accesos.

Un perfil de navegador separa cookies y ventanas, pero no selecciona ni limita la conexión de un MCP. Registrar identificadores de destino no secretos en el repositorio y almacenar credenciales en gestores de secretos. No copiar claves de Kova ni cambiar sus recursos por esta decisión.

## Risks

Una identidad administrativa compartida mantiene un punto de acceso común a ambos productos. Operar sobre el espacio incorrecto puede afectar al otro producto: verificar cuenta, organización y recurso antes de cada mutación. Las conexiones pueden caducar o requerir nueva autorización; no se promete ausencia permanente de login.

## Revisit when

Se separen propietarios o equipos, cambien requisitos de acceso, o una integración no permita administrar ambos espacios sin reconexiones frecuentes. La revisión podrá cambiar identidad administrativa sin mezclar datos ni credenciales de ejecución.

Configuración propuesta y fuentes oficiales: [checkpoint vigente](../checkpoints/platform-foundation-low-cost.md). Ejecución posterior al «Empecemos» de Arturo: organización Supabase Abogalia Free creada y acceso por ID comprobado sin modificar conexiones; [registro de servicios](../operations/service-registry.md). No hay proyecto de base ni otros espacios nuevos.
