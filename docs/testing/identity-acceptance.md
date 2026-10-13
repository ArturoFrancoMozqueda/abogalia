# Identity — Estrategia de aceptación T07

Fecha: 2026-10-12. A7 en modo diseño; revisor A0. Único archivo de esta orden.
Estado: **estrategia preparada; ninguna suite implementada o ejecutada**.

## Alcance autorizado y fuentes

La orden vigente de A0 comunica que Arturo aprobó las recomendaciones A del
[checkpoint](../checkpoints/identity-and-contexts.md),
[matriz](../security/access-matrix-proposed.md) y
[modelo](../data/identity-model-proposed.md), además de continuar el desarrollo.
Retención comunicada: 30 días para cuenta/membresía terminadas y 90 días para
auditoría. A0 debe sincronizar sus estados y esos parámetros en las fuentes:
los borradores leídos aún dicen Proposed/retención pendiente. Esta estrategia usa
la autorización comunicada, sin modificar esos archivos ni inventar nuevos IDs de
decisión. Approved sigue sin significar Implemented.

Contratos dependientes: [T05 API](../contracts/identity-api.md) y
[T06 UX](../ux/identity-flows.md), leídos y conciliados al cerrar T07. Los endpoints, errores
y campos definitivos se tomarán de T05; las acciones visibles y estados accesibles,
de T06. No duplicar un contrato HTTP inventado aquí.

Se conservan IC-01 correo/contraseña/confirmación y recuperación; IC-02 identidad
multifunción, práctica propia y un despacho; IC-03 propiedad por contexto y
participación acotada; IC-04 invitación aceptada, facultades específicas y salida
multifunción; IC-05 cookie opaca, custodia API, MFA profesional/administrativo,
JWT 15 minutos, sesión absoluta 12 horas e inactividad 30 minutos; IC-06 API/SQL
con runtime mínimo y RLS. C01, wrapper redactado y baseline revisado, preceden
distribución de código por A0. Esta orden no instala dependencias, ejecuta SQL,
lee configuración sensible ni accede a proveedores.

## Niveles de evidencia

| Nivel | Real en la prueba futura | Simulado explícitamente | Qué permite afirmar |
|---|---|---|---|
| Reglas unitarias | Reloj controlado, verificador criptográfico y decisiones de acceso/estado | Transporte Supabase y respuestas de claves/sesión/factor, cuando corresponda | Regla probada para entradas concretas; no compatibilidad real del proveedor |
| Integración local | FastAPI, persistencia/sesión de aplicación, PostgreSQL, migraciones y roles reales sujetos a grants/RLS | Solo frontera HTTP de Supabase con dobles de transporte; sin mock del repositorio, SQL o autorización | Flujo local API/base y aislamiento reales con Auth simulado |
| E2E local | Navegador, web/API, cookie y CSRF reales, persistencia/PostgreSQL | Supabase mediante transporte de prueba aislado y declarado | Recorrido local integrado y UX; no correo/MFA real del proveedor |
| Proveedor real | Auth/renovación/cierre/MFA/entrega permitida contra entorno Abogalia autorizado y sintético | Ninguna llamada Auth cubierta por este rótulo puede estar simulada | Evidencia específica del proveedor y entorno; independiente de local/CI/release |
| Release/recuperación | URL, TLS/orígenes/caché finales y restore sintético autorizados | Sin equivalencia con tests locales | Operación real, solo después de ejecutar y documentar esas verificaciones |

No sustituir PostgreSQL por SQLite ni probar RLS solamente como propietario,
superusuario o BYPASSRLS. La credencial de preparación local se inyectará fuera de
salidas; el ejecutor separará preparación de ejercicio bajo rol runtime. No crear
roles por este documento. La versión local compatible y privilegios efectivos
se registrarán sin cadenas de conexión ni valores secretos.

Los JWT de prueba se firman con material efímero generado en memoria; claves
privadas, tokens y cookies no se guardan en fixtures, snapshots, argumentos,
reportes o logs. La simulación reemplaza transporte, no el verificador de firma.
Fallas HTTP, respuestas parciales y rotación de claves se inyectan por esa frontera.
El mecanismo elegido de comprobación vigente de sesión del proveedor debe tener
casos propios: un mock de `auth.sessions` no demuestra que Free/rol real lo permita.

## Fixtures y oráculo de autorización

