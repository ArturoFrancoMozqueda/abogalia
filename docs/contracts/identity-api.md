# Contrato HTTP — Identity

Fecha: 2026-10-12. Orden T05/A4, revisor A0. Estado: diseño técnico concreto para implementación local, revisión A0 pendiente; **no implementado**. Arturo aprobó continuar y las recomendaciones A de IC-01..IC-06, modelo conceptual y matriz presentados; A0 registra esa aprobación y actualiza sus estados. Los encabezados pendientes de los documentos originales no son evidencia de revocación de esa respuesta. Este contrato no añade tablas de cliente/negocio, retención, recuperación administrativa de factores, proveedor de correo, gasto o despliegue.

Dependencias: [checkpoint](../checkpoints/identity-and-contexts.md), [modelo](../data/identity-model-proposed.md), [matriz](../security/access-matrix-proposed.md). Base compartida `codex/identity-design`, fundación local preservada. Único archivo T05: este documento.

## Superficie y reglas comunes

Web consume exclusivamente `/api/auth/*` del mismo origen mediante cookies de aplicación. Supabase Auth autentica; FastAPI custodia access/refresh tokens y aplica controles propios de sesión. PostgreSQL privado recibe conexiones de runtime con privilegios mínimos, separadas de migración/administración. No acceso de negocio desde navegador a Data API, ni `service_role` universal, ni identidad obtenida de un `user_id` del cuerpo.

Todas las respuestas Auth llevan `Cache-Control: no-store` y `Referrer-Policy: no-referrer`; no caché compartida, prerender ni almacenamiento persistente cliente de respuestas. Cuerpos JSON UTF-8; ningún cuerpo acepta campos desconocidos, rutas de retorno, actor, rol, contexto, JWT, token de refresco o credencial administrativa. Query strings de estas rutas deben estar vacías. No serializar errores de proveedor, validación FastAPI con `input`, cookies, cuerpos sensibles ni cabeceras de autenticación.

Los errores usan exactamente `{ "error": { "code": string, "message": string } }`, con mensajes fijos en español. No `detail`, claims, email, identificadores internos o contenido del proveedor. Rechazo de transporte, validación y middleware debe mantener este formato.

| HTTP | code | message | Uso |
|---|---|---|---|
| 401 | AUTHENTICATION_REQUIRED | Se requiere iniciar sesión. | Sesión necesaria ausente/expirada/revocada |
| 401 | INVALID_CREDENTIALS | No fue posible iniciar sesión. | Contraseña incorrecta, cuenta inexistente o correo no confirmado; sin distinción |
| 401 | INVALID_CODE | El código no es válido o expiró. | OTP incorrecto/expirado/usado; sin distinción de existencia |
| 403 | REQUEST_FORBIDDEN | La solicitud no está permitida. | CSRF/origen incorrecto, bearer de navegador, acceso fuera de contrato |
| 403 | MFA_REQUIRED | Completa la verificación adicional. | Acción profesional/administrativa protegida con assurance insuficiente |
| 403 | FEATURE_UNAVAILABLE | Esta función aún no está disponible. | Recuperación/desinscripción administrativa MFA sin contrato |
| 422 | INVALID_REQUEST | Revisa los datos de la solicitud. | JSON/campos/tipos/formato/tamaño inválidos; no eco del dato |
| 429 | RATE_LIMITED | Inténtalo de nuevo más tarde. | Límite aplicado sin revelar existencia de cuenta |
| 503 | AUTH_UNAVAILABLE | El acceso no está disponible temporalmente. | Proveedor/custodia/verificación no disponible o dependencia sin configurar |

`Retry-After` puede acompañar 429/503 con segundos enteros; no incluye datos de usuario. Límites por IP/preautenticación/identidad normalizada deben tratar intentos de cuentas inexistentes y existentes igual. Umbrales numéricos y política de abuso quedan como configuración revisable de C01/C02 antes de exposición pública; no declarar protección probada con el mero código 429.

