# ADR-004: Proyecto Supabase vacío propio en us-east-1

Status: Implemented, 2026-10-12. Proyecto vacío creado por Arturo y verificado por conector; sin integración de aplicación.

## Context

La organización Supabase Abogalia ya existe en Free, identificador jdmkzzkgnzwldthjqtgx. Arturo eligió crear el proyecto vacío en us-east-1, con plan Free y costo previsto US$0/mes dentro de cuota. Esta región se propuso para cercanía con la API Fly en iad; el hosting y su gasto siguen pendientes.

## Decision

Crear el proyecto abogalia en la organización Abogalia, región us-east-1 (North Virginia), plan Free. Desactivar la exposición automática de nuevas tablas y activar RLS automático en public como protección inicial. No crear tablas de negocio, usuarios del producto, almacenamiento de documentos ni políticas públicas antes del diseño correspondiente.

## Alternatives

- us-west-1 u otra región, según latencia y ubicación de datos requerida.
- Desarrollo exclusivamente local mientras se resuelven esas restricciones.

## Why

Mantener base y API cercanas es una hipótesis razonable de latencia, pendiente de medición. Un proyecto propio conserva separación de datos, credenciales y configuración frente a Kova. El tier gratuito permite preparar integración sin contratar cómputo pagado.

## Consequences

La región fija ubicación inicial de la base; cambiarla puede requerir migración. Free tiene cuotas, pausa por inactividad y limitaciones de respaldo: preparar recuperación antes de recibir datos reales. El límite gratuito aplica al administrador a través de sus organizaciones; confirmarlo al crear. Supabase Auth está aprobado en ADR-003, pero sus flujos no se implementan por crear el proyecto.

## Risks

RLS automático sin políticas de acceso concede cero acceso mediante los roles sujetos a RLS, pero no protege frente a credenciales que lo omitan: diseñar también roles de runtime y autorización de la API. Esta configuración no demuestra aislamiento del producto ni reemplaza pruebas. Tratamiento y ubicación de datos legales sensibles: LEGAL REVIEW REQUIRED antes de admitirlos.

La creación por conector no pudo avanzar porque get_cost no estaba disponible. Arturo completó la contraseña y el envío del formulario web. Proyecto `xggefantvuwpilksfdoy` verificado en la organización aprobada, Free, us-east-1, ACTIVE_HEALTHY y sin tablas public. No se inventó una confirmación de costo ni se registró una credencial en el repo.

El trigger ensure_rls está habilitado. La exposición automática se desactivó en el formulario, pero la consulta de catálogo mostró privilegios residuales para postgres (incluido TRUNCATE) y grants CRUD predeterminados para tablas creadas por supabase_admin. RLS no restringe todas las operaciones; este estado inicial no es un modelo de permisos del producto. Las futuras migraciones deben controlar explícitamente grants/revokes, propietarios y políticas y probarlos antes de admitir datos. La verificación no creó tablas ni modificó permisos. Evidencia detallada en el registro de servicios.

## Revisit when

Mediciones, continuidad operativa, cuota gratuita, recuperación o requisitos de ubicación de datos requieran cambiar región o tier. No subir de plan automáticamente ni reutilizar un proyecto de Kova.

Fuentes: [regiones Supabase](https://supabase.com/docs/guides/platform/regions), [facturación y cupo Free](https://supabase.com/docs/guides/platform/billing-on-supabase). Estado real: [registro de servicios](../operations/service-registry.md).
