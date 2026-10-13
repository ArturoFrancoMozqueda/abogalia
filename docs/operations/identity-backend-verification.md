# Verificación local de backend Identity — A4/C02

Fecha: 2026-10-12. Rama/worktree asignado de backend desde baseline
`1eaf758d776a77e0507629c9e33c6c1d969bee79`; sin commit ni integración por A4.
Implementación local técnica, C02 todavía no Done. D-031/D-032/D-033 y T05
constituyen autorización; no se seleccionaron proveedores, gasto, hosting o datos
jurídicos adicionales.

## Cambios

- `identity/config.py`: Settings inyectadas explícitamente, repr sin campos,
  origen exacto, excepción HTTP loopback acotada, destino Supabase fijo Abogalia,
  publishable moderna y clave CSRF de runtime. Sin `.env` ni lectura de variables
  existentes; A0 integra carga runtime y PostgreSQL por separado.
- `identity/security.py`: referencias aleatorias/digests, doble envío CSRF
  HMAC-SHA256 ligado a referencia/clase, JWT PyJWT ES256/RS256 con JWKS confiable,
  algoritmo/firma/issuer/audience/sujeto/sesión/AAL/iat/exp y cap de 15 minutos.
  No claves aportadas en headers JWT ni metadata editable para autorizar.
- `identity/provider.py`: gateway HTTPX a GoTrue, sin SDK state compartido,
  redirects o proxies de entorno; errores sanitizados. Login, refresh, signup,
  OTP, cambio de contraseña, scope explícito de logout y TOTP. No llamadas reales
  a Supabase ejecutadas por A4.
- `identity/service.py`: contrato SessionStore/SessionProbe inyectado; límites
  absolutos 12 horas e inactividad 30 minutos; polling no extiende actividad;
  refresh dentro de transacción; revocación local antes de llamada externa y
  revocación por sujeto para recuperación verificada. Creación fija hora al inicio
  de login, antes del proveedor, para cutoff concurrente de logout global.
- `identity/logging.py`: filtro de `uvicorn.access` elimina rutas Auth incluso
  codificadas antes de formatear; HTTPX/HTTPCore sin nivel debug. La operación debe
  conservar `--no-access-log` y ninguna instrumentación de cuerpos/cookies.
- `routes/auth.py` y `main.py`: endpoints T05, cuerpo acotado a 8 KiB, JSON sin
  atributos ajenos, origen/CSRF, rechazo de query y Authorization del navegador,
  errores uniformes sin `input` de Pydantic, no-store/no-referrer. Cookies
  HttpOnly/Secure/SameSite Strict, rotación de login/MFA y eliminación al logout.
  `create_app(settings=None, store=None, probe=None, provider=None, clock=None)`
  permite inyección; defaults mantienen health y sesión anónima, Auth incompleta503.

MFA verifica factor propio y desafío ligado a provider_session_id/factor/expiración,
consumido antes de verificar incluso ante fallo. Rotación guarda nuevo digest en
la misma transacción SQL, conserva subject/provider_session_id/created_at.
MFA requerido no equivale a permisos profesionales implementados; no existen
endpoints de contenido profesional en este bloque. Recuperación/desinscripción
administrativa MFA continúa403.

Registro/recuperación sin correo compatible configurado devuelven503. OTP se recibe
únicamente en body y requiere plantilla de código/correo aprobada; no callback que
transporte credenciales en URL. Respuestas de proveedor no se serializan al navegador,
salvo proyección dedicada de configuración TOTP dentro del flujo Auth autorizado;
ningún secreto/factor real fue creado en estas pruebas.

## Evidencia ejecutada

Ejecutado en worktree backend con intérprete compartido Python 3.12 y dependencias
fijadas del baseline, `PYTHONPATH=apps/api/src`:

- Ruff lint y formato de los archivos propios: pasan.
- Pytest de `test_auth.py`, `test_jwt.py`, `test_csrf.py`: **73 pruebas pasan**.
  Transporte GoTrue simulado con HTTPX MockTransport, claves/tokens sintéticos
  efímeros generados en memoria, SessionStore en memoria exclusivo de tests.
  Ejecución sin traceback de input o valores sensibles.
- Casos: credenciales/errores, respuestas mínimas, límites de sesión con reloj,
  refresh concurrente serializado, proveedor/probe/store caídos, revocación
  local/global, recuperación sin acceso automático, CSRF/origen/query/bearer,
  límites de cuerpo, firma/claims/JWT mayor de15min, MFA sesión ajena/replay,
  rotación sin extender plazo, cookies y filtro de access logs.
