# FastAPI en Fly — paquete de producción preparado

## Estado publicado — 2026-10-15

API https://legalia-api.fly.dev, una máquina started sharedcpu1x/1024MB en iad,
sin volúmenes, builder o réplica. Imagen Alpine3.24/Python3.12.15 del commit
75feda74c617 pasó CI, arranque UID10001/libpq/criptografía y Trivy HIGH/CRITICAL;
no se publicaron las imágenes Debian bloqueadas. Ver service-registry para digest.
Cinco variables runtime importadas privadamente por stdin, sin incluir `.env` en
CI, imagen, argumentos o repo. Health y controles HTTPS directos y mediante
Cloudflare comprobados. Conexión desde VM a PostgreSQL con TLS, rol runtime mínimo
y RLS FORCE comprobada con lectura exclusiva de catálogos.
La aceptación de correo/MFA/revocación y restauración permanece pendiente.
Los apartados siguientes conservan evidencia de la preparación e intentos anteriores.


2026-10-15. Hosting Cloudflare Static Assets + Fly aprobado por Arturo. Esta entrega
prepara fuentes locales; no crea app/organización, contrata recursos, instala CLI,
accede a credenciales, construye/publica imagen ni despliega. El coordinador controla
registro de destinos, inyección privada, CI y ejecución. Kova queda fuera de alcance.

## Artefactos y configuración