Identidades públicas sintéticas A/B/C, prácticas PA/PB y despachos D1/D2. A tiene
PA y membresía profesional D1; B tiene PB y D2; otro integrante D1 carece de
asignación sobre el recurso usado. A también participa **como cliente** en una
relación D1. C participa en otra relación. Nadie tiene dos despachos profesionales
activos. Operador O gestiona miembros sin facultad sobre contenido jurídico.

Preparar estados invitado/activo/suspendido/finalizado, cuenta no confirmada y
restringida, niveles MFA incompleto/completo y sesiones vigentes/caducadas/revocadas.
Los datos del recurso tienen un marcador público específico para detectar lectura
ajena. No crear flujo de solicitudes, consultas, reservas o asuntos productivos para
probar Identity: relaciones futuras pueden ser fixtures mínimas explícitas sobre
el contrato aprobado, sin declarar completadas C04/C05.

El resultado se verifica contra actor/acción/objeto/contexto/estado de la matriz,
no copiando el predicado de implementación al test. Todo negativo incluye un
positivo autorizado equivalente y comprueba estado persistido, filas afectadas y
ausencia de marcador ajeno. Respuesta vacía, API apagada o un 500 no demuestran
autorización. T05 fijará códigos/errores y ocultación consistente de existencia.

## Casos críticos y trazabilidad

Cada fila es una especificación pendiente de implementación. NEG refiere a T02
y DM a T03. Los casos de superficies futuras son puertas de aceptación cuando
se habiliten, no trabajo de producto autorizado por esta estrategia.