Validación del contrato: cuerpos de hasta 8 KiB, `email` string con sintaxis de correo y hasta 254 caracteres; `password`/`new_password` string no vacía hasta 1024 bytes UTF-8, nunca trim ni truncado. Política de fortaleza aprobada/configurada del proveedor es adicional; registro/cambio pueden responder 422 genérico si la rechaza. No normalizar silenciosamente parte local del correo; enviar forma consistente al proveedor y usar su identidad verificada, sin fusionar personas por texto de correo. Códigos OTP/TOTP: string de seis dígitos ASCII, preservando ceros iniciales; si la configuración revisada del proveedor cambia longitud, versionar este contrato antes de usarla. UUIDs: strings válidas, siempre con comprobación de pertenencia.

## Cookies, CSRF y origen

Producción HTTPS:

- `__Host-abogalia_session`: identificador opaco aleatorio de 32 bytes codificado base64url, sin claims ni tokens Supabase. `HttpOnly; Secure; SameSite=Strict; Path=/`, sin Domain. Referencia de preautenticación o sesión; servidor distingue estado y jamás promueve una referencia aportada por el cliente.
- `__Host-abogalia_csrf`: token CSRF firmado, `Secure; SameSite=Strict; Path=/`, sin Domain; puede ser leído por JavaScript. No es credencial Auth ni token Supabase, aunque tampoco debe entrar en logs/URLs. GET `/csrf` también lo devuelve en JSON para evitar depender de parsear cookies en frontend.

Excepción única local: desarrollo HTTP sobre `http://127.0.0.1:5190`, proxy Vite a API. Nombres `abogalia_session`/`abogalia_csrf`, mismas propiedades salvo Secure/prefijo `__Host-`. Solo entorno de desarrollo explícito y loopback; inicio de aplicación falla si se pretende usar esta excepción en producción. HTTPS de producción requiere destino aprobado; ningún dominio se selecciona aquí.

Protocolo de doble envío firmado, derivado de [OWASP CSRF](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html):

1. GET `/csrf` establece una referencia opaca de preautenticación si no existe sesión válida; no autentica ni extiende sesión. Genera nonce aleatorio de 32 bytes. Token `v1.<nonce-base64url>.<mac-base64url>`; MAC HMAC-SHA256 con clave de runtime exclusiva y mensaje con dominio `abogalia-csrf-v1`, clase de referencia y campos de longitud explícita para referencia opaca + nonce. La referencia no aparece en el token; no se usa email/ID estático como vínculo.
2. Respuesta establece cookie CSRF y devuelve `{ "csrf_token": string }`. Si la cookie ya es válida para esa referencia, conserva token para no romper pestañas concurrentes. Frontend mantiene token solo en memoria, envía `X-CSRF-Token` y `credentials: same-origin` en POST.
3. Todo POST, incluido login/register/recover/logout, exige `Content-Type: application/json`, `Origin` exactamente igual al origen configurado (esquema/host/puerto), sin null, ausencia, comodines ni confianza en Host/X-Forwarded-Host no validado. Exige cookie CSRF y cabecera idénticas, formato acotado y HMAC válido ligado a la referencia recibida. Comparaciones de MAC/token en tiempo constante; rechazo antes de llamar proveedor o producir efectos. Origen permitido de tests se inyecta solo en entorno sintético; no fallback a Referer.
4. GET `/csrf` admite fetch del mismo origen: Origin exacto si presente; si no, `Sec-Fetch-Site: same-origin` y `Sec-Fetch-Mode` distinto de `navigate`. Tests internos usan Origin exacto. Ausencia de ambas pruebas devuelve 403. No CORS con credenciales hacia otros orígenes. `/session` nunca exige CSRF y no produce operaciones de negocio; SameSite/no-store y ausencia de CORS protegen lectura desde terceros.
5. Login correcto y elevación MFA rotan referencia opaca e invalidan su predecesora; eliminan cookie CSRF. Frontend vuelve a GET `/csrf` antes de siguiente POST. Logout invalida referencia y elimina ambas cookies; la próxima visita crea preautenticación nueva. CSRF anterior falla tras rotación, aunque una pestaña aún lo conserve. No sesión compartida en un singleton de cliente Supabase.

La referencia de preautenticación expira a los 30 minutos, es incapaz de ejecutar acciones autenticadas y no contiene identidad. Cookie de sesión autenticada expira como máximo a las 12 horas de login; cookie CSRF no excede vigencia de su referencia. La sesión impone límites en servidor aun si el navegador conserva cookies.

## Sesión y estados

`SessionView` es una unión exacta:

