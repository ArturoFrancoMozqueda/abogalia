# Identity y contextos — Modelo de amenazas propuesto

Fecha: 2026-10-12. Estado: **Proposed; no aprobado ni implementado**.
Orden T02, A2; capacidades C01/C02/C03. Revisor asignado: A0, distinto del autor.
Base recibida: `codex/identity-design`, HEAD
`c71fea298742a43994cf6026494ded080b3ef50d`, más cambios locales preservados.
Este documento no autoriza código, SQL, configuración de proveedores ni gasto.

## Actualización de aprobación

D-031 registra la aprobación de Arturo de las recomendaciones A de T01 y del
modelo/matriz recomendados para Identity. D-032 fija 30 días para cuenta cerrada
/evidencia mínima de membresía terminada y 90 días para auditoría, con eliminación
/anonimización posterior. Esta actualización supera el estado pendiente de esas
partes en el borrador; no aprueba superficies F/C03–C19 ni plazos ausentes para
datos jurídicos o evidencia profesional. Implementación y pruebas reales pendientes.

## Contrato y hechos conservados

Se leyó AGENTS.md, README.md, el plan completo, el registro de decisiones y el
[checkpoint de base](../checkpoints/repository-and-empty-database.md).
D-003 permite práctica independiente y pertenencia a **un despacho** por abogado;
no concede acceso entre contextos. D-028 aprueba Supabase Auth como proveedor;
login, roles, sesiones y permisos siguen pendientes. D-029 y D-030 aportan proyecto
vacío y base local, sin integración de Identity. Las propuestas antiguas no autorizan
permisos ni tratamiento de datos.

Dependencia: [checkpoint T01](../checkpoints/identity-and-contexts.md), borrador leído.
Contrato de coordinación: IC-01 registro; IC-02 persona con varias funciones;
IC-03 propiedad de relaciones; IC-04 membresía/salida; IC-05 sesión/MFA/revocación;
IC-06 camino de datos. Estos IDs organizan pendientes, no son decisiones aprobadas.
La [matriz propuesta](access-matrix-proposed.md) precisa sujetos, objetos y negativos.
T03 definirá el modelo conceptual; este documento no crea tablas o roles técnicos.

## Activos y fronteras

Activos conceptuales: identidad y sesión; membresías y permisos; perfil público y
credenciales profesionales privadas; relaciones de cliente y su contexto; evidencia
de consentimiento; datos jurídicos futuros; eventos mínimos de seguridad.
Credenciales de runtime, migración y administración se protegen por separado.
No se consultaron datos de clientes ni valores secretos para preparar este diseño.

Fronteras que debe definir IC-06:

| Frontera | Riesgo a resolver antes de implementar |
|---|---|
| Navegador → proveedor Auth | Almacenamiento de sesión, recuperación, redirecciones y renovación; no introducir tokens en URLs ajenas al flujo aprobado |
| Navegador → FastAPI | Identidad verificada, autorización por acción/objeto, origen y protección CSRF si se eligen cookies |
| FastAPI → PostgreSQL | Rol mínimo y contexto verificado; no inferir que usar Auth aplica RLS a una conexión SQL propia |
| Navegador → Data API, si se aprobara | Camino alterno que debe aplicar la misma política; no abrirlo por comodidad |
| Persona → práctica/despacho/relación | Una selección de contexto del navegador no demuestra membresía ni propiedad |
| Operación humana → proveedor/aplicación | Administración de infraestructura no implica acceso funcional al contenido jurídico |
| Código → Git/CI/bundle/logs | Copias involuntarias de secretos o datos; todas las salidas requieren control |

Atacantes considerados: visitante externo; usuario autenticado que manipula IDs;
miembro o exmiembro de despacho; cuenta comprometida; operador con privilegios
excesivos; PR/dependencia no confiable. Disponibilidad y errores accidentales también
pueden degradar controles. Un checkout o un conector autenticado no acota permisos.

## Amenazas, controles y evidencia exigida

