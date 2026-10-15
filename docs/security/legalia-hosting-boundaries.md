# Fronteras de seguridad: Cloudflare Static Assets y Fly

2026-10-15. A2, diseño y revisión independiente de artefactos locales. Arturo eligió
Cloudflare Static Assets y Fly para backend; A0 conserva destino, acceso, gasto y
publicación. Este documento no crea recursos, concede permisos ni certifica un
despliegue. No cambios de migraciones, secretos o datos reales.

## Alcance y estado de aprobación

React Router/Vite estático y FastAPI/Supabase Auth conservan su arquitectura.
Navegador → origen HTTPS de Cloudflare → Worker para /api → Fly HTTPS → PostgreSQL
privado/Supabase Auth. No SDK Auth público, service_role, base accesible desde Worker
o navegador, SSR nuevo, caché de sesión o funciones profesionales añadidas.

La instrucción de habilitar registro/acceso anticipadamente está aplicada a web/API
locales según checkpoint de activación. Esa excepción no prueba entrega, MFA o
revocación real ni determina por sí sola condiciones de publicación en Internet.
A0 aplica la autorización vigente de Arturo para la publicación concreta; no se
reabre una decisión ya suficiente ni se deduce excepción nueva de este documento.
Los apartados históricos de plataforma con hosting Discussing no anulan su elección
posterior. Hosting elegido tampoco equivale a despliegue/seguridad comprobados.

## Contrato de origen, cookies y CSRF

Solo un origen público HTTPS exacto, sin path/credenciales/query/fragmento ni barra
final, definido después de conocer el destino real. Backend en modo producción:
ABOGALIA_ENVIRONMENT no development y Settings.development_http=False. Sin HTTP
local o fixtures como fallback. Mantener issuer/proyecto/audience/JWT/sub/SID/AAL,
sesión activa por GET/user, cifrado custodiado, 12h/30min y fronteras transaccionales.

Cookies __Host-abogalia_session y __Host-abogalia_csrf: Secure, Path=/, sin Domain,
SameSite=Strict. Sesión HttpOnly; CSRF no HttpOnly por contrato existente. Set y
delete deben conservar exactamente los atributos, también en401/logout/rotación.
Worker transmite múltiples Set-Cookie como campos separados; nunca dividir por
coma (Expires contiene coma) o convertirlos a un único string. No reescribir Domain
para compartirlos con Fly. El navegador conserva ambas cookies en el host público.

POST/PATCH siguen Origin exacto + CSRF ligado a cookie, JSON estricto y cuerpo
acotado. Preservar Origin y Sec-Fetch-* originales; no inventar valores same-origin
ni reemplazar origen atacante por el permitido. Rechazar bearer conserva contrato.
Sin CORS comodín, ACA-Credentials para otros sitios o excepciones por ser proxy.
Una preflight o un header Origin no son autenticación. No habilitar métodos nuevos
para hacer funcionar un formulario; un error de CSRF debe seguir rechazándose.

## Proxy y activos estáticos

Destino backend es un único HTTPS Fly real validado por A0, no input del navegador.
Allowlist exacta de esquema/hostname/puerto; sin userinfo, path base arbitrario,
query/fragmento, wildcard, host derivado de Host/Forwarded o parámetros url/next.
Conservar path/query autorizados por el contrato HTTP; query Auth prohibida llega
al rechazo uniforme, nunca a logs ni a una redirección. No URL join que cambie
authority por //host, escapes o esquema inyectado. Fetch con redirect manual/error:
no seguir3xx con Cookie/Authorization/cuerpo privado a otra ubicación. Un Location
inesperado produce fallo fijo sin filtrar destino/diagnóstico/cookies recibidas.

Forwarding por allowlist de headers necesarios. Suprimir Host, Forwarded,
X-Forwarded-*, X-Real-IP y headers de enrutamiento/proveedor aportados por cliente;
no convertirlos a identidad, origen confiable, permisos o IP de rate limit.
El transporte al host Fly usa Host del destino fijo. No enviar Authorization de
usuario ni cabeceras de despliegue; rechazo de bearer no debe transformarse en éxito.
Si llega Authorization, rechazar403 fijo antes de fetch; quitarlo silenciosamente
permitiría ejecutar cookie+CSRF válidos que FastAPI habría rechazado.
Cookie y X-CSRF-Token solo van al destino aprobado por HTTPS.