```typescript
type SessionView =
  | { authenticated: false }
  | { authenticated: true; user: { id: string; email: string; assurance: "aal1" | "aal2" } };
```

`id` es sujeto Auth verificado; `email` es correo verificado del propio usuario; no perfil, metadata, permisos globales ni factores. `assurance` proviene de sesión/JWT validado y estado vigente, jamás del cuerpo. No devolver `session_id` del proveedor, expiraciones/token, refresh token ni cookie opaca en JSON. JSON de `/csrf` es la excepción explícita para token CSRF de aplicación.

Sesión máxima absoluta 12 horas desde login, inactividad 30 minutos, JWT Supabase máximo 15 minutos. Servidor valida firma/algoritmo/issuer/audience/exp/sub según destino confiable configurado; JWT decodificado no autentica. La configuración real del proveedor debe respetar 15 minutos; emitir JWT superior invalida el flujo y devuelve 503, no se declara cap aplicado por borrar el token temprano.

Solo operaciones autenticadas válidas iniciadas por el usuario actualizan actividad; sondeo `/session` y GET `/csrf` no la actualizan. MFA exitoso rota referencia sin reiniciar reloj absoluto. Renovación Supabase permanece interna, serializada por sesión para impedir perder tokens concurrentemente; no endpoint de refresh que acepte tokens del navegador. Error de renovación/custodia/verificación deniega acceso privado, sin ampliar plazos.

Cada petición privada comprueba revocación local y vigencia necesaria de sesión Supabase; para garantía ante revocación fuera de la aplicación, mecanismo de lectura restringida de estado Auth por A3/A0, sin privilegios administrativos universales. Hasta existir mecanismo probado, no declarar revocación global/proveedor completa. Revocación local precede cualquier retorno exitoso; global invalida todas las sesiones locales del sujeto bajo una versión/referencia de servidor. Peticiones con efecto vuelven a comprobar vigencia en su frontera transaccional. No pueden retirar contenido descargado. No retención de historia de sesión inferida aquí; almacén efímero restringido elimina tokens al expirar/revocar, con diseño de custodia de A3/A0 separado de datos de negocio.

MFA `aal1` puede consultar su estado y gestionar el paso Auth permitido; no permite acciones profesionales/administrativas protegidas. MFA no sustituye permisos. Retirada de Membership retira facultades profesionales derivadas; una participación independiente como cliente se reevalúa por separado, sin crear modelo de negocio en este contrato.

## Endpoints principales

Todos los POST requieren CSRF/origen anteriores; los errores comunes posibles son 403/422/429/503 además de los específicos indicados. GET requiere query vacía. Ninguna ruta acepta `Authorization` del navegador como alternativa: si se envía bearer, responder 403, incluso con cookie válida.

| Método/ruta | Cuerpo exacto | Precondición | Éxito | Específico |
|---|---|---|---|---|
| GET `/api/auth/session` | Sin cuerpo | Cookie opcional | 200 `SessionView` | Sesión ausente/expirada/revocada → 200 `{authenticated:false}` y limpiar cookies inválidas; dependencia necesaria caída → 503 |
| GET `/api/auth/csrf` | Sin cuerpo | Bootstrap del mismo origen | 200 `{csrf_token:string}` y cookie | No inicia sesión ni la prolonga |
| POST `/api/auth/login` | `{email:string,password:string}` | Preautenticación o sesión válida | 200 `SessionView` con authenticated:true; cookie nueva | 401 INVALID_CREDENTIALS uniforme; proveedor no confirma email → mismo 401 |
| POST `/api/auth/register` | `{email:string,password:string}` | Preautenticación o sesión válida | 202 `{accepted:true}` | Cuenta existente y nueva mismo cuerpo/estado; no cookie autenticada ni user ID |
| POST `/api/auth/recover` | `{email:string}` | Preautenticación o sesión válida | 202 `{accepted:true}` | Presente/ausente mismo resultado; no envía credencial a navegador |
| POST `/api/auth/logout` | `{scope:"local"\|"global"}` | Cookie válida + CSRF; preautenticación admisible solo local | 204 sin cuerpo; cookies expiradas | Global sin sesión autenticada → 401; local ya sin autenticación → 204 |