Los controles son recomendaciones para el checkpoint. Las reglas de secretos de
AGENTS.md ya son obligatorias. Prioridad alta indica bloqueo de aceptación cuando
la superficie exista; no expresa una evaluación cuantitativa de probabilidad.

| ID | Amenaza y consecuencia | Control propuesto | Negativo verificable | Pendiente |
|---|---|---|---|---|
| TM-01 | IDOR: cambiar identidad, contexto, cliente u objeto para leer/escribir datos ajenos | Autorizar cada acción, objeto y relación contra fuente vigente; filtrar listados, búsquedas, conteos y exportaciones | NEG-01/02/03: IDs ajenos no devuelven datos ni generan efectos | IC-02/03/06 |
| TM-02 | Escalamiento: metadata, formulario o JWT se usan para obtener facultades | Separar campos editables de atributos de autorización; servidor valida transiciones y facultad del actor | NEG-04/05: modificar metadata/propietario no amplía acceso | IC-01/04 |
| TM-03 | Confusión entre cliente, abogado y despacho de la misma persona | Evaluar función en relación concreta; no unir permisos por email, identidad o selector UI | NEG-03: misma persona en dos funciones no ve notas internas como cliente | IC-02/03 |
| TM-04 | JWT válido con claims antiguos tras baja, suspensión o salida | Fuente vigente para membresía; definir objetivo medible de revocación, caché e invalidación | NEG-06/07: JWT previo no mantiene facultades tras el límite aprobado | IC-04/05 |
| TM-05 | Robo, repetición o aceptación incorrecta de sesión/JWT | Verificación criptográfica y claims esperados, recuperación segura, TLS, política de sesión/MFA | NEG-08/09: firma/issuer/audience/exp incorrectos y sesión inválida rechazados | IC-01/05 |
| TM-06 | Salida del despacho mueve o expone práctica propia, relaciones y documentos | Cambio de membresía separado de propiedad; retirar facultades profesionales derivadas sin cancelar silenciosamente otra participación independiente; transferencia explícita | NEG-06/10/20: salida bloquea nuevo acceso profesional derivado, conserva práctica según decisión, no copia datos; reevaluar función cliente por separado | IC-02/03/04 |
| TM-07 | Acceso alternativo evade FastAPI o RLS; vistas/funciones amplían privilegios | Inventario por superficie; grants mínimos y políticas explícitas; pruebas con rol runtime real | NEG-11/12: ninguna vía alterna lee/modifica objetos ajenos ni ejecuta privilegios excluidos | IC-06 |
| TM-08 | Soporte o administrador obtiene lectura jurídica universal | Facultades separadas; intervención acotada con motivo y auditoría según checkpoint operativo | NEG-13: cuenta ordinaria/operador sin facultad no administra ni lee contenido | IC-04; C17 |
| TM-09 | Tokens, contraseñas o textos privados salen en logs, errores, HTML o sourcemaps | No capturar valores; allowlist de campos operativos, exclusión de cuerpos/headers/cookies y revisión de artefactos | NEG-14/15: marcadores sintéticos no aparecen en ninguna salida pública | C01; IC-06 |
| TM-10 | PR, workflow, scanner o dependencia filtra credenciales administrativas | Jobs de validación sin secretos; permisos mínimos, acciones fijadas por SHA y revisión de supply chain | NEG-16: PR no confiable no recibe secretos ni facultades de release | C01; A6/A0 |
| TM-11 | Enumeración, abuso de recuperación o redirección a destino ajeno | Respuestas sin confirmar identidad, límites por finalidad, destinos permitidos y validación de flujo | NEG-17: recuperación no revela cuenta ni acepta destino arbitrario | IC-01/05 |
| TM-12 | Caché o carrera entrega datos de otro contexto o tras revocación | Claves de caché con actor/contexto/política; revalidar antes de efectos; semántica de operaciones en curso acordada | NEG-07/18: cambio concurrente de contexto/membresía no provoca fuga ni escritura tardía | IC-04/05/06 |

