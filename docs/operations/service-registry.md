# Registro de servicios de Abogalia

## Destino vigente: Legalia (2026-10-13)

Comprobación2026-10-15: Fly autenticado con la identidad propia de Legalia;
la API de organizaciones identifica slug técnico `personal`, nombre `Legalia`,
mientras el panel usa `/dashboard/legalia`. App `legalia-api` creada y hostname
asignado `legalia-api.fly.dev`; aún sin máquinas ni despliegue. No se deben usar
recursos de otro usuario aunque su organización también se llame personal.
Cloudflare: cuenta `68d5920648c2f57c6ab47e87a07de308`, subdominio existente
`legaliasupport.workers.dev`, cuota Free100000/día comprobados en panel.
`legalia-web` es el nombre previsto; todavía no hay Worker publicado.
Build de imagen previsto en runner estándar Linux del repositorio público y GHCR,
sin Docker local, builder Fly/Depot ni credenciales runtime en CI. El workflow
requiere escaneo de fuentes y ausencia de vulnerabilidades HIGH/CRITICAL antes
de publicar la imagen. No implica haber ejecutado o superado estos controles.

Actualización hosting2026-10-15: Arturo eligió Cloudflare Workers Static Assets
para frontend y Fly.io para FastAPI. Configuración y pruebas locales preparadas;
cuenta Cloudflare, organización/appFly y hostnames reales todavía no confirmados.
No despliegue realizado ni recursos contratados. CLI Fly0.4.118 obtenido del
release oficial y verificado por SHA256 en directorio temporal, ayuda consultada
con HOME vacío; no login ni lectura de credenciales existentes. Las entradas
históricas de hosting propuesto no reabren esta selección.

Arturo cambió el nombre del producto a **Legalia**, creó cuentas independientes
y pidió implementar el esquema aprobado en el proyecto nuevo. Las entradas
Abogalia siguientes conservan evidencia histórica y **no son destinos de runtime**.

| Recurso | Destino vigente | Estado comprobado |
|---|---|---|
| Supabase organización | `tagovxtvdicxjweeerwi`, LEGALIA | Free, panel de Arturo |
| Supabase proyecto | `spohytnxscljtitvmdab`, legalia | Healthy; us-east-1; PostgreSQL 17.11 |
| Auth URL | `https://spohytnxscljtitvmdab.supabase.co` | Destino público; runtime reconciliado sin leer `.env` |
| Identity PostgreSQL | Esquema privado `identity` | Instalado desde SQL Editor; once controles de roles/RLS/grants true |
| Validación de sesión Auth | HTTP D-039 implementado localmente | Revocación real pendiente; no requiere rol probe SQL ni permisos sobre `auth` |
| Resend | Cuenta independiente de Legalia creada por Arturo | SMTP guardado privadamente por Arturo; plantillas instaladas y verificadas en panel; entrega y dominio pendientes |

Security Advisor muestra cero errores y advertencias tras restringir EXECUTE de la
función preexistente `public.rls_auto_enable()`. No se leyó su definición ni se
alteró el trigger. JWT 900 s, OTP 600 s/6 dígitos y Site URL local guardados.
Confirmación de correo requerida; acceso anónimo y linking manual desactivados.
El conector Supabase de esta sesión no pudo acceder al proyecto nuevo; no confundir
la sesión del panel con una nueva conexión MCP autorizada.
Los nombres técnicos ABOGALIA_* y abogalia_identity_* se mantienen por compatibilidad;
no representan reutilización de credenciales. [Evidencia vigente](legalia-supabase-setup.md).

2026-10-15: conexión runtime con TLS verify-full y formato privado verificados.
Una lectura remota exclusiva de catálogo confirmó identidad del rol runtime,
ausencia de privilegios elevados/membresías ascendentes y tres tablas Identity
propiedad del owner con RLS FORCE. C03 aún no instalado; ambos flags de activación
y correo permanecen desactivados. Sin lectura de filas de usuarios ni mutaciones.

## Evidencia histórica de Abogalia

Actualizado: 2026-10-12, America/Mexico_City. Contiene destinos y estados comprobados, sin secretos. Identidad administrativa aprobada: posprojectsupport; en GitHub se conserva la cuenta personal existente.

| Servicio | Destino | Identificador comprobado | Estado |
|---|---|---|---|
| GitHub | ArturoFrancoMozqueda/abogalia | Repositorio público existente | Implementación local Identity en 720c1cf; CI preparado, sin push |
| Desarrollo local | React/FastAPI de Abogalia | Web 127.0.0.1:5190, API 127.0.0.1:8090 | UX/API/sesiones PostgreSQL verificadas localmente; Auth real pendiente |
| Supabase | Organización Abogalia | `jdmkzzkgnzwldthjqtgx` | Creada; Free, `tier_free`, comprobado por conector |
| Supabase | Proyecto abogalia, Free, us-east-1 | `xggefantvuwpilksfdoy` | Creado por Arturo; organización, región y estado ACTIVE_HEALTHY verificados por conector |
| Cloudflare | Cuenta y frontend propios | Pendiente | Sin configurar |
| Fly | Organización y API propias | Pendiente | Sin configurar ni máquinas contratadas |
| Resend | SMTP Free propio de Abogalia | D-034 Approved; espacio/buzón pendientes | Arturo indicó que no existe dominio; piloto con remitente de prueba propuesto, sin configurar |
| Vercel | Sin selección para Abogalia | No aplica | Panel disponible; no se interpreta como cambio de hosting |