Login reemplaza la sesión de este navegador solo después de verificar credenciales y crear custodia nueva; fallo no autentica ni cambia usuario vigente. Login de usuario con factores enrolados entrega `aal1` hasta verificación MFA; no impedir acceso al propio flujo MFA. Registro y recuperación no exponen respuesta cruda del proveedor; errores de duplicado se normalizan a 202. Fallos de infraestructura sí devuelven 503 independientemente de existencia; no inventar `accepted:true` si no hay camino configurado para cumplir el flujo.

Logout revoca primero la referencia local; llamadas posteriores con ella fallan aunque cierre de proveedor falle. Solo 204 si se completó el alcance pedido; fallo posterior del proveedor devuelve 503 y mantiene cookies eliminadas y revocación local efectiva. Reintento global tras perder sesión no se promete idempotente por cookie borrada; UI informa fallo parcial y requiere nuevo acceso o intervención aprobada, sin afirmar cierre de todos los dispositivos. No invocar signout global por omisión de scope del SDK.

## Confirmación y recuperación sin credenciales en URL

Para implementar el recorrido completo con el contrato aprobado se proponen estos POST adicionales, sujetos a revisión técnica de A0 y configuración de correo antes de habilitar:

| Método/ruta | Cuerpo exacto | Precondición | Éxito/efecto | Error específico |
|---|---|---|---|---|
| POST `/api/auth/confirm` | `{email:string,code:string}` | CSRF/preautenticación | 204; verifica OTP `type=email`, confirma correo; descarta/revoca sesión temporal y requiere login normal | 401 INVALID_CODE |
| POST `/api/auth/recover/complete` | `{email:string,code:string,new_password:string}` | CSRF/preautenticación | 204; verifica OTP `type=recovery`, actualiza contraseña, revoca sesiones del sujeto y elimina cookies del navegador; requiere login normal | 401 INVALID_CODE; 422 por contraseña no aceptada; 503 si no completa actualización/revocación |

El código se pega en formulario y viaja únicamente en body JSON por HTTPS; no enlaces con `token`, `token_hash`, JWT, contraseña o código, ni fragmentos/query, redirecciones o logs que los capturen. Sesión que Supabase emita al verificar recuperación se custodia temporalmente solo para actualizar contraseña; nunca se convierte en acceso profesional o sesión general de aplicación. Cambio de contraseña y revocación se tratan como etapas explícitas: fallo posterior al cambio no promete reversión ni permite reutilizar OTP consumido. UI indica 503 y requiere iniciar sesión con contraseña nueva para gestionar cierre autorizado; prueba de esta excepción antes de publicar.

