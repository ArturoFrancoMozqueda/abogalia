# Legalia — preparación de Cloudflare Workers Static Assets

## Despliegue comprobado — 2026-10-15

Frontend publicado: https://legalia-web.legaliasupport.workers.dev/.
Cuenta y destino propios registrados en service-registry; configuración efectiva
`apps/web/wrangler.production.jsonc`, API permitida exclusivamente
`https://legalia-api.fly.dev`. La plantilla sin destino permanece cerrada.
Arturo autorizó User Read, Account Read, Background Access y Workers Scripts Write;
el permiso anterior Workers Write fue sustituido, sin añadir otros permisos.
Cloudflare Free, sin upgrade automático, analytics ni Workers Logs habilitados.

El primer deploy mostró502 porque Workers rechaza combinar `cache: no-store`
con `cf.cacheTtl: 0`. Se reprodujo en workerd local y se retiró el override cf;
se conserva no-store de solicitud y respuesta y no se habilitó caché.
[Fetch oficial](https://developers.cloudflare.com/workers/runtime-apis/fetch/).
El motor real pasó de502 a200; treinta pruebas sintéticas y tipos pasan.

Comprobaciones reales HTTPS desde el origen público: health200, sesión anónima200,
CSRF200, dos cookies __Host host-only/Secure/Path=/SameSiteStrict (sesión HttpOnly),
POST vacío sinCSRF403, conCSRF422 y Origin ajeno403. Authorization sintético no vacío
rechazado403. El intermediario elimina un Authorization vacío antes de llegar al
Worker: no se atribuye ese caso al control de presencia de la aplicación.
Todas esas respuestas API no-store; registro y acceso se renderizan en navegador.
Supabase Site URL público guardado y comprobado tras navegación nueva, sin comodines.
No se crearon usuarios ni enviaron correos durante estas comprobaciones.

El formulario expuso el formato GoTrue con code numérico + error_code estable;
se añadió compatibilidad limitada a categorías permitidas, sin inferir por mensajes.
Imagen API corregida desplegada; el navegador mostró el rechazo correcto de
credenciales sintéticas (sin crear cuenta ni enviar correo). Una sesión previa
al reinicio fue rechazada por CSRF y el cliente renovó el bootstrap sin reintentar
la mutación automáticamente.
La aceptación con cuenta confirmada, correo, MFA, revocación y restauración permanece
pendiente; este deploy no acredita C02 Done. Los apartados siguientes son históricos.


Actualización de integración A0: Wrangler4.151.0 fijado como dev dependency con
lockfile, instalación sin scripts. `deploy --dry-run` pasó y generó bundle local
sin subirlo; ejecución con dotenv deshabilitado y env-file/devnull, sin credenciales
o destinos reales. La ayuda de esa versión se consultó antes de ejecutarla.
La validación edge, cookies HTTPS y publicación reales siguen pendientes. Los
apartados iniciales describen la entrega del agente anterior a esta integración.

2026-10-15. Orden A0: hosting frontend Cloudflare Workers Static Assets y API Fly
aprobados; base `4d0b227c0618`. Esta entrega prepara fuentes y pruebas locales.
No crea cuenta/Worker/app Fly, configura dominios, inicia sesión con Wrangler,
lee secretos ni publica infraestructura. No se selecciona Paid ni gasto adicional.

## Artefactos y límites

- `apps/web/worker/index.ts`: gateway mismo origen y selección de archivos estáticos.
- `apps/web/wrangler.jsonc`: plantilla con destino vacío, sin account_id ni URLs reales inventadas.
- `apps/web/worker/index.test.mjs`: pruebas nativas Node 24, sin dependencia nueva.
- Build existente `apps/web/build/client`; portada `index.html` prerenderizada y
  `__spa-fallback.html` generado por React Router. No se despliega SSR ni build/server.

En la preparación inicial, `APPROVED_API_ORIGINS` y `LEGALIA_API_ORIGIN` estaban vacíos: toda llamada API
falla con JSON503 antes de fetch. A0 debe registrar después el origen HTTPS exacto
del recurso Fly de Legalia realmente provisionado, tanto en lista revisada como en
configuración. No basta un hostname que termine en fly.dev, una query, un header
Host, URL de usuario o variable arbitraria. Coincidencia exacta del origen canónico,
sin usuario, puerto explícito, path, query o fragmento. La factory de tests solo
inyecta un destino sintético; el export por defecto conserva la lista cerrada.

## Enrutamiento y caché

`run_worker_first=true` garantiza que API nunca entre en assets o fallback, incluso
con navegación. Se desactivan HTML handling y fallback automático; el Worker decide
`/` → `/index.html`, las seis rutas privadas existentes → `/__spa-fallback.html`,
y otros archivos → su path. Rutas desconocidas conservan404, no un éxito SPA falso.
Static Assets documenta el binding y la ejecución previa del Worker; SPA automático
normalmente usa index.html, por eso aquí se selecciona el fallback real de React
Router. [Binding](https://developers.cloudflare.com/workers/static-assets/binding/),
[SPA](https://developers.cloudflare.com/workers/static-assets/routing/single-page-application/),
[HTML handling](https://developers.cloudflare.com/workers/static-assets/routing/advanced/html-handling/).

`/api` y `/api/*`, incluidos auth y professional, solo se envían al backend fijo.
Mismo path/query y método; ninguna query elige destino. La solicitud upstream pide
no-store sin overrides cf de TTL; no se usa Cache API ni cache.put. Respuestas
API y shells privados llevan private/no-store y no-store para CDN/Cloudflare-CDN,
sin cache positivo de sesiones. API404/401/403/409/503 conserva respuesta backend,
sin convertirse en HTML estático. Fallo de configuración503; red o redirect502,
mensaje JSON fijo sin repetir cuerpo de error/excepción.

No se siguen redirects upstream ni se entrega Location/Content-Location al browser;
se descarta el cuerpo del redirect. Así las credenciales no viajan a otro destino.
Cloudflare advierte que redirect=follow puede reenviar headers entre hosts; esta
implementación fija manual en ambas capas.
[Request](https://developers.cloudflare.com/workers/runtime-apis/request/).

## Frontera de autenticación

El navegador sigue llamando `/api/*` al origen web. Origin, cookie, CSRF y
Sec-Fetch-Site/Mode/Dest originales se preservan; no se inventa Origin permitido o
same-origin cuando faltan. Bootstrap CSRF C02 necesita los Sec-Fetch originales.
Solo estos headers y Accept/Content-Type se reenvían. Presencia de Authorization
en API, incluso vacía y con cookie/CSRF válidos, se rechaza403 antes de fetch sin
leer/reflejar su valor, preservando el rechazo del contrato backend. Se descartan
Forwarded, X-Forwarded-*, Host e IPs aportadas por usuario como Fly-Client-IP,
CF-Connecting-IP o X-Real-IP. Ninguno se convierte en identidad o autorización.
El backend debe validar Origin contra el origen web público exacto configurado.

Se conservan separadas las cabeceras Set-Cookie, incluidos borrados/Expires y
atributos Secure/HttpOnly/SameSite/Path. No se reescribe Domain ni se degrada __Host.
Con API en el mismo origen del navegador, la cookie host-only pertenece al frontend
público; el backend HTTPS en producción debe emitir __Host y Secure. Se eliminan
headers hop-by-hop y CORS de la respuesta: no se habilita un API cross-origin.
Esto no reemplaza CSRF, validación activa de sesión, MFA o RLS de la API.

Las solicitudes ASSETS no reciben cookies, Authorization, headers de identidad ni
query. No hay logging, analytics, cuerpo/Auth o secretos en fuente/env público.
`observability.enabled=false` evita habilitar Workers Logs en esta plantilla; no
acredita políticas de logs propias de proveedores o del origen Fly, que A0 debe
revisar antes de tráfico de autenticación. No ejecutar tails con datos de usuario.

## Cuota y publicación posterior

Con run_worker_first=true **todas las solicitudes entrantes, incluso assets,
invocan el Worker y consumen su cuota**. Propuesta operativa Free: referencia actual
100000 solicitudes diarias/10ms CPU; medir carga/latencia y tratar agotamiento como
indisponibilidad. La cuota de Static Assets por sí sola no elimina la invocación
en esta configuración. No cambio automático a Paid, no garantía de capacidad.
[Workers pricing](https://developers.cloudflare.com/workers/platform/pricing/).

`workers_dev=false` y `preview_urls=false` dejan cerradas superficies de publicación
en la plantilla; no se inventa subdominio. A0 debe vincular únicamente el recurso y
origen web de Legalia provisionados, revisar identidad/cuenta por el canal aprobado
y ajustar la configuración pública antes de desplegar. workers.dev permite una
URL del proveedor sin comprar dominio; su habilitación y el origen API/Auth deben
ser explícitos y consistentes. [workers.dev](https://developers.cloudflare.com/workers/configuration/routing/workers-dev/).
No se agrega OAuth ni callbacks de terceros; los flujos aprobados siguen siendo
correo/contraseña, OTP y MFA. Una URL de hosting no aprueba nuevos flujos OAuth.

Secuencia del coordinador: build revisado → fijar/verificar Wrangler compatible
mediante cambio de dependencias propio → validación del empaquetado/bindings →
registrar hostname Fly exacto en lista/config → configurar API producción con
origen web exacto/cookies seguras → desplegar por flujo autorizado → comprobar
portada/assets/rutas privadas/API/CSRF/cookies/no-cache/redirect/rollback. No usar
npx latest ni instalar/provisionar desde esta entrega. Las validaciones con Wrangler,
workerd y Cloudflare real todavía no se ejecutaron.

## Verificación reproducible

Desde raíz, Node24 y dependencias ya fijadas del repositorio:

```sh
pnpm exec biome check apps/web/worker/index.ts apps/web/worker/index.test.mjs apps/web/wrangler.jsonc
pnpm --filter @abogalia/web exec tsc --ignoreConfig --noEmit --strict --target ES2022 --module ESNext --lib ES2022,DOM,DOM.Iterable worker/index.ts
node --test --test-reporter=dot apps/web/worker/index.test.mjs
```

Resultado: **30 pruebas nativas pasan**, tipo estricto y formato/lint focal pasan.
Prueban destino vacío/no canónico/externo, frontendHTTP cerrado, path/query y body,
headers originales vs spoof, ausencia de Origin sin inventarlo, API404 no assets,
no-store, cookies múltiples intactas, redirects301/302/303/307/308 sin segundo fetch
ni filtración, error de red sin retry/echo, rutas index/SPA/assets y404/405, plantilla
cerrada, cancelación y presencia de Authorization rechazada antes de upstream. Todo fetch y binding está simulado con
marcas públicas sintéticas; no se imprime ninguna cookie o cabecera de credencial.

Las pruebas usan Web APIs de Node, no el runtime Cloudflare. No acreditan despliegue,
resolución Fly, TLS/certificados reales, cache distribuido, múltiples Set-Cookie en
edge, cookies del browser, cuota real o login/OTP/MFA. A2 revisa la fuente por
separado; A0 integra CI/package/global. Ningún remoto, archivo privado, dependencia,
lockfile o commit fue operado por esta entrega.