| ID | Nivel y escenario | Aserción significativa | Trazabilidad |
|---|---|---|---|
| IA-01 | Integración/E2E: registro, confirmación y recuperación | Cuenta sin confirmación no alcanza datos privados; registro/recuperación no añaden facultad profesional, despacho ni vínculo por correo coincidente | IC-01/02; NEG-04/17 |
| IA-02 | Unit/integración: recuperación presente/ausente, destino alterado, vínculo repetido y fallos Auth | Respuesta conforme al contrato sin enumeración, destino permitido, sin sesión/facultad creada por fallo parcial; límites acordados funcionan | IC-01; NEG-17 |
| IA-03 | Unit/integración: JWT correcto y firma corrupta, algoritmo no permitido, issuer/audience ajenos, exp vencido, sub ausente | Verificación real rechaza entradas inválidas antes de lectura/escritura; JWKS ajeno no se acepta desde cabecera/URL aportada por usuario | IC-05; NEG-08 |
| IA-04 | Integración: session_id ausente/inválido/no vigente, sub/sesión de aplicación no coincidentes y aal incompleto | Sesión opaca queda vinculada a sujeto y sesión verificados; ninguna combinación confusa obtiene acceso; nivel MFA solo no concede permiso | IC-05; NEG-09/21 |
| IA-05 | Integración/E2E: login/logout/cambio sensible y cookie | Cookie opaca Secure/HttpOnly y SameSite del contrato; JS no lee tokens Auth; fijación de sesión no persiste tras autenticar; valores ausentes de cuerpo/respuesta/URL | IC-05; NEG-14/15 |
| IA-06 | Integración/E2E: petición mutante con CSRF omitido/incorrecto, origen ajeno/ausente según política | Mutación denegada antes de efectos; origen válido sin CSRF no basta ni CSRF válido legitima origen ajeno; positivo con ambos válidos funciona | IC-05; NEG-19 |
| IA-07 | Unit/integración: reloj en límites 12h absoluta y 30min inactiva, antes/exactamente/después | Nunca ampliar límite absoluto al renovar; actividad que el contrato considera válida actualiza inactividad; a igualdad del límite sesión ya no accede | IC-05 |
| IA-08 | Integración: access JWT 15min, refresh correcto/fallido, expiración durante operación | JWT vencido no autentica; renovación no prolonga sesión absoluta ni revive revocada; efecto privado requiere vigencia en frontera acordada | IC-05; NEG-08/09 |
| IA-09 | Integración: cierre actual/todas conforme a alcance T05; sesión previa conservada | La siguiente petición privada tras commit de revocación queda denegada en ámbito cerrado sin esperar JWT; sesiones fuera del alcance conservan solo lo permitido | IC-05; NEG-09 |
| IA-10 | Integración: fuente de sesión/membresía inaccesible, timeout/error/respuesta incompleta | Nuevas operaciones privadas fallan cerradas; no fallback a claims antiguos; no efectos, tokens ni datos en respuesta/log de error | IC-04/05; NEG-07/14 |
| IA-11 | Integración SQL/API: sustituir ID propio por ajeno en lectura/escritura y referencias padre/hijo | Rechazo sin marcador ajeno; original y referencia destino intactos; listado/búsqueda/conteo/exportación no filtran existencia privada | IC-03/06; NEG-01/02/05; DM-02/10 |
| IA-12 | Integración: metadata/payload rol, propietario/contexto/verificado/actor manipulados | Ninguna autoelevación; actor proviene de sesión; cambios de ámbito o facultad solo por transición autorizada | IC-02/04; NEG-04/05; DM-06 |
| IA-13 | Integración/E2E: contexto cambiado PA/D1/PB, roles cliente/profesional y operador O | Selector no concede facultades; despacho no ve PA; miembro sin asignación/O gestor no ve relato; cliente no ve notas internas | IC-02/03/04; NEG-03/13; DM-01/03 |
| IA-14 | Integración/E2E: suspensión/salida de A con caché caliente/JWT anterior/asignación subsistente | Siguiente petición profesional D1 denegada; PA aislada y accesible si cuenta vigente; participación cliente D1 se evalúa por separado; no copia ni transferencia | IC-04; NEG-06/20; DM-04/05/14 |
| IA-15 | Integración: invitación ajena/repetida/pendiente, reingreso y último gestor | Invitación pendiente no concede acceso; no aceptación por tercero ni doble activación; reingreso no restaura asignación retirada; salida del último gestor sigue regla aprobada | IC-04; DM-07/14 |
| IA-16 | PostgreSQL real: runtime sin identidad/contexto y después identidad A con objeto B | Grants/RLS niegan lectura/mutación; policies de UPDATE verifican origen y resultado; rol efectivo sin propiedad, superuser o BYPASSRLS | IC-06; NEG-11/12; DM-10/12 |
| IA-17 | PostgreSQL real: vistas/funciones/secuencias/grants/herencia/esquemas | Runtime no ejecuta funciones privilegiadas, altera grants o logra TRUNCATE; revisar REFERENCES aparte de RLS; ninguna vista elude política | IC-06; NEG-12; DM-12 |
| IA-18 | Integración: ruta privada alterna Data API o endpoint de diagnóstico/camino directo | Navegador no tiene vía privada alternativa autorizada; inventario y configuración lo demuestran; si otra vía se propone, requiere contrato/pruebas propios | IC-06; NEG-11 |
| IA-19 | Integración/E2E/artefactos: éxito/error/renovación con marcadores públicos sensibles | Ausencia de marcadores en logs/analytics/respuestas, HTML/JS/sourcemaps; respuesta Auth nunca contiene tokens, cookie ni cuerpo privado del proveedor | C01/IC-05; NEG-14/15 |
| IA-20 | Integración: cuenta/membresía finalizadas 30d y auditoría 90d | Acceso se retira inmediatamente, no tras retención; limpieza idempotente respeta límites acordados y no elimina relaciones de terceros ni restaura facultades | Retención; DM-13 |
| IA-21 | Integración/E2E: aal1/aal2, desinscripción/cambio de factor, recuperación y operador soporte | MFA profesional/admin requerido para acción privada; recuperación no lo evita; MFA completo no supera denegación por objeto o membresía | IC-05; NEG-21 |
| IA-22 | Integración: confirmación/recovery complete con OTP expirado/reutilizado/ajeno; fallo tras cambio de contraseña | Confirmación no crea login; recovery temporal no crea sesión general; OTP consumido no se reutiliza ni se promete rollback de contraseña; cierre incompleto se informa 503 | IC-01/05; T05 |
| IA-23 | Integración: CSRF firmado de otra referencia/preautenticación y antiguo tras login/MFA/logout | Cookie/cabecera iguales no bastan si firma/vínculo inválidos; referencia anterior denegada; POST sin Origin y GET bootstrap sin prueba same-origin siguen reglas distintas T05 | IC-05; NEG-19 |
| IA-24 | Contrato API/web: errores de middleware/validación/proveedor, campos extra/query/bearer y caché | Forma exacta de T05, sin eco de input o error crudo; respuestas Auth no-store/no-referrer; bearer incluso con cookie válida rechazado; JSON y límites comprobados | C01/IC-05/06; T05 |
| IA-25 | E2E: teclado, errores y fallos de red/timeout/logout/MFA | Formularios accesibles T06; sin doble envío/reintento automático incierto; estado ausente se distingue de dependencia caída; limpiar contenido tras revocación y no mostrar éxito no confirmado | T06; NEG-14 |