Compatibilidad oficial: [Python verify_otp](https://supabase.com/docs/reference/python/auth-verifyotp) documenta `email` y `recovery`; [reset_password_for_email](https://supabase.com/docs/reference/python/auth-resetpasswordforemail) envía por defecto un enlace y no cambia contraseña; [plantillas Auth](https://supabase.com/docs/guides/auth/auth-email-templates) ofrecen `Token` para código enviado por correo. Por ello el formulario por código requiere plantilla revisada que muestre OTP y no `ConfirmationURL`/`TokenHash` en URL. No se habilita con la plantilla predeterminada ni se simula que `reset_password_for_email` ya devuelve un OTP al navegador. Configuración de correo propio/hook y plantillas continúa pendiente, sin seleccionar proveedor. Free nuevo limita personalización con correo default y éste no sirve para registro público.

No hay callback activo en este contrato: el código pegado elimina necesidad de transportar secretos por URL. Si una limitación de versión/proveedor obliga a callback PKCE/enlace, A0 debe revisar contrato y privacidad del transporte antes de implementarlo; no añadir GET que cambie contraseña o consuma credencial por inferencia. UX puede tener ruta de confirmación/recuperación sin parámetros sensibles.

## MFA TOTP

Rutas con CSRF y sesión autenticada de aplicación; factor/challenge deben pertenecer al sujeto y sesión vigente. No acepta teléfono, user_id ni códigos de recuperación administrativa.

| Método/ruta | Cuerpo exacto | Éxito | Reglas |
|---|---|---|---|
| GET `/api/auth/mfa/factors` | Sin cuerpo ni query | 200 `{factors:Array<{id:string,status:"verified"\|"unverified"}>}` | Solo factores TOTP del propio sujeto; necesario para volver a desafiar un factor existente tras login; sin secretos/URI/metadata |
| POST `/api/auth/mfa/enroll` | `{}` | 201 `{factor_id:string,totp:{qr_code:string,secret:string,uri:string}}` | Enrolamiento TOTP no verificado; `secret`/URI/QR solo en flujo dedicado privado de configuración; nada de logs, caché, analytics, URL de navegación o persistencia cliente |
| POST `/api/auth/mfa/challenge` | `{factor_id:string}` | 200 `{challenge_id:string,expires_at:number}` | IDs propios; expires_at unix segundos del proveedor; factor ajeno → 403 genérico sin revelar existencia |
| POST `/api/auth/mfa/verify` | `{factor_id:string,challenge_id:string,code:string}` | 200 `SessionView` con assurance:aal2; referencia rotada | Verifica challenge vigente de la misma sesión y factor; rechaza challenge ajeno o código inválido; actualiza custodia interna con sesión elevada |
| POST `/api/auth/mfa/recover` | Cualquier solicitud se rechaza | 403 FEATURE_UNAVAILABLE | No recuperación de factor aprobada; no bypass por correo/soporte |
| POST `/api/auth/mfa/unenroll` | Cualquier solicitud se rechaza | 403 FEATURE_UNAVAILABLE | Desinscripción necesita contrato de reautenticación/efecto y recuperación; no implementada por comodidad |

Enrolamiento genera un secreto de configuración necesario para el usuario en su flujo Auth aprobado: esta respuesta específica no autoriza mostrarlo en herramientas/chat/reportes. `qr_code` se renderiza como imagen privada; no HTML/SVG inyectado sin validar. No volver a obtener secretos del factor después de la entrega inicial. Cada endpoint requiere proveedor real/configuración soportada o devuelve 503; un mock o bandera `aal2` local no acredita MFA.

Basado en [enroll](https://supabase.com/docs/reference/python/auth-mfa-enroll), [challenge](https://supabase.com/docs/reference/python/auth-mfa-challenge), [verify](https://supabase.com/docs/reference/python/auth-mfa-verify) y [guía MFA y listado de factores](https://supabase.com/docs/guides/auth/auth-mfa). La biblioteca/versión elegida debe contrastarse antes de código, incluido el método Python para listar factores (la ruta de referencia consultada no estuvo disponible); contrato externo no depende de serializar respuestas SDK completas.

## Aceptación y entrega

- OpenAPI refleja métodos, cuerpos, unión de sesión y errores; pruebas frontend/API verifican contrato, sin fixtures con valores reales.
- Sin bearer alternativo, tokens Supabase/metadata en JSON, ni eco de contraseña/OTP en errores; prueba con marcadores sintéticos en todos los paths y fallos de proveedor/middleware.
- Login CSRF y POST sin Origin/CSRF válido se rechazan antes de efectos; token firmado de otra sesión/preautenticación, subdominio y predecesor rotado fallan. Login/logout/MFA no reutilizan referencia opaca anterior.
- Reloj sintético comprueba 12 horas/30 minutos y polling sin extensión; JWT >15 minutos falla; renovación concurrente, fallo de custodia y revocación global/local no conceden acceso residual.
- Registro/recover presente/ausente normalizan respuesta; SMTP sin configurar devuelve 503 honesto. OTP expirado/reutilizado/ajeno falla; confirmación no autentica automáticamente y recuperación no concede privilegios.
- MFA incompleto bloquea acciones protegidas; factor/challenge ajeno falla; retiro/recuperación queda cerrado. El estado cliente no sustituye permiso profesional.
- Antes de datos reales: custodia/persistencia/revocación de sesión verificadas, mecanismos de consulta Auth con privilegios mínimos, revisión de secretos redactada, correo y tratamiento aprobados, retención aplicable y revisión independiente. LEGAL REVIEW REQUIRED donde corresponda.

Verificación T05: documentación oficial pública revisada el 2026-10-12; contrato documental preparado. Sin código, tablas, SQL, instalación, `.env`, conexión de proyecto, secretos reales, correo enviado, tests de runtime, CI remoto o despliegue. Protocolo CSRF concretado para revisión A0; umbrales de abuso, custodia física y configuración del proveedor/correo son dependencias materiales, no controles declarados implementados.
