# Checkpoint — Suite inicial pequeña, con recursos propios de Abogalia

Fecha: 2026-10-12. React + FastAPI Approved, D-025. Hosting y gasto Discussing, D-026. Suite propia Approved, D-023. Administración con posprojectsupport y espacios propios Approved, D-027. Supabase Auth Approved, D-028; proyecto vacío propio Free/us-east-1 Implemented, D-029. Organización Abogalia Free creada y monorepo local implementado, D-030; integración de aplicación y hosting pendientes. Esta es la recomendación vigente; el checkpoint anterior conserva alternativas con Vercel y servicios pagados.

## Lo que entiendo

Arturo quiere conservar React + FastAPI y aprovechar las lecciones reales de Kova, comenzar con Supabase y Resend Free y aumentar recursos cuando sean necesarios. Mantendrá ambos productos: cada uno necesita datos, credenciales, releases, dominio y costos propios. Pidió sesiones separadas, pero señaló la fricción de iniciar sesión repetidamente en plugins y MCPs. La propuesta debe conservar el aislamiento y permitir reutilizar conexiones autenticadas. No se propone modificar Kova ni financiar Abogalia con sus créditos.

## Decisiones tomadas

React + FastAPI, D-025; suite propia, D-023; método basado en evidencia de Kova, D-021. Los dos flujos de texto asistido están aprobados, D-019/D-020, y OCR, extracción e indexación documental aplazados, D-022. Identidad, almacenamiento básico, manejo de datos reales y contratación siguen sujetos a sus decisiones.

Arturo confirmó posprojectsupport para administrar los servicios con espacios propios de Abogalia, D-027 y [ADR-002](../decisions/ADR-002-administration-and-product-isolation.md). Se conserva la identidad personal existente de GitHub. Después aprobó Supabase Auth como proveedor de identidad, D-028, y proyecto abogalia Free en us-east-1, D-029. Proyecto creado y verificado; los flujos de Identity aún están pendientes.

## Decisiones pendientes

Hosting Cloudflare/Fly, actualización del catálogo público, flujos de Identity, región y tamaño del backend, presupuesto global y objetivos de recuperación. Supabase Auth aprobado; proyecto Free en us-east-1 creado, integración pendiente. Cupo Free suficiente para esta creación; no presupone otro proyecto remoto gratuito. Confirmar disponibilidad del equipo Free propio en Resend antes de crearlo. No se autoriza contratar hosting por inferencia.

Implementar el modelo aprobado en D-027 verificando identidad y alcance de cada conexión antes de configurar. Varias conexiones al mismo plugin quedan como opción cuando la autorización sea específica de una cuenta o equipo. Diagnosticar dónde se repite el login; no se presupone que la causa sea expiración, cambio de proyecto o permisos. Esta actualización no cambia conexiones ni credenciales.

Comprobación de acceso, 2026-10-12: tras precisar Arturo que se refiere a las integraciones de Kova en Codex, las consultas de organizaciones Supabase y del equipo Kova en Vercel respondieron correctamente con las conexiones existentes, sin solicitar un nuevo login. Resend también respondió en la auditoría anterior de esta conversación. Esto confirma acceso en esas consultas, no explica los episodios anteriores ni garantiza acceso de escritura o persistencia futura. Los paneles web tienen sesiones diferentes y pueden requerir login aunque el conector funcione.

## Diseño propuesto

| Componente | Configuración inicial propuesta | Base mensual USD |
|---|---|---:|
| Frontend React | Cloudflare Workers Static Assets Free; rutas de API mediante Worker pequeño, dentro de cuota | 0 |
| API FastAPI | Una máquina Fly shared-cpu-1x de 1 GB, sin VM adicional de chat o documentos | 6.70 por 30 días encendida en iad/ewr |
| PostgreSQL | Supabase Free, proyecto y organización propios | 0 dentro de cuota |
| Correo | Resend Free, equipo y dominio propios | 0 dentro de cuota |
| **Base calculada de esos componentes** | | **6.70 + consumo y extras** |