## Acceso comprobado

La organización Supabase se creó en el panel con la sesión administrativa de posprojectsupport y plan Free, US$0/mes. El conector `get_organization` devolvió su nombre y plan usando el identificador de esta tabla sin pedir reautenticación. `list_organizations` aún devolvió solo Kova; esa lista incompleta no es prueba de falta de acceso. Confirmar cada destino mediante su identificador y respuesta directa.

El método `get_cost` no estuvo disponible en el servidor del conector. No se confirma ni crea un proyecto por ese método, ni se inventa un ID de confirmación. La creación puede continuar por el panel con costo y región revisados; el usuario deberá completar una nueva contraseña de base si el formulario lo exige.

Formulario preparado tras aprobar D-029: organización Abogalia FREE, proyecto abogalia, East US (North Virginia) us-east-1; Data API habilitada, exposición automática de tablas desactivada y RLS automático activado. Integración opcional de GitHub sin seleccionar. El agente no generó ni introdujo contraseña ni envió el formulario. Arturo completó la creación y avisó «Listo, ya creé el proyecto».

Verificación posterior: `get_project` devolvió `xggefantvuwpilksfdoy`, nombre abogalia, organización `jdmkzzkgnzwldthjqtgx`, región `us-east-1` y `ACTIVE_HEALTHY`. `get_organization` confirmó Free. El panel muestra Healthy, North Virginia, cómputo Nano, sin repositorio GitHub conectado ni migraciones. URL pública del proyecto: https://xggefantvuwpilksfdoy.supabase.co; [panel](https://supabase.com/dashboard/project/xggefantvuwpilksfdoy). Las consultas directas funcionaron con la conexión existente, sin reautenticación; la lista general de proyectos todavía omitía el nuevo destino. No se promete ausencia permanente de login.

`list_tables` para public devolvió cero tablas. Una consulta de catálogo confirmó el event trigger `ensure_rls` habilitado. La revisión de privilegios predeterminados encontró que postgres no concede SELECT/INSERT/UPDATE/DELETE a anon/authenticated para nuevas tablas public, pero conserva otros privilegios, incluidos TRUNCATE; supabase_admin conserva también permisos CRUD predeterminados. No interpretar el checkbox de exposición como eliminación de todos los permisos ni RLS como protección de todas las operaciones. Antes de crear tablas, el diseño de Identity y sus migraciones deben definir explícitamente propietario, grants/revokes y políticas, con pruebas de aislamiento. No se modificaron esos permisos en esta verificación.

Supabase Auth aprobado como proveedor, D-028. Gateway, custodia y UX implementados
localmente con proveedor sintético; integración y autorización reales siguen
pendientes. Proyecto creado no equivale a aplicación conectada.

## Límites de operación

La pestaña Supabase original apuntaba al SQL Editor de Kova Production y la de Fly a secretos de `pos-project-backend`. No se ejecutaron consultas, cambios de secretos ni configuración en esos recursos. La sesión existente de Vercel no selecciona ese hosting para Abogalia. Arturo creó la contraseña y el proyecto vacío de Abogalia; el agente no leyó ni guardó esa contraseña. No se han creado invitaciones, integraciones de GitHub, máquinas ni despliegues.

La aplicación local y su workflow de CI se prepararon tras aprobar D-030. Tras D-031/D-033 se creó el baseline local 1eaf758, sin publicación. [Verificación](local-foundation-verification.md). No se han publicado cambios ni ejecutado CI remoto; los costos de GitHub Actions se revisarán al operar, sin presumir que el cupo se multiplica por repositorio.

Guardar secretos únicamente en archivos locales excluidos o gestores del proveedor y CI. Este repositorio es público: nunca incorporar contraseñas, tokens, claves privadas ni información de clientes. No usar destinos de Kova como valor por defecto o sustitución cuando falte un recurso de Abogalia.


Lectura pública durante Identity (2026-10-12): endpoint JWKS del destino Abogalia
responde con una clave pública ES256. Se registró únicamente disponibilidad, cantidad
y algoritmo; no se leyó material privado ni usuarios, sesiones o configuración Auth.
Esto comprueba acceso a claves públicas, no login, correo, MFA o revocación real.

Tanda 03 (2026-10-12): consulta directa confirmó otra vez Abogalia, organización
jdmkzzkgnzwldthjqtgx, ref xggefantvuwpilksfdoy, us-east-1 y ACTIVE_HEALTHY.
JWKS público respondió con una clave ES256. Sin lectura de claves privadas,
usuarios, sesiones o configuración Auth. La consulta de catálogo por conector no
produjo evidencia interpretable: no se confirma estado nuevo de schema/grants.
D-035 aprueba probar desde frontend local; D-034 selecciona Resend SMTP Free,
sin sobrecostos automáticos. Recursos/configuración/envíos todavía no ejecutados.

D-036 ejecutado parcialmente: esquema privado Identity aplicado mediante migración
atómica identity_owner_runtime_private_schema; tres tablas con RLS FORCE y roles
owner/runtime mínimos comprobados. [Verificación](identity-supabase-verification.md).
Probe diferido: el operador postgres carece de USAGE grantable sobre Auth gestionado.
Sin ampliación de roles administrados, contraseñas, clientes, SMTP o hosting.
D-037: primer commit b30bf7b publicado en codex/identity-design, cabecera remota
verificada. .env creado privado con variables vacías; plantilla pública revisada.
Sin merge o CI remoto confirmado; no interpretar push como despliegue.
