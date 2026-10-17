# Checkpoint — Repositorio ejecutable y proyecto de base vacío

Fecha: 2026-10-12. Estado: Implemented, base local y proyecto vacío verificados. La instrucción «Empecemos» autorizó iniciar la preparación acordada y crear el espacio administrativo gratuito. Después se aprobaron estructura/renderizado, proveedor Auth y configuración del proyecto vacío, antes de implementar sus respectivos alcances.

Actualización: Auth aprobado en D-028, sin integración. Proyecto Free/us-east-1 creado por Arturo y verificado, D-029 Implemented, ref xggefantvuwpilksfdoy. Monorepo Abogalia con React Router confirmado expresamente, D-030, y base local implementada y verificada. Kova permanece aparte. Este bloque está terminado; identidad, conexión de aplicación y hosting tienen alcances posteriores.

## Lo que entiendo

Abogalia necesita una base ejecutable para construir capacidades completas con React y FastAPI, recursos propios y administración cómoda con posprojectsupport. Ya existen el monorepo ejecutable localmente y el proyecto Supabase vacío propio en Free. La aplicación aún no se conecta a Supabase ni implementa flujos del producto.

## Decisiones tomadas

React + FastAPI, D-025; recursos propios, D-023; administración con posprojectsupport y espacios separados, D-027. No se reutilizan claves, clientes ni infraestructura de Kova. La creación de la organización Supabase gratuita está verificada en el [registro de servicios](../operations/service-registry.md).

Supabase Auth, D-028 y [ADR-003](../decisions/ADR-003-supabase-auth.md); proyecto abogalia Free en us-east-1, D-029 y [ADR-004](../decisions/ADR-004-empty-supabase-project.md). Crear la base vacía no implementa todavía sus flujos de autenticación ni permisos.

Monorepo Abogalia, apps/web React Router framework sobre Vite, prerenderizado público y apps/api FastAPI, D-030 y [ADR-005](../decisions/ADR-005-monorepo-and-rendering.md). La implementación actual incluye solo portada y comprobación de HTTP local; no incluye flujos de negocio.

## Decisiones pendientes

1. **Catálogo futuro y hosting.** Estructura/renderizado aprobados e implementados en su base técnica. Quedan por diseñar rutas públicas del catálogo, frecuencia de regeneración, áreas privadas y configuración del hosting. El prerender genera contenido durante el build: cambios públicos exigen regeneración; no se presupone suficiente para todo el catálogo futuro. [React Router: rendering](https://reactrouter.com/start/framework/rendering).
2. **Integración de identidad.** Proveedor Supabase Auth aprobado. Siguen pendientes registro, roles, permisos, MFA y políticas de sesión; esos flujos tendrán checkpoint de Identity. [Supabase Auth](https://supabase.com/docs/guides/auth).
3. **Permisos y operación de la base.** Proyecto vacío creado y verificado en Free/us-east-1. RLS automático habilitado y cero tablas public; el formulario desactivó exposición automática, pero existen privilegios residuales y diferencias según propietario. [Detalle](../operations/service-registry.md). Antes de crear tablas, definir explícitamente propiedad, permisos y políticas. No hay benchmark; la ubicación final de datos sensibles requiere revisión de tratamiento y LEGAL REVIEW REQUIRED antes de usarlos.

La selección de Vercel frente a Cloudflare/Fly y el gasto de hosting siguen pendientes. Tener su panel abierto no modifica esas decisiones.

## Diseño propuesto

Primera entrega técnica: frontend y API ejecutables localmente, configuración de ejemplo sin secretos, comandos reproducibles, dependencias fijadas y CI de build/tipos/lint y contratos técnicos esenciales. La interfaz inicial será una comprobación técnica explícita, sin simular un flujo comercial completo. Un endpoint de salud comprobará la API; no se devolverán secretos ni detalles de infraestructura.

El proyecto Supabase será propio y vacío. No activar integración automática de GitHub, ramas pagadas o políticas públicas de tablas por comodidad. Los proveedores de hosting se conectarán cuando la entrega local esté verificada y su selección aprobada.

## Datos afectados

Nombre e identificador de organización, proyecto vacío y configuración técnica, y registro de destinos administrativos. Sin solicitudes legales, usuarios del producto, documentos, pagos ni migraciones de negocio.

## Seguridad

El repo público debe excluir `.env`, claves y artefactos generados. El administrador y las credenciales de runtime se distinguen; las credenciales nuevas no se muestran ni guardan en documentación. El formulario de Supabase exige una contraseña de base: si se usa ese formulario, el usuario completa su creación y envío conforme a las reglas de control del navegador. No ejecutar operaciones en Kova ni sustituir destinos de Abogalia por sus IDs.

## Impacto futuro

La estructura soportará desarrollo coordinado de frontend/API y separación de módulos. Auth y propiedad condicionarán todas las capacidades. La región cambia latencia y ubicación de datos; el renderizado cambia despliegue y actualización del catálogo. La configuración local no decide modelo de multi-tenancy ni contratación.

## Implementación propuesta

Completado: organización gratuita de Supabase, comprobación directa de acceso, registro de servicio, exclusiones Git, código React/FastAPI, dependencias fijadas, CI preparado y verificación local. [Informe](../operations/local-foundation-verification.md). Arturo completó la creación del proyecto vacío; nombre, organización, plan, región, estado saludable y ausencia de tablas public verificados con la conexión existente, sin nuevo login. La consulta de catálogos identificó permisos que deben tratar las futuras migraciones. No se crearon tablas, flujos de Identity ni despliegues pagados en este bloque.