/api y /api/* deben ejecutarse antes de Static Assets/SPA fallback. API404/error no
puede convertirse en index.html200. Archivos públicos tienen política independiente;
ningún JSON privado, cookie, `.env`, backup, sourcemap con datos privados o script
de operador se empaqueta en assets. No registrar tokens/OTP/PII/URLs privadas.
Preview/orígenes alternos no heredan sesión o acceso por cambiar configuración.

Respuestas API, bootstrap, éxito, errores y Set-Cookie: Cache-Control:no-store y
Referrer-Policy:no-referrer; no Cache API/put, cacheEverything o regla CDN que omita
cookies. Headers de estáticos no se presuponen aplicados a respuestas Worker.
No ACAO amplio ni debug/stack/cabeceras de servidor o proveedor en errores.
Verificar Fetch y Workers reales además de mocks del cliente.

Fly público conserva su propia frontera: Origin no demuestra que la petición vino
de Cloudflare; un cliente HTTP puede falsificarlo. No declarar backend inaccesible
directamente sin mecanismo independiente comprobado. Directo sigue exigiendo Auth,
CSRF cuando corresponde y RLS. No añadir credencial universal de proxy por inferencia.

## Contenedor, configuración y TLS

Build context por allowlist y Dockerignore defensivo, no COPY . desde raíz sin
confinamiento. Solo código API, dependencias fijadas y CA pública necesaria;
excluir todos los .env*, .identity-pilot, archivos one-off, VCS, logs, pruebas con
artefactos privados, gestores de credenciales y contenido jurídico. Certificado CA
público revisado no es secreto; no confundirlo con clientcert/key o material Fernet.
Comprobar contenido/capas/artefacto final y scanner redactado antes de publicar.

Secrets se inyectan en runtime por mecanismo privado del proveedor, nunca build
ARG/ENV literal, Dockerfile, fly.toml público, imagen, navegador VITE_* o comando
con valores. Entrypoint no abre dotenv ni registra configuración. Mantener validación
de destino Legalia, rol mínimo exacto, verify-full, passfiledevnull ysslcertmode=disable;
no conexión por service/PG* heredadas o certificados cliente implícitos.

sslrootcert debe apuntar a la CA pública dentro del contenedor revisado, sin fallback
si una ruta macOS del DSN no existe. El operador prepara esa configuración fuera de
salidas visibles; el agente no lee/modifica su valor. CSRF/cipher keys son estables
entre reinicios/releases y custodiadas externamente, no generadas cada arranque.
Cambiar cipher key sin proceso de transición invalidaría custodia existente.

Cliente → Cloudflare y Worker → Fly usan HTTPS validado. Fly puede terminar TLS
antes del listener interno; Secure deriva de configuración aprobada, no de headers
cliente. Uvicorn no confía proxy headers arbitrarios para autorización. Usuario no
root, puerto interno fijo y acceso/logs acotados son parte del artefacto revisable.

## Una VM, un proceso y operación

Preauth, límites y desafíos guardan estado en memoria. Un único worker/proceso por
una VM: sin reload, WEB_CONCURRENCY>1, réplicas automáticas o segunda VM implícita.
min_machines_running=1 es un mínimo, no un máximo: A0 debe comprobar inventario real
y parámetros de creación/deploy, sin asumir que el archivo limita la flota a una.
Escalar/repartir tráfico requiere rediseñar estado compartido y decisión propia.

Reinicio, OOM, autostop y despliegue pueden perder formularios/desafíos/límites en
memoria; el cliente debe recomenzar conscientemente con bootstrap nuevo, sin retry
automático de escritura/OTP ni extensión de sesión. Una VM no es alta disponibilidad.
Autostop/estrategia de actualización, tamaño/región/costo los determina A0 con Arturo;
este informe no selecciona esos parámetros ni garantiza downtime cero.

/api/health actual solo acredita liveness. No usarlo como evidencia DB/Auth/correo
listos. Inicio de producción falla cerrado ante configuración inválida; probes no
leen cuentas reales, generan emails, crean sesiones o requieren secretos en URL.
Readiness operativa requiere prueba separada saneada de conexión/roles/esquema y
recorridos sintéticos autorizados. Migración C03 sigue sin aplicar remotamente;
no prometer guardar perfil profesional por publicar su UI. Retención periódica y
retiro Auth permanecen pendientes, bajo responsabilidad de Arturo.

## Comprobaciones prerelease

| Frontera | Positivo y negativo verificables |
|---|---|
| Cookie pública | Bootstrap HTTPS obtiene ambas __Host separadas y Secure/Strict/Path=/; sin Domain; logout/401 eliminan ambas correctamente |
| CSRF/origen | Origen público+token válido permite request; origen ajeno/ausente o duplicado, bearer, token ausente y cuerpo extra siguen rechazados |
| Proxy | Solo hostHTTPS aprobado recibe; host/URL inyectados, redirect a otro destino y spoofheaders no encaminan privados; API404 no cae en assets |
| Caché | Dos clientes no comparten bootstrap/sesión/respuesta; no-store/referrer sobreviven proxy en2xx/4xx/5xx y ninguna cache rule intercepta API |
| Empaquetado | Imagen/assets/historial de capas sin configuración privada; CA pública en ruta esperada; configuración inválida termina sin secretos/traceback |
| Proceso | Configuración e inventario1VM/1worker; reinicio falla cerrado en preauth y no renueva sesión12h; no se promete HA |
| Backend directo | Misma exigencia Auth/CSRF/MFA/RLS; ningún permiso deriva de Forwarded/Origin/IP o ser proxy |
| Operación | Health liveness separado de evidencia DB/Auth; failclosed con proveedor indeterminado; correo/MFA/revocación aún no se acreditan por deploy |

No repetir credenciales/cookies en reporte, capturas o comandos de prueba. Scanner y
negativos de empaquetado no sustituyen el recorrido HTTPS desplegado; tampoco se
declara verificada versión Auth real por el código de una rama upstream.

## Evidencia y fuentes

Contexto/checkpoints/código de Settings, cookies, middleware, runtime y logging
leídos. Revisión independiente final de fuentes congeladas A1/A4 sin bloqueantes
actuales, después de corregir strip silencioso de Authorization por rechazo403
antes de fetch. Su regresión prueba presencia vacía y cookie/CSRF/Origin válidos
sin contactar upstream. No se editó implementación ajena durante esta revisión.

Artefactos revisados: apps/web/worker/index.ts, index.test.mjs, wrangler.jsonc y
documento Cloudflare; apps/api/Dockerfile, .dockerignore, fly.toml.example,
production.py, test_production_startup.py y documento Fly. Ejecutados por A2:
**43 pruebas sintéticas de producción pasan** y **30 pruebas nativas Node24 Worker
pasan**. Node no estaba en PATH; se usó el runtime existente del escritorio sin
instalar dependencias. HTTP/binding/servidor de pruebas están simulados, sin red.

La fuente Worker mantiene allowlist/config backend vacías: falla cerrado503, no
hay destino Fly inventado. Fly es plantilla sin app/org/región/origen asignados.
Docker no se construyó; Docker/Linux/CA/libpq en imagen, Wrangler/workerd, inventario
Fly, edge con múltiples cookies, TLS/caché/proxy y navegador HTTPS reales aún no
están acreditados. Scanner de imagen/capas y configuración real forman parte de
la publicación coordinada. No ejecución de servicios, lectura de privados,
aprovisionamiento, publicación o aceptación Auth remota por esta revisión.

Fuentes oficiales consultadas2026-10-15: [routing Worker antes de assets](https://developers.cloudflare.com/workers/static-assets/routing/worker-script/),
[Set-Cookie múltiple en Headers](https://developers.cloudflare.com/workers/runtime-apis/headers/),
[headers de activos](https://developers.cloudflare.com/workers/static-assets/headers/),
[cookies y prefijo Host](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Set-Cookie),
[Fly red/puertos](https://docs.fly.io/networking/app-services),
[secrets en runtime](https://docs.fly.io/apps/secrets),
[despliegue y redundancia por defecto](https://docs.fly.io/launch/deploy/),
[checks y efectos de routing](https://docs.fly.io/reference/health-checks/),
[autostop/autostart](https://docs.fly.io/launch/autostop-autostart/),
[Docker build context](https://docs.docker.com/build/concepts/context/).