La aplicación puede emitir `Set-Cookie` para el flujo aprobado; IA-05/19 no prohíben
ese uso protocolario. Prohíben valores de cookie/tokens en cuerpos, logs, herramientas
visibles y artefactos de prueba. E2E deshabilitará HAR, video, traces o dumps de red
que capturen autenticación; capturas de pantallas sensibles tampoco son evidencia
publicable. Solo estado booleano de atributos y resultados sanitizados.

T05 concreta dos excepciones de salida para su finalidad: token CSRF de aplicación
en bootstrap y secreto/URI/QR del propio factor en enrolamiento TOTP privado. El
segundo es material sensible imprescindible al configurar el factor, no permiso
para serializar tokens de sesión o respuestas Auth completas. A0 confirmó que la
excepción del propio enrolamiento pertenece al flujo Auth aprobado; recuperación y
desinscripción siguen cerradas. La regla «sin secretos en respuestas» se aplica a
todos los cuerpos fuera de esa entrega dedicada. Probar que factor ajeno/preautenticación no obtiene esos
campos; ninguna otra ruta los repite; no cache, logs, HTML público o capturas los
conservan. En pruebas, inspección en memoria devuelve solo cumplimiento booleano,
nunca imprime el valor. Si la dependencia de enrolamiento no está configurada,
registrar ese flujo bloqueado, sin simular configuración real del proveedor.

Precisiones de T05 para el oráculo: GET session sin autenticación devuelve 200 con
`authenticated:false`, no 401; una dependencia necesaria caída devuelve 503.
Registro/recover presente/ausente devuelven 202 uniforme, pero infraestructura no
configurada devuelve 503. Login no confirmado y credenciales inválidas comparten
401 INVALID_CREDENTIALS. Logout solo devuelve 204 al completar alcance; fallo
posterior de proveedor devuelve 503 y conserva revocación local/cookies retiradas.
La UI no mantiene identidad privada como si la cookie siguiera válida ante ese
fallo parcial ni anuncia cierre global completo. MFA recover/unenroll devuelven
FEATURE_UNAVAILABLE, sin habilitar un bypass para hacer pasar E2E.

Polling GET session y GET csrf no actualizan inactividad; MFA exitoso no reinicia
12h absolutas. JWT cuya duración exceda 15min genera AUTH_UNAVAILABLE, incluso
si aún no expiró. Comprobar bootstrap local HTTP únicamente loopback/configuración
dev explícita y cookies de producción Secure/__Host-; desplegable con excepción
local activada debe fallar inicio. Versionar OpenAPI y cliente contra unión
SessionView/errores T05, sin snapshot de cookies, códigos o cuerpos sensibles.

## Concurrencia y aislamiento de conexiones

Usar barreras/eventos deterministas, transacciones y dos conexiones/peticiones
reales; no sleeps como demostración ni mock de lock/commit. Observar orden de
commit y estado final desde lectura autorizada separada.

| ID | Carrera | Invariante y comprobación |
|---|---|---|
| ICN-01 | Dos peticiones renuevan la misma sesión | Renovación serializada/idempotente según contrato; no duplicar sesión ni perder rotación; fallo de una respuesta no divulga refresh token; revocación vence renovación tardía |
| ICN-02 | Logout/revocación confirma mientras refresh está bloqueado | Al liberar refresh, no recrea sesión vigente; siguiente petición tras revocación denegada; estado persistido permanece revocado |
| ICN-03 | Salida/suspensión/cambio de facultad frente a escritura privada en curso | Frontera transaccional acordada impide commit posterior con facultad retirada; probar orden inverso autorizado y ausencia de modificación parcial |
| ICN-04 | A y B alternan peticiones en pool de tamaño 1; rollback/error/cancelación intermedios | Identidad/contexto solo transaccionales; B no hereda A tras éxito, fallo o devolución de conexión; petición sin contexto denegada |
| ICN-05 | A acepta invitaciones D1/D2 simultáneamente | Máximo un despacho profesional activo al commit; conflicto definido en contrato, sin unión temporal de datos ni doble evento engañoso |
| ICN-06 | Cambio de contexto y respuesta de lectura tardía/caché caliente | API filtra por actor/contexto; UI no presenta respuesta antigua en nuevo contexto; cache no comparte datos entre sujetos |