## Particularidades de Supabase y PostgreSQL

La firma del JWT acredita origen, no vigencia de cada membresía. `user_metadata`
es editable y no sirve para autorizar; tampoco los claims de `app_metadata`
garantizan actualización inmediata. Comprobar privilegios contra la fuente aprobada.
Revisar vistas, funciones privilegiadas y permisos de creación/ejecución, además de
filas. [Supabase RLS](https://supabase.com/docs/guides/database/postgres/row-level-security).

FastAPI deberá verificar firma, algoritmo permitido, issuer, audience, expiración y
sujeto con una biblioteca revisada y versionada; nunca confiar en mera decodificación.
El contrato deberá manejar rotación y fallo de claves sin aceptar identidades no
verificadas. No se selecciona algoritmo ni se presupone configuración del proyecto.
[Supabase JWT](https://supabase.com/docs/guides/auth/jwts).

Cerrar sesión y revocar renovación no garantiza rechazo inmediato del access token
ya emitido. Supabase documenta comprobación de `session_id` contra sesión vigente
para ese requisito. Límites gestionados de duración, inactividad y sesión única
requieren Pro o superior. Para el proyecto Free, IC-05 debe elegir una garantía
realizable sin gasto implícito, incluyendo tratamiento de operaciones en curso y
fallo de la fuente de vigencia. No se concede acceso administrativo a `auth.sessions`
por esta propuesta. [Sesiones](https://supabase.com/docs/guides/auth/sessions).

Los grants determinan acceso al objeto; RLS limita filas. Exposición desactivada y
trigger automático no reemplazan revisión de privilegios residuales por propietario.
[Seguridad Data API](https://supabase.com/docs/guides/api/securing-your-api).
PostgreSQL excluye TRUNCATE/REFERENCES de RLS; superusuarios y BYPASSRLS la evaden,
y propietarios normalmente también. El rol runtime y las pruebas no deberán depender
de esos privilegios. [PostgreSQL 17](https://www.postgresql.org/docs/17/ddl-rowsecurity.html).

## Revisión de las opciones recomendadas de T01

IC-05 A propone cookie opaca HttpOnly y custodia/renovación de tokens en API,
MFA profesional/administrativo y objetivos numéricos de sesión. Es una recomendación,
no un contrato aprobado ni capacidad demostrada del SDK. Requiere persistencia
sensible de servidor, vinculación inequívoca cookie/sujeto/sesión, renovación
concurrente, caducidad, rotación, protección CSRF y recuperación de MFA sin bypass.
El acceso profesional debe comprobar nivel MFA vigente para la acción, además de
permisos; MFA no sustituye autorización. NEG-09/19/21 cubren esas obligaciones.
La siguiente petición privada puede denegarse tras revocación, pero no retirar
contenido ya descargado. Fallos de fuente vigente y efectos en curso necesitan
semántica aprobada; no asumir que un timeout de aplicación revoca toda sesión Auth.

IC-06 A propone API con SQL runtime mínimo y RLS adicional. Debe concretar cómo
identidad y contexto verificados llegan a cada transacción, con aislamiento del pool
y privilegios suficientes para que el cliente no falsifique el contexto. NEG-11/12/18
deben probar controles en API y rol runtime real. No aceptar una conexión propietaria
como prueba de políticas. No se ratifican estas opciones ni los números de IC-05.

## Propuesta local y CI para C01

Diseño para A6/A0; **ningún scanner instalado, ejecutado o workflow modificado**:

1. A0 selecciona versión y checksum del scanner desde su release oficial y revisa
   contrato de CLI antes de integrarlo. Gitleaks es candidato, no herramienta elegida.
   Su documentación distingue `git`/`dir`/`stdin` y ofrece `--redact=100`. No usar
   redacción parcial, modo verbose, trace/debug ni reportes crudos.
   [Gitleaks oficial](https://github.com/gitleaks/gitleaks).
2. Probar primero redacción con marcadores públicos sintéticos, nunca secretos reales.
   Validar stdout, stderr, reporte y errores del wrapper. Exponer solo ruta lógica,
   regla y estado; suprimir líneas coincidentes, fragmentos, valores y contexto crudo.
   Un fallo de scanner/redacción bloquea publicación, no cuenta como scan limpio.
3. Revisar cambios explícitos, archivos nuevos aprobados y baseline de historial.
   Excluir `.env`, gestores de credenciales y datos privados de lecturas ordinarias.
   El examen del historial requiere proceso que mantenga valores fuera de cualquier
   salida visible; no volcar diffs históricos sin revisión previa. No usar un baseline
   de hallazgos para ignorar exposiciones conocidas.
4. Revisar bundle, HTML prerenderizado, sourcemaps, imágenes de contenedor y reportes
   si se generan. Evitar introducir secretos en `VITE_*`; una clave publishable
   pública necesita IC-06 aprobado y no habilita lectura jurídica por sí misma.
5. En CI, validación sin credenciales de runtime o despliegue; permisos mínimos por
   job y acciones por SHA. No combinar ejecución de código no confiable con secretos
   mediante `pull_request_target` o equivalente. Separar release autorizado de PR.
   [GitHub secure use](https://docs.github.com/en/actions/reference/security/secure-use).
6. A0 verifica disponibilidad/configuración real de secret scanning y push protection
   antes de atribuirles cobertura; ninguna garantiza detectar todos los formatos.
   Falsos positivos requieren evidencia segura y revisión; no saltarse bloqueos.
   [Secret scanning](https://docs.github.com/en/code-security/concepts/secret-security/secret-scanning),
   [push protection](https://docs.github.com/en/code-security/concepts/secret-security/push-protection).

Ante sospecha de exposición: detener operación afectada y publicación; reportar solo
proveedor/variable/ubicación; coordinar rotación/revocación con responsable autorizado.
No repetir valores, borrar evidencia ni reescribir historia. Borrar un archivo no
revoca una credencial. Esta entrega no demuestra ausencia absoluta de filtraciones.

## Decisiones, límites y próximos criterios

Las preguntas se agrupan exclusivamente en IC-01–IC-06 de T01, sin ampliar la sesión:
registro/recuperación; varias funciones; propiedad; membresía/salida; sesión/MFA y
tiempo máximo de revocación; camino de datos/rol runtime. Administración sustantiva
y retención de eventos requieren checkpoints posteriores. No fijar duraciones por
inferencia. Privacidad, región, transferencia y tratamiento: **LEGAL REVIEW REQUIRED**.

Para implementar: aprobación de T01, modelo conceptual aprobado, matriz acordada,
contratos API y errores definidos, responsables de migraciones y revisión asignados.
Para aceptar C02/C03: negativos de la matriz con datos sintéticos y controles reales;
la prueba debe fallar al retirar la autorización, no solo comprobar un mock.

Fuentes públicas consultadas el 2026-10-12. Se revisó el
[changelog Supabase](https://supabase.com/changelog.md): deprecación de
[cifrados TLS](https://supabase.com/changelog/cbc-tls-ciphers-deprecated) y cambios de
[PostgreSQL 15.19/17.11](https://supabase.com/changelog/postgres-15-19-17-11-breaking-changes)
deben reconfirmarse al implementar. No se inspeccionó versión remota ni se actualizaron
clientes o extensiones. Los
[tokens administrativos acotados](https://supabase.com/changelog/scoped-personal-access-tokens-ga)
son una opción futura para operación autorizada, sin crearlos ni asumir que el MCP
actual tenga esos límites. Principio de autorización por objeto y mínimo privilegio:
[OWASP](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html).

Verificación de esta entrega: revisión documental y enlaces internos al integrar T01;
sin pruebas de runtime, scanner, CI remoto, restauración o despliegue. Las pruebas
descritas son especificaciones pendientes, no evidencia de capacidad implementada.