Durante construcción local, hosting/base/correo pueden tener US$0 de cuotas. Fly no tiene un Free permanente para organizaciones nuevas. Su referencia de 1 GB corresponde a iad/ewr y 30 días; región y mes de 31 días cambian el precio. Transferencia, volúmenes y otros recursos son cargos aparte. Se propone una máquina sin volumen de datos y con IP compartida, no extras pagados innecesarios. 512 MB tendría referencia US$3.69, pero no se selecciona por ahorrar antes de medir memoria. Una máquina permite crecimiento vertical, pero no garantiza redundancia ni capacidad para una cifra de usuarios. [Fly pricing](https://docs.fly.io/about/pricing).

La tarifa de hosting podría subir a aproximadamente US$11.70 de base si el Worker requiere Paid. Workers Free limita ejecución a 100,000 peticiones diarias y 10 ms de CPU por invocación. Static Assets tiene peticiones gratuitas e ilimitadas, pero llamadas al Worker, proxy y SSR consumen cuota. Proponer ejecución del Worker solo en rutas necesarias como `/api/*`; validar límites, comportamiento de cookies, caché y latencia antes de declarar adecuado Free. FastAPI permanece en Python convencional sobre Fly. El catálogo público necesita renderizado indexable; la estimación presupone archivos estáticos o prerenderizados. SSR es decisión adicional con cómputo y prueba propios. [Static Assets](https://developers.cloudflare.com/workers/static-assets/billing-and-limitations/), [rutas selectivas](https://developers.cloudflare.com/workers/static-assets/routing/worker-script/), [Workers pricing](https://developers.cloudflare.com/workers/platform/pricing/).

Supabase Free incluye 500 MB de base, 1 GB de archivos, 50,000 usuarios activos mensuales de Auth, y pausa por inactividad; no incluye backups automáticos. Su uso inicial exige copias independientes y restauración comprobada antes de recibir datos reales. Pro desde US$25 se decide por cuotas, continuidad y recuperación, no por una fecha arbitraria. Con una Micro y el resto igual, la base sería aproximadamente US$31.70; consumo sigue aparte. [Supabase pricing](https://supabase.com/pricing), [backups](https://supabase.com/docs/guides/platform/backups).

Resend Free incluye 3,000 correos mensuales y máximo 100 diarios; crear alertas y pasar a Pro antes de que se comprometan acceso y notificaciones. Pro agrega US$20 de cuota. [Resend pricing](https://resend.com/pricing).

Sentry Developer, UptimeRobot Free, Turnstile, GitHub Actions y respaldos R2 son candidatos dentro de sus cuotas; no se presume que todas las cuotas de una cuenta se dupliquen por proyecto. Dominios, IA por consumo, impuestos, pagos y excedentes quedan fuera de US$6.70. No se autoriza un margen arbitrario. Cómputo de backups y tareas breves debe contarse en la API o CI disponible; una cola no ejecuta trabajo por sí sola.

### Dos suites, con administración cómoda

Modelo aprobado, D-027: usar posprojectsupport para administrar espacios propios de ambos productos, conservando la identidad personal existente de GitHub. La separación queda en recursos, permisos por espacio, credenciales de ejecución y facturación. La identidad humana de administración se comparte; no equivale a cuentas administrativas totalmente independientes. Configuración pendiente.

| Proveedor | Espacio propio propuesto para Abogalia | Acceso administrativo |
|---|---|---|
| GitHub | Organización propia y repositorio de Abogalia; secrets y workflows propios | Cuenta personal existente |
| Cloudflare | Cuenta de organización Abogalia con dominio, Worker y facturación propios | Perfil de usuario habitual miembro de ambas cuentas |
| Fly | Organización regular Abogalia, app FastAPI y facturación propias; no vincular facturación a Kova | Usuario habitual miembro de ambas organizaciones |
| Supabase | Organización Abogalia y proyecto propio; plan Free sujeto a cupo | Usuario habitual miembro de ambas organizaciones |
| Resend | Equipo Abogalia con dominio de envío, claves y facturación propios; Free sujeto a disponibilidad | Usuario habitual miembro de ambos equipos |

Fly recomienda un usuario para administrar varias organizaciones sin alternar logins. Una organización regular permite facturación propia; no se propone una organización vinculada a la factura de Kova. Cloudflare distingue el perfil de usuario de sus cuentas de organización: un usuario puede pertenecer a varias cuentas con configuraciones y facturación propias. GitHub permite pertenecer a varias organizaciones con una cuenta personal y limita a una cuenta personal gratuita por persona. Estos nombres son objetivos de organización, no recursos creados ni disponibilidad confirmada. [Fly: organizaciones](https://docs.fly.io/blueprints/staging-prod-isolation/), [Cloudflare: cuentas y perfiles](https://developers.cloudflare.com/fundamentals/concepts/accounts-and-zones/), [términos de GitHub](https://docs.github.com/en/site-policy/github-terms/github-terms-of-service).

Arturo había pedido sesiones separadas y después señaló la fricción de autenticar plugins/MCPs continuamente. Se recomienda una sesión administrativa habitual por proveedor, con accesos directos al espacio correcto; perfiles de navegador separados son opcionales para ordenar ventanas. Los perfiles separan cookies pero no seleccionan ni aíslan las credenciales de un MCP. Las sesiones de los usuarios de las aplicaciones sí serán propias de cada producto; compartir administrador no comparte el acceso de clientes.

En Codex, conservar las conexiones existentes y comprobar mediante una lectura el acceso al espacio Abogalia cuando exista. No asumir que el plugin alcanza todos los equipos a los que pertenece el usuario: una autorización puede estar limitada a un espacio. Cuando se necesite otra conexión, mantener ambas si el plugin y entorno lo permiten. OpenAI documenta varias cuentas conectadas al mismo plugin, con cada llamada usando las credenciales de la conexión seleccionada. Su disponibilidad concreta debe verificarse; no se promete ausencia permanente de reautenticación. [Autenticación y múltiples cuentas](https://developers.openai.com/plugins/build/auth#support-multiple-accounts).

Para cada operación comprobar cuenta, organización y recurso de destino; guardar únicamente sus identificadores no secretos en el proyecto. Las claves de aplicación y despliegue serán específicas de Abogalia, almacenadas en los gestores de secretos correspondientes. Priorizar conectores y herramientas oficiales; abrir paneles solo cuando aporten información necesaria. No guardar tokens en documentación ni reutilizar claves de Kova. No se modifican las conexiones de Kova por esta propuesta.

Supabase factura por organización: Free/Pro afecta proyectos de esa organización. Separarlas permite subir Abogalia sin subir Kova. El límite de dos proyectos Free aplica a todas las organizaciones donde se es Owner/Administrator, no dos por organización; los pausados no cuentan. El conector actual muestra Kova Production ACTIVE_HEALTHY y CENEVAL Study App INACTIVE: apunta a un cupo posible, que se confirmará al provisionar. Reactivar CENEVAL puede cambiar disponibilidad; no se elimina o reactiva para hacer espacio. [Billing](https://supabase.com/docs/guides/platform/billing-on-supabase).

Resend admite varios equipos bajo el mismo correo administrativo y separa sus API keys, facturación y consumo. No basta agregar otro dominio a un equipo compartido para conseguir ese aislamiento. [Managing Teams](https://resend.com/docs/dashboard/settings/team).

## Datos afectados

Los datos previstos de Abogalia permanecerán en recursos propios, sin lectura de los datos de clientes de Kova. Este checkpoint no crea esquemas, sesiones ni políticas de retención; identidad y autorización requieren diseño específico para práctica independiente y despacho.

## Seguridad

Validar autorización en FastAPI y base, sesiones, cookies y CSRF; excluir respuestas privadas de caché pública y secretos del navegador. Mantener claves de runtime y migración distintas y accesos acotados por aplicación. MFA administrativa, restauración comprobada, filtrado de telemetría y URLs correctas de correo forman parte de la entrega operativa. Pruebas con datos sintéticos aislados. No se aprueba enviar texto jurídico a un proveedor de IA ni un diseño de pagos por esta recomendación; quedan sus checkpoints y LEGAL REVIEW REQUIRED.

## Impacto futuro

Crecer por memoria/CPU medidas en Fly y por cómputo de Supabase cuando corresponda. Las réplicas pueden ser necesarias por disponibilidad antes que por carga; se presupuestarán cuando se defina ese objetivo. Worker Paid, correo Pro y base Pro tienen disparadores separados. Se conserva portabilidad de FastAPI/PostgreSQL y release coordinado entre frontend/API. No se promete operación sin mantenimiento ni una factura máxima.

## Implementación propuesta

Orden vigente tras aprobar administración, sin iniciar contratación:

1. **Repositorio y registro de servicios.** El repositorio público `ArturoFrancoMozqueda/abogalia` ya existe y contiene documentación. Preparar estructura React/FastAPI, desarrollo local, configuración de ejemplo sin valores secretos, exclusiones Git y CI. Registrar proveedor, espacio, entorno e identificadores reales cuando existan; no inventarlos. La organización propia de GitHub sigue como destino por configurar; transferir el repo no es dependencia de comenzar localmente y no se ejecuta por inferencia.
2. **Acceso de clientes y permisos.** Supabase Auth aprobado, D-028; definir flujos de Identity, propiedad de solicitudes, práctica independiente y membresía de un despacho antes de crear tablas. Autenticación validada en FastAPI y autorización diseñada por recurso. Renderizado estático inicial y estructura aprobados e implementados, D-030; catálogo futuro requiere regeneración específica. [Supabase Auth](https://supabase.com/docs/guides/auth).
3. **Supabase propio.** Organización Abogalia Free y proyecto xggefantvuwpilksfdoy en us-east-1 creados y verificados. La consulta directa del conector funciona sin nuevo login aunque las listas generales aún omiten el destino. Trigger RLS habilitado, cero tablas public y privilegios residuales documentados en el [registro](../operations/service-registry.md). Definir grants/revokes, políticas, propietarios y credenciales distintas de runtime/migración en el diseño de Identity; migraciones versionadas y copia/restauración antes de datos reales.
4. **Cloudflare y correo.** Preparar cuenta propia, URLs y secretos de despliegue. Se puede validar con URLs del proveedor sin comprar un nombre todavía: la marca sigue pendiente. Después de elegir y disponer del dominio, configurar DNS, equipo Resend, dominio de envío verificado y URLs de autenticación. Integrar correo y probar alta/recuperación; no inferir entrega por aceptación de API.
5. **Fly cuando la API pueda desplegarse.** Preparar organización propia, app y release coordinado con React; contratar cómputo dentro del presupuesto aprobado. Verificar memoria, salud, conexión a base, sesión y autorización con datos sintéticos. Incorporar diagnóstico antes del primer despliegue remoto. No mantener una máquina pagada sin aplicación lista para verificar.
6. **Comprobación operativa y capacidades.** Probar aislamiento por contexto, correo, restauración, versiones y rollback antes de datos reales. Incorporar las dos funciones de IA mediante decisiones de proveedor, límites y tratamiento. No se despliega un servidor documental permanente.

Este orden concreta preparación y dependencias; la aprobación de D-027 no autoriza por sí sola comprar dominio, contratar Fly, escoger Auth, transferir GitHub o implementar esquemas pendientes.

Inicio de preparación: Arturo dejó paneles abiertos e indicó «Empecemos». Se creó la organización Abogalia Free en Supabase y se verificó mediante consulta directa desde el conector. Después aprobó monorepo React Router/FastAPI, Supabase Auth y región us-east-1; la base local se implementó y Arturo completó la creación del proyecto vacío. Primer bloque verificado y terminado: [registro de servicios](../operations/service-registry.md) y [checkpoint](repository-and-empty-database.md). La disponibilidad del panel Vercel no cambia el hosting propuesto. Login, permisos, conexión de aplicación y hosting siguen pendientes.