- `apps/api/Dockerfile`: Python3.12.15 Alpine3.24 oficial, fijado por digest de
  índice OCI `sha256:1b668429b3511ab407d8e00648891631b0b1a4d7e15e3ca70f38ab5b91ad4ab4`.
  Digest consultado en HTTPS en registry oficial `library/python`, tag3.12.15-alpine3.24,
  el2026-10-15; índice incluye linux/amd64 y linux/arm64. Identidad pública del tag
  contrastada con [official-images](https://github.com/docker-library/official-images/blob/master/library/python).
  Fijar digest impide deriva del tag; no certifica ausencia de vulnerabilidades.
- `requirements.txt` existente, sin editar: pip `--require-hashes --only-binary=:all:`;
  no dev dependencies, compiladores, nuevas dependencias, service_role o secretos.
- Contexto de build **exclusivamente `apps/api`**, con `.dockerignore` denegando todo
  salvo archivos Python de paquetes conocidos, lock y CA pública. No contexto raíz,
  dotenv, Git, venv, tests, fixtures, caches, certificados cliente o claves privadas.
  COPY limitado a requirements, src y certificado público exacto. UID/GID10001 sin
  login, sin home creado; proceso sin root, sin shell de arranque ni volumen de datos.
- `apps/api/fly.toml.example`: plantilla que requiere completar app, región y origen
  reales aprobados. Ningún nombre u organización inventados; no usarla sin completar.
  Una VM shared-cpu-1x/1GB, puerto8080, HTTPS en Fly, sin volumen, release command,
  servicios DB/Redis/Sentry extra ni máquina auxiliar. La plantilla no reserva recursos.
- `abogalia_api.production`: único entrypoint del contenedor. Bind0.0.0.0:8080 solo
  dentro de la máquina, un worker, sin reload/access log/debug/proxy-header trust.
  No lee dotenv. No aceptar argumentos; configuración exclusivamente inyectada.

No Docker/flyctl disponibles en este entorno: **no build ni arranque Linux de la
imagen verificados**. Antes de publicar, construir en entorno autorizado con contexto
limitado, escanear imagen y verificar dependencias/CA/libpq y runtime Linux. El
cliente libpq debe ser>=16; el guard existente falla cerrado antes de conectar.

## Inyección de producción — nombres, sin valores

| Nombre | Contrato |
|---|---|
| ABOGALIA_ENVIRONMENT | production explícito, incluso en bootstrap apagado |
| ABOGALIA_IDENTITY_ENABLED | 0 o1 explícito; ausente/inválido no arranca |
| ABOGALIA_WEB_ORIGIN | Origen HTTPS exacto del frontend Cloudflare aprobado, sin path/query/fragment/credenciales/wildcard; host DNS y puerto443 o implícito |
| ABOGALIA_SUPABASE_URL | Destino Legalia vigente, requerido al habilitar |
| ABOGALIA_SUPABASE_PUBLISHABLE_KEY | Publishable exclusiva del proyecto; nunca secret/service_role |
| ABOGALIA_DATABASE_DSN | Runtime mínimo Legalia, TLS verify-full, password explícito, CA del contenedor |
| ABOGALIA_CSRF_KEY | Clave persistente de firma, al menos32bytes; no regenerar por arranque |
| ABOGALIA_SESSION_CIPHER_KEY | Clave Fernet persistente de custodia; no regenerar por arranque |
| ABOGALIA_AUTH_EMAIL_READY | 0 o1; ausente conserva correo deshabilitado |

Fly permite inyectar secretos como variables **runtime** de la app. Usar gestor o
stdin privado coordinado, nunca argumentos visibles, build ARG/ENV, archivos Git,
logs, prompts o bundles web. Quien puede desplegar código puede acceder a secretos
runtime: restringir ese permiso al espacio Legalia. No usar credenciales de Kova.
No copiar el `.env` local al build ni pedir nuevos valores por chat.

El modo0 sirve health-only bootstrap explícito: requiere producción y origen HTTPS,
construye Settings con cookies Secure/__Host y mantiene Auth indisponible. No activa
flags automáticamente. Al cambiar a1, valida nombres requeridos y usa runtime
existente con rol mínimo y ApiSessionProbe HTTP explícito. No DSN probe SQL ni
fallback; no migración remota implícita. Email permanece según gate configurado.

DSN dentro del contenedor requiere exactamente
`sslrootcert=/app/certificates/supabase-prod-ca-2021.crt`; se empaqueta la CA pública
ya revisada del repo. **La ruta macOS local no funciona en Linux.** El coordinador
deriva privadamente la configuración de Fly con esa ruta, sin imprimir DSN o cambiar
valores locales. No `sslrootcert=system`, `sslmode=require` o TLS deshabilitado como
atajo. Conserva confinamiento existente: Legalia directo o pooler aprobado, puerto5432,
postgres, rol técnico runtime exacto/cualificado, no hostaddr/service/options ni roles
elevados. `PG*` heredadas se rechazan salvo PGPASSFILE que custodia sobrescribe;
sslcertmode=disable interno evita archivos cliente implícitos. Runtime no es owner.

La custodia permanece en Supabase. Mantener CSRF/cipher estables en despliegues;
rotarlos necesita procedimiento propio de invalidación/reconciliación, no nueva
clave al construir o encender la VM. Nada se guarda en disco efímero de Fly como
base de sesiones, salvo código/CA pública instalados.

## Un proceso y una máquina

La preautenticación y challenges MFA son memoria local: **una sola VM y un worker**.
`WEB_CONCURRENCY` ausente o1; otro valor, cualquier UVICORN_*, GUNICORN_CMD_ARGS o
FORWARDED_ALLOW_IPS externo bloquean el arranque. El entrypoint fija opciones y no
confía en cabeceras reenviadas por clientes. Cookies Secure/HttpOnly/__Host y CSRF
usan Settings/origen configurados, no scheme declarado en X-Forwarded-Proto.
Fly termina TLS y fuerza HTTPS; el hop interno es HTTP. Se deshabilitan redirects
por slash para no generar Location con esquema/host internos. No se necesita
confiar `*` en forwarded headers ni CORS amplio; el Worker proxy conserva contrato
same-origin y no cachea Auth. Verificación completa del Worker corresponde a su paquete.

Plantilla desactiva autostop/autostart para evitar pérdida de preauth/MFA por pausa.
Una caída/reinicio/deploy igualmente pierde esas referencias y falla cerrado;
reiniciar formularios/desafíos, sin restaurarlos desde tokens del cliente. No prometer
continuidad ni alta disponibilidad. Estrategia immediate evita convivencia planeada
de releases, a costa de interrupción. Verificar **inventario real exactamente una
máquina** antes/después: el bloque vm define tamaño, no máximo de réplicas.

Fly deploy documenta `--ha` por defecto true. El coordinador debe seleccionar
`--ha=false` y escala exactamente1 en la ejecución autorizada, sin canary/bluegreen,
replicas spare o autoscaler. No se ejecutó CLI; comprobar `--help` de la versión
instalada antes de usarla. No inferir que min_machines_running=1 limita el total.
Región, app, org y costos se registran con destinos reales; no repetir estimaciones
históricas como precio actual ni contratar extras para superar un fallo.

## Diagnósticos, salud y aceptación

Logging y streams Python/FD1/2 quedan suprimidos durante validación/importación y
vida del servidor. Al terminar, solo JSON fijo stopped (exit0) o
production_unavailable (exit2); ningún valor/argumento/excepción cruda. Sin access
logs que filtren query, cuerpos HTTP, bearer/cookies o trazas de proveedor/SQL.
Esto limita diagnóstico; monitorear estado de proceso y salud agregada, no activar
--debug para investigar datos privados. La supresión no prueba ausencia de registros
en proxies/proveedores externos, cuyo contrato debe revisarse por separado.

`/api/health` es **liveness**, tanto con Identity0 como1: no consulta DB/Auth ni
acredita correo, sesiones, RLS, TLS remoto o preparación de negocio. El check HTTP
Fly usa esa ruta interna sin secretos. Pruebas startup no realizan red.

Antes de habilitar tráfico: origen exacto Worker→API, cookies Secure/HttpOnly/SameSite,
CSRF/origen, no-store y rutas proxy, login/correo/MFA reales, JWT/probe y revocación
antes de exp, aislamiento/local/global, DB TLS/rol/RLS y rollback en frontera.
Los harness existentes delimitan cada parte; una pantalla o un mock no declara C02
Done. La autorización de hosting no acredita estos resultados por sí misma.

Retención periódica, cierre/retiro Auth, backups/restore y alertas operativas siguen
pendientes; no hay scheduler o release command que purgue cuentas. Desplegar C03
requiere su esquema aprobado instalado por el coordinador, nunca por startup.
Rollback usa imagen/config previa revisadas y claves compatibles; no revertir datos
ni reactivar sesiones/perfiles retirados por restaurar un backup antiguo. Datos
jurídicos y clientes reales mantienen revisión jurídica/operativa pendiente.

## Verificación de esta entrega

43 pruebas dedicadas pasan con configuración sintética: bootstrap0 sin DB/red,
HTTPS/cookies y rutas exactas, modo1 validado sin connect, matriz de modos/origen,
workers/proxy/PG heredado, proyecto/host/rol/TLS/CA/clave incorrectos, argumentos,
salida Python/nativa y fallo saneados, opciones de servidor y estructura de imagen/
plantilla. Ruff y formato se comprueban antes de freeze. No build Docker, scan de
imagen, fly config validate, CI remoto, aprovisionamiento, secretos Fly o despliegue.
Revisión independiente e integración quedan a cargo de A2/A0.

Fuentes oficiales consultadas2026-10-15: [FastAPI Fly](https://docs.fly.io/python/frameworks/fastapi),
[configuración](https://docs.fly.io/reference/configuration),
[secrets](https://docs.fly.io/apps/secrets),
[cabeceras/proxy](https://docs.fly.io/networking/request-headers),
[deploy/ha](https://docs.fly.io/flyctl/cmd/fly_deploy),
[Docker context](https://docs.docker.com/build/concepts/context/) y
[Uvicorn0.54.0](https://github.com/encode/uvicorn/blob/0.54.0/uvicorn/config.py).
La web Uvicorn no respondió; se verificó código oficial de la versión fijada y
fuente instalada local, sin leer configuración privada.

2026-10-15: build Linux y arranque health-only pasaron en GitHub. Trivy0.76.0
bloqueó la imagen Bookworm por vulnerabilidades HIGH/CRITICAL del sistema base;
no se publicó imagen ni desplegó máquina. Se actualiza la base a Trixie oficial
fijada por digest para repetir build/arranque/escaneo; resultado aún pendiente.

Trixie también pasó build/arranque pero conserva hallazgos HIGH sin corrección
publicada; no se ignoraron ni se publicó. Se prepara Python3.12.15 oficial sobre
Alpine3.24, digest verificado en registry y catálogo official-images, sin cambiar
Python ni dependencias de aplicación. CI debe comprobar compatibilidad musl de
ruedas con hashes, UID10001, libpq>=16, criptografía, arranque y escaneo completo.