- Correcciones de revisión A5: códigos de proveedor en allowlist explícita,
  duplicado/desconocido normalizados a202, contraseña débil422 y SMTP/configuración
  inválida503; rechazo definitivo de refresh purga tokens con commit antes401,
  infraestructura503 no renueva actividad. OpenAPI declara unión de sesión y
  errores uniformes con modelos mínimos. Frontera posterior a llamadas MFA
  revalida sesión/tiempo/probe y elimina custodia antes401, sin devolver secretos
  si Auth revoca o se cruza límite durante enrolamiento/desafío. Pruebas
  deterministas incluyen rollback fiel del store en memoria; SQL integrado aún
  corresponde a A0/A3. Bootstrap de sesión caducada también confirma eliminación
  antes de emitir el error/crear preautenticación nueva.
- Revisión adicional: el doble de tests ahora elimina por digest vigente tras
  rotación, igual que `_Transaction.delete` SQL. Negativo nuevo revoca probe en
  frontera posterior a la rotación MFAverify:401 y cero filas de custodia,
  sin asumir que un doble con digest original demuestra la eliminación real.
- Revisión A2: logout global requiere JWT/sesión/probe vigentes, con comprobación
  inicial y de frontera antes de revocar bajo el mismo lock; llamada externa
  ocurre después del commit. Cookie A retirada en Auth no puede eliminar nueva
  sesión B del mismo sujeto. Se elimina solo custodia inválida A y devuelve401;
  logout global válido elimina todas las locales aun si proveedor falla después503.
  También probado retiro de Auth entre comprobación inicial y frontera:401
  conserva B y no invoca cierre externo.
- Renovación seguida de acción fallida: el par nuevo se guarda y confirma antes
  de relanzar el error fuera de la transacción; actividad se actualiza solo tras
  éxito y comprobación final. Factor ajeno403 y OTP incorrecto401 próximos al
  vencimiento conservan el refresh nuevo, actividad original y acceso posterior
  válido sin segunda renovación. Esto evita rollback de un token de refresh ya
  consumido en el proveedor; A0 verificará también con PostgreSQL real.

Una advertencia de deprecación de Starlette TestClient/HTTPX se emitió; no se
instaló otra dependencia ni se cambió el lockfile. Se conserva como límite de
herramientas de pruebas de este baseline, para revisión de A0.

## Límites y siguientes comprobaciones

Las pruebas de almacén en memoria **no prueban SQL/RLS/roles ni aislamiento real**.
A3 implementa storage y prueba PostgreSQL; A0 integra ambos y realiza recorrido
web → API → PostgreSQL. A4 no creó/ejecutó tablas, migraciones o grants remotos.

Referencias de preautenticación y desafíos MFA están acotados a 10,000 entradas
por proceso y expiran; no contienen tokens de Supabase. Un cambio de worker o
reinicio falla cerrado y requiere nuevo bootstrap/desafío. No son sesión Auth
persistente y el límite de capacidad no se presenta como política completa de
abuso. Para varios workers se requiere coordinar esa custodia temporal o afinidad
probada antes de publicar; umbrales por IP/cuenta quedan para revisión operativa.

Persistencia autenticada solo usa SessionStore; sin store/probe configurado no se
acepta sesión privada. El callback mínimo para comprobar `auth.sessions` y la
configuración JWT real del proveedor deben estar disponibles y probados antes de
usar usuarios reales. No se verificaron sesiones/MFA/correo en proveedor real,
CI remoto, deploy, restauración ni secret scan final de integración por A4.
C01 y revisión independiente A0/A2 deben ejecutarse antes de commit/push.

No leerá ni devolverá valores de `.env`, credenciales, datos de clientes o Kova.
No se escogió retención jurídica o responsabilidad legal. Uso de datos reales y
tratamiento: LEGAL REVIEW REQUIRED según los checkpoints aplicables.

## Fuentes técnicas públicas

Consultadas el 2026-10-12: [GoTrue OpenAPI oficial](https://github.com/supabase/auth/blob/master/openapi.yaml),
[JWT Supabase](https://supabase.com/docs/guides/auth/jwts),
[MFA](https://supabase.com/docs/guides/auth/auth-mfa),
[plantillas OTP](https://supabase.com/docs/guides/auth/auth-email-templates),
[errores Auth](https://supabase.com/docs/guides/auth/debugging/error-codes),
[PyJWT 2.15.1](https://pyjwt.readthedocs.io/en/stable/usage.html) y
[OWASP CSRF](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html).
Skill Supabase aplicada desde la fase de diseño. Los esquemas oficiales orientan
gateway y validaciones; el transporte mock no demuestra compatibilidad del
proyecto real o de una versión GoTrue desplegada.
