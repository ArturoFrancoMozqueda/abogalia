# C02 — Validación activa de sesión por API

2026-10-14. D-039: Arturo aprobó validación por API. Base338617a91589,
codex/identity-design. Implementación local del contrato aprobado; aceptación
con proveedor real sigue pendiente. No lectura de .env, envío de correos,
credenciales administrativas, SQL remoto, migraciones o cambios de privilegios.

## Comportamiento implementado

SessionProbe.active(sid, subject, *, access_token) recibe siempre el token vigente.
ApiSessionProbe verifica JWT mediante las claves públicas del gateway y exige
subject/SID coincidentes, UUID canónico no nulo, firma/issuer/audience/exp/iat/aal
según verificador vigente. Solo entonces consulta GET /auth/v1/user por HTTPS al
proyecto fijo Legalia spohytnxscljtitvmdab con publishable y bearer custodiado.

GET usa Request independiente, sin cookies, cabeceras o parámetros heredados del
cliente. Sin redirects/reintentos, timeout10s y lectura acotada:64KiB éxito/8KiB
error; rechaza contenido comprimido antes de decodificar. Un 200 exige UUID id igual
al sujeto verificado; no guarda perfil/metadata ni inventa prueba independiente del
SID desde la respuesta. La ligadura SID→token proviene del JWT verificado. No cache
positivo, mapa global SID→token, refresh dentro del probe o fallback JWT/SQL/local.
Se consulta una vez /user por cada frontera de validación, además de llamadas propias
de MFA/factors existentes y obtención de claves públicas para verificar JWT.

401 **o**403 con código exacto session_not_found/user_not_found son los únicos
rechazos HTTP definitivos que devuelven False y permiten purgar custodia. Se corrigió
la restricción inicial a401 tras verificar upstreamAuth: ausencia de usuario/sesión
puede responder403. Otros401/403, timeout,429,5xx,redirect,JSON inválido, identidad
ajena o respuesta excesiva devuelven indisponibilidad, deniegan acceso y conservan
custodia; nunca se consideran revocación por el status solo. Errores no adjuntan
body, código arbitrario, identidad o token del proveedor.

El runtime/launcher seleccionado explícitamente por A0 es HTTP conforme D-039;
no se deduce ese modo por ausencia de DSN probe. A2 adapta solo la firma SQL para
fixtures/compatibilidad, sin enviar tokens a PostgreSQL. La operación normal sigue
requiriendo storage privado mínimo y los gates aprobados; el shim no es fallback.

## Transacciones, renovación y MFA

Login/OTP validan token ligado y sesión activa antes de autorizar. Entrada privada
y frontera anterior al resultado/commit utilizan el token vigente. Si requiere
refresh, primero verifica criptografía/sub/SID del par devuelto y guarda el par
rotado bajo la transacción existente; luego comprueba activamente la nueva sesión.
Un rechazo definitivo borra y confirma antes de401. Un error transitorio se relanza
fuera de la transacción para conservar la renovación consumida, sin extender
inactividad ni devolver contenido. Evita recuperar por accidente el refresh anterior.

El chequeo final revalida tiempo, JWT y sesión. MFA recibe subject/email exclusivamente del registro ya verificado si el proveedor
omite user, sin GET previo al guardado ni inferir identidad desde claims no
verificados. Si user existe pero discrepa, se deniega sin fallback. JWT/sub/SID/aal2
se comprueban antes de guardar; solo la frontera final autoriza la respuesta.
MFA guarda rotación atómica; si
la frontera falla por infraestructura, conserva credenciales verificadas nuevas
bajo la referencia opaca original porque no se entregó la cookie nueva. El resultado
es503 sin secreto/contenido y actividad original. Una revocación confirmada borra
custodia incluso tras rotar digest. Logout global revoca localmente solo tras ambas
fronteras; el proveedor externo se invoca después del commit, sin ampliar alcance.

Esto protege los efectos locales de Identity. No promete revertir efectos ya
aceptados por un proveedor remoto ni contenido entregado antes de revocación.
No implementa negocio/profesionales o prueba de retirada Auth para retención30/90.

## Archivos y evidencia

Propiedad A4: identity/provider.py,service.py,contracts.py,session_probe.py;
tests/test_auth.py,test_identity_integration.py,test_api_session_probe.py; este
informe. Coordinador posee runtime/launcher/docs/locks e integración. A2 revisa
independientemente y mantiene shimSQL. No commits/push por A4.

Primera suite global tras adaptarHTTP:386passed; tras negativos de infraestructura
posterior a renovación y rotaciónMFA:389passed. Tras ajuste401/403 y persistenciaMFA (incluida respuesta sin user):395passed.
Con negativo de discrepancia explícita de identidad: **396passed**, sin fallos. Verificación integrada independiente corresponde a A0. Ruff lint/formato pasan.

Pruebas incluyen JWT no ligado/expirado/sin firma/SIDnulo,1GETporfrontera,sin caché,
allowlist401/403,sujetoajeno,429/5xx/timeout/redirect/body inválido/grande,aislamiento
respecto cookies/headers del cliente. PostgreSQL real aislado verifica cifrado,
refresh,actividad,MFArotación,purga trasrevocación externa simulada y global/local
logout. Auth utiliza MockTransport declarado y sesiones sintéticas; la base local
real no convierte esas respuestas en aceptación de Supabase real. No se imprimen
credenciales efímeras ni materialMFA.

## Verificaciones reales pendientes

Tras configuración privada aprobada, comprobar en Legalia con identidad sintética
autorizada: GET/user positivo y revocación externa antes de expJWT, alcances local/
global,refresh concurrente,MFA y error transitorio. No confundir logout de cookie
local con prueba de revocación del proveedor. Gate operativo y C02Done permanecen
condicionados a esa evidencia, SMTP/correo/retención y revisión independiente.
No se consumió ningún envío del ensayo histórico ni se accedió a clientes reales.

Fuentes públicas consultadas durante checkpoint/revisión:
[guía avanzada Supabase](https://supabase.com/docs/guides/auth/server-side/advanced-guide),
[auth.go upstream](https://github.com/supabase/auth/blob/master/internal/api/auth.go),
[UserGet upstream](https://github.com/supabase/auth/blob/master/internal/api/user.go).
Upstream actual distingue JWT aún válido de sesión ausente; no identifica la revisión
desplegada de Legalia ni sustituye la prueba real. Las garantías dependen también de
la validación propia y los controles transaccionales mantenidos.