ICN-03 exige un contrato de orden observable, no promesa de cancelar todo cálculo ya
iniciado. Ninguna prueba afirma retirar bytes descargados antes de revocación.
Si T05 no fija frontera de efecto para una operación, documentar ese caso como
bloqueado; no convertirlo silenciosamente en eventual consistencia.

## Retención y eliminación

Probar bordes de 30d/90d con reloj controlado y ejecución explícita del proceso de
limpieza, nunca esperar días reales. A0/T03 deben fijar inicio del cómputo, unidades,
campos que se purgan o anonimizan, vínculos mínimos conservados, frecuencia del
proceso y tratamiento de restauración/backups. No asumir eliminación de Auth al
borrar fila local ni borrar relato/relación de terceros en cascada.

Los 30d/90d no aprueban plazos de documentos, perfiles públicos, consentimientos o
datos de atención. La prueba debe mostrar que registros terminados no autorizan
durante retención; limpieza repetida es segura; cuenta cerrada no recupera identidad
por simple coincidencia de correo; restore sintético no revive permisos revocados.
La verificación real de restore tendrá evidencia independiente. Tratamiento y
derechos aplicables: **LEGAL REVIEW REQUIRED**; esta estrategia no certifica cumplimiento.

## Cómo impedir falsos positivos de aceptación

1. Antes del negativo, el positivo autorizado prueba servidor/base/fixture funcional.
2. Observar resultado y persistencia mediante roles adecuados; evidencia solo IDs
   sintéticos, caso, estado esperado/obtenido y conteos permitidos.
3. En entorno aislado, una mutación deliberada de controles críticos (quitar vínculo,
   vigencia, filtro contexto, CSRF, verificación JWT o política de fila) debe hacer
   fallar su negativo. Restaurar esa mutación antes de entregar; sin quitar controles
   en proyecto remoto o rama común. No necesita un framework nuevo por inferencia.
4. La suite RLS tiene ejecución directa como runtime para detectar que un filtro API
   o privilegio administrador ocultó una política inexistente. La suite API también
   prueba sus controles sin confiar únicamente en RLS.
5. Reportar skips/bloqueos de DB/proveedor como pendientes, no pruebas aprobadas.
   No escribir tests que solo comparen constantes de implementación consigo mismas.

## Evidencia proveedor real y puertas de entrega

Antes de afirmar C02/C03 completos, el ejecutor autorizado confirmará destino
Abogalia, alcance y aislamiento sintético y ejecutará: registro/confirmación y
recuperación con correo permitido; verificación JWT/claves; TOTP/MFA; renovación
y rotación concurrentes; cierre actual/global según contrato; comprobación de
vigencia de sesión compatible con privilegios mínimos del proveedor.
No se configura SMTP, se contrata tier ni se otorgan grants administrativos para
lograr un test. Falta de mecanismo viable en Free se reporta como bloqueo concreto.

Registro de evidencia por caso: nivel local/proveedor/CI/release, versión de
contrato/implementación, entorno lógico, fecha, resultado, simulación y limitación.
No valores Auth, relatos, emails reales, requests crudos, trazas privadas o conexión
con contraseña. Unit/integración con Supabase simulado nunca se etiqueta proveedor
real; C03 de confianza requiere su checkpoint posterior de verificación profesional.

Puertas: C01/baseline; contratos T05/T06 conciliados; modelo/estados/retención
precisados; suites locales pertinentes y revisión independiente; evidencia proveedor
real para flujos dependientes; CI remoto solo si ejecutado; release/restore antes de
datos reales. Un mock o pantalla no satisface Definition of Done.

Fuentes oficiales ya consultadas en T02, sin acceso de proyecto:
[Supabase sesiones](https://supabase.com/docs/guides/auth/sessions),
[JWT](https://supabase.com/docs/guides/auth/jwts),
[RLS](https://supabase.com/docs/guides/database/postgres/row-level-security),
[PostgreSQL 17](https://www.postgresql.org/docs/17/ddl-rowsecurity.html).
Revalidar versiones y proveedor antes de implementación; no afirmar que un mock
reproduce toda su semántica.

Verificación actual: revisión documental de IC-01–IC-06, NEG-01–21 y DM pertinentes;
contratos T05/T06 leídos y conciliados; 25 casos y seis carreras especificados.
Sin pruebas ejecutadas, instalación,
Git, SQL, conexiones remotas, scanner, secretos, recursos Kova o nuevos agentes.
