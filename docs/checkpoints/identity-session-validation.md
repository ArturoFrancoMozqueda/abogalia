# Checkpoint — Validación activa de sesiones Identity

Fecha: 2026-10-13. C02, A2/A3. Estado **Proposed / Awaiting decision**.
Base eba6cbedb631; nombres técnicos preservados. Revisor independiente A4.
La aprobación IC-05 exige revocación efectiva en la siguiente petición privada;
esta propuesta cambia la fuente técnica de esa comprobación, no su garantía.

## Lo que entiendo

Legalia tiene sesiones locales custodiadas por API y tablas privadas instaladas.
La conexión SQL probe requiere USAGE auth y SELECT(id,user_id) auth.sessions.
El operador postgres tiene SELECT grantable de columnas pero no USAGE grantable
de auth; PUBLIC tampoco tiene USAGE. 003 permanece sin aplicar. No activar acceso
privado reduciendo revocación a firma/exp JWT o consulta de una sesión local.

La documentación oficial actual distingue getClaims() de getUser(): la consulta
de usuario al servicio puede detectar terminación de sesión en servidor.
[Guía avanzada Auth](https://supabase.com/docs/guides/auth/server-side/advanced-guide).
Existe una alternativa HTTP sin conceder acceso a esquemas administrados.
Falta comprobar el comportamiento en la versión realmente desplegada de Legalia.

## Decisiones tomadas

Se mantienen IC-05/IC-06 y D-031: API custodia tokens, cookie opaca HttpOnly,
firma/iss/aud/exp/session_id/aal verificados, JWT900s, aplicación12h/30min,
CSRF/origen, MFA y comprobación al entrar y antes del resultado/commit privado.
No nuevos roles profesionales, Data API del navegador o credenciales administrativas.
Supabase permanece proveedor. Proyecto vigente spohytnxscljtitvmdab, organización
tagovxtvdicxjweeerwi; destino fijo y TLS. Los identificadores públicos no son secretos.

## Decisiones pendientes

**Una decisión acotada para Arturo:** ¿Aprobamos usar GET /auth/v1/user del proveedor
con el token custodiado como fuente de validación activa, condicionada a pruebas
reales de revocación en Legalia, o conservamos el probe SQL hasta conseguir un
grantor legítimo de USAGE auth?

- **A recomendada, HTTP:** implementar y probar un adaptador de getUser con
  controles abajo. No crear probe SQL ni eliminar sus gates por ausencia de DSN;
  seleccionar explícitamente el mecanismo aprobado. Menos privilegios SQL, más
  dependencia del servicio Auth y carga/latencia por comprobación.
- **B SQL:** mantener contrato actual y bloqueo hasta obtener USAGE de un grantor
  legítimo por un mecanismo confirmado del proveedor. No prometer disponibilidad
  de soporte ni conceder membresía a roles administrados para resolverlo.

Si la prueba real de A no demuestra revocación, conservar fail-closed y decidir
entre B o continuar deshabilitado. No hay fallback automático a JWT/local/cache.
No se reabre el límite 30/90 ni se decide mantenimiento por esta elección.

## Diseño propuesto

API valida criptográficamente el token actual y coteja sub/session_id con el registro
custodiado. El adaptador hace GET al destino fijo `.../auth/v1/user` con publishable
pública y bearer custodiado, exclusivamente en cabeceras HTTPS del flujo Auth.
Nunca en URLs, herramientas visibles, logs, cookies legibles por JS o artefactos.
Un 200 solo vale con objeto de usuario válido y UUID id igual al sujeto verificado.
La respuesta getUser no contiene una nueva prueba independiente del SID: se exige
el mismo token firmado previamente ligado al SID esperado y comprobado por Auth.
No aceptar JWT sin session_id, session_id nulo/ajeno o identidad derivada de metadata.

Contrato propuesto antes de código:
`SessionProbe.active(provider_session_id, subject, *, access_token) -> bool`;
`ApiSessionProbe` usa el transporte aislado del gateway existente. Se cambian
call sites de login, entrada de operación y frontera de resultado; cada llamada
usa el token vigente tras cualquier refresh/MFA. No mapas globales SID→token,
almacenamiento extra o refresh durante el probe. El adaptador SQL puede mantener
su consulta, con firma compatible, si se elige B de forma explícita.

Una consulta HTTP por cada frontera existente, sin caché de resultado positivo.
No duplicar un GET dentro de una misma comprobación. Timeout/429/5xx/JSON inválido,
redirect o respuesta excesiva nunca permiten acceso; distinguir sesión rechazada
de proveedor indisponible con categorías fijas. Conserva rechazo antes de devolver
contenido y semántica transaccional/refresh del servicio.
Solo códigos definitivos de sesión/usuario ausentes en allowlist, sobre token
verificado, pueden limpiar custody; un 403 genérico no es prueba de revocación.
Conservar la sesión local ante errores de infraestructura, denegando la operación.
No callback asíncrono que
considere válida una operación mientras sigue consultando Auth. Respuestas y trazas
no incluyen payload del proveedor. Sin reintentos automáticos de refresh/logouts.

La [documentación de sesiones](https://supabase.com/docs/guides/auth/sessions)
relaciona session_id con auth.sessions y explica que cierre elimina las filas
afectadas, mientras JWT emitidos pueden seguir vigentes. El código público actual
de [Auth requireAuthentication/maybeLoadUserOrSession](https://github.com/supabase/auth/blob/master/internal/api/auth.go)
carga la sesión reclamada y rechaza su ausencia; [UserGet](https://github.com/supabase/auth/blob/master/internal/api/user.go)
devuelve el usuario autenticado. Es evidencia de código upstream consultado hoy,
no prueba de la versión desplegada: master cambia y no se conoce aquí su revisión
exacta en Legalia. La prueba del proyecto es obligatoria antes de habilitar A.

## Datos afectados

Mismos tokens ya cifrados y mismo registro de sesión. HTTP obtiene temporalmente
el usuario autenticado; retener únicamente identidad mínima necesaria, sin copiar
perfil/metadata a negocio o auditoría. No nuevo esquema ni retención de respuestas.
La variable AUTH_SESSION_CHECK_DSN dejaría de ser requerida solo en modo HTTP
explícitamente aprobado; no editar su valor ni leer .env. Runtime DB sigue siendo
rol mínimo, independientemente de cómo se verifica Auth.

## Seguridad

Pruebas locales del adaptador mediante MockTransport declarado: éxito/sujetoajeno,
SID y sub cruzados/sin firma/expirado, clave/algoritmo erróneo, respuesta mal formada,
429/timeout/redirección/5xx, y marcadores sintéticos ausentes de respuestas/logs.
PostgreSQL real conserva RLS, grants, bloqueo de usuario, cutoff y rollback;
concurrencia refresh/revocation/global logout y frontera pos-yield deben seguir
fallando si desaparece sesión. Comprobar número de llamadas por frontera y token
rotado correcto, sin cachear sesiones entre usuarios o reutilizar clientes con
estado mutable de bearer. No acceso directo del navegador a Auth tokens.

Aceptación **proveedor real separada**, con identidad sintética autorizada y sin
capturas/volcados de tokens:

1. Login válido, JWT aún no vencido y comprobación HTTP positiva.
2. Terminar esa sesión en Auth fuera de la eliminación de cookie local; la siguiente
   petición privada con referencia local conservada debe negarse por validación
   activa antes de exp JWT. Un mero logout local no acredita esta prueba.
3. Dos sesiones del mismo sujeto: alcance local conserva la otra; global invalida
   ambas; recuperación de contraseña sigue el alcance aprobado.
4. Revocación durante operación ya iniciada bloquea la frontera del resultado y
   revierte el efecto de negocio; renovación concurrente no recupera sesión retirada.
5. Error/transitorio de Auth no devuelve contenido ni borra silenciosamente una
   sesión local válida como si fuera revocación confirmada.

Guardar solo nombres de escenarios/booleanos/conteos/versión pública si disponible.
No crear usuarios o enviar correos por esta propuesta. Cerrar evidencias sin consumir
ensayos OTP adicionales innecesarios; máximo aprobado de seis mensajes se conserva.

## Impacto futuro

El mecanismo HTTP mueve tráfico de verificación al proveedor; puede requerir ajustar
timeouts, capacidad y medición de latencia antes de escalar, sin decidir tier/gasto.
No sustituye control de cuenta/membresía vigente ni revoca contenido ya entregado.
Validar tras cambios del proveedor. Retirada definitiva Auth y purga de cuenta a30d
siguen un contrato distinto: getUser que rechaza sesión no demuestra identidad
eliminada o imposibilidad de un nuevo login. Backups/restore pendientes.

## Implementación propuesta

Tras aprobar A: A0 coordina contratos/runtime/gates; A4 implementa adaptador y calls;
A2 revisa frontera/retención y A7 prueba PostgreSQL+transporte sintético. Orden de
archivos exclusivos antes de editar; no modificar SQL administrado. Actualizar
documentación/API y readiness para expresar mecanismo elegido y evidencia real
pendiente, sin afirmar que 003 se aplicó. Antes de aprobación solo este checkpoint
y la investigación pública. No implementación, secretos, SQL remoto o commits
en esta entrega. LEGAL REVIEW REQUIRED antes de operación con datos jurídicos.
