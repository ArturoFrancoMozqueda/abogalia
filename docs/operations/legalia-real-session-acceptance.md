# Aceptación real de sesiones Legalia — herramienta preparada

2026-10-15. C02 / D-039. Implementación local; **no ejecutada contra Legalia**.
No activa Identity, correo ni permisos. No acredita entrega de correo, revocación
real, custodia SQL, navegador, MFA, efectos C03 ni retirada definitiva de cuenta.

## Alcance y ejecución privada

`scripts/verify_identity_auth_sessions.py` es independiente del ejecutor histórico
SMTP. Requiere una cuenta de usuario APP sintética, ya confirmada y exclusiva del
ensayo; nunca cuenta administrativa, del proveedor, de un cliente o compartida.
El cierre global puede retirar otras sesiones anteriores de esa misma cuenta.
El operador atesta esa condición mediante `LISTO` en entrada oculta. En esta entrega
no se confirmó que exista una cuenta disponible; no ejecutar por inferencia.

Desde una terminal interactiva real, con las dependencias Python fijadas del repo:

```sh
apps/api/.venv/bin/python scripts/verify_identity_auth_sessions.py --run
```

Mailbox y contraseña solo por `getpass`, sin eco y sin fallback a stdin legible.
No argumentos con valores, pipes, prompts de agentes ni grabación de terminal.
No pedir nuevos valores `.env`: el parser privado existente obtiene exclusivamente
la publishable del `.env` raíz en runtime (regular0600, dueño actual, sin enlaces,
límite32KiB). El agente no lee ese archivo. No instala configuración en el entorno,
no importa main/runtime ni usa DB, service_role, APIs administrativas o clientes reales.
Destino HTTPS fijo `spohytnxscljtitvmdab`, sin proxies de entorno ni redirects,
timeout10s; puerta de gateway permite solo login password, JWKS y logout.
GET/user usa el adaptador aislado aprobado. No signup, recover, refresh ni correos;
no accede al marcador SMTP ni altera su presupuesto histórico máximo de seis.

## Recorrido y criterio verificable

1. Login A y B: JWT firmado, issuer/audience/TTL900/sub/SID/aal verificados;
   mismo sujeto, SID distintos y ambos positivos por `ApiSessionProbe` HTTP.
2. Logout local A conservando su token original: firma y vigencia siguen válidas;
   HTTP debe reconocer ausencia definitiva, mientras B sigue activo.
3. Login C del mismo sujeto, SID diferente: B y C positivos antes de logout global B.
4. Tokens originales B/C todavía criptográficamente vigentes, pero ambos negativos
   por HTTP tras global; A original continúa negativo. Sin refresh ni reemplazo.

Son tres logins para disponer de dos sesiones vivas antes del cierre global.
No polling, espera a expiración, retry ni fallback. Un timeout, 429, respuesta
indeterminada, JWT vencido/inválido o 403 genérico nunca demuestra revocación.
Solo los códigos definitivos aprobados de ausencia en401/403 se aceptan como
negativo mediante el adaptador existente. Si la versión desplegada sigue aceptando
el token original, la prueba no está verificada y `cleanup_failed` indica una
sesión que permanece activa; conservar bloqueo y revisar contrato,
no inventar éxito ni cambiar proveedor/permisos para obtenerlo.

## Salida y limpieza

Salida JSON con status fijo, nueve checks booleanos con nombres fijos y cleanup
booleano; exit0 solo `verified`, resto2. `verification_unavailable` indica entrada
CLI rechazada; `verification_pending` un recorrido incompleto/no demostrado;
`cleanup_failed` indica limpieza fallida o cierre ambiguo que exige al responsable
comprobar/revocar las sesiones sintéticas por canal privado. La salida no imprime
email, contraseña, JWT, SID, sujeto, cabeceras, payloads ni excepciones. FD1/2,
streams Python y logging se suprimen durante operación; los prompts privados usan
la TTY. La contraseña/tokens existen temporalmente en memoria; Python no promete
borrado seguro de strings y una interrupción abrupta del proceso impide finally.

Finalmente intenta logout **local** solo de sesiones devueltas que no tuvieron
ya intento de logout. Cada intento ambiguo queda consumido: no se repite el mismo
cierre automáticamente. Cierra cliente incluso ante fallos. Si login crea una
sesión y pierde la respuesta, no se conoce su referencia para limpiarla: responsable
Arturo debe retirarla privadamente. No renovación automática ni sesión persistida.
`cleanup=true` exige ausencia definitiva HTTP observada para cada sesión devuelta,
con su token original todavía válido y sin fallos de cierre/cliente. Una sesión
todavía activa, JWT vencido o comprobación indeterminada deja cleanup=false; no
se repite el cierre para forzar éxito. Login ambiguo también deja cleanup=false.
No es un inventario independiente de todas las sesiones del proveedor.

## Evidencia y próximos pasos

Pruebas sintéticas en `apps/api/tests/test_identity_auth_verification.py`, con
MockTransport y firmas efímeras generadas en memoria, sin secretos ni red.
19 pruebas sintéticas pasan; Ruff y formato pasan. Revisión independiente
A1/A5 y revisión A0 sin bloqueantes. Quedan pendientes ejecución real por operador y aceptación del
resultado redactado. Solo después puede diseñarse prueba navegador/API/SQL de
revocación externa conservando cookie local y rollback de negocio en frontera;
esta herramienta no cubre esa aceptación integrada ni eliminación Auth/retención.

Documentación oficial consultada el2026-10-15:
[sesiones](https://supabase.com/docs/guides/auth/sessions),
[signOut](https://supabase.com/docs/reference/javascript/auth-signout) y
[guía avanzada](https://supabase.com/docs/guides/auth/server-side/advanced-guide).
JWT aún vigente y sesión terminada son comprobaciones distintas. La prueba real
sigue siendo necesaria para la versión de Legalia. `changelog.md` devolvió tipo
no admitido; se consultó el [changelog HTML](https://supabase.com/changelog), incluido
aviso TLS del12oct; se conserva validación TLS del cliente, sin downgrade.
