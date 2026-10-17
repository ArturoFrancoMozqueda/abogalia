# C03 — Matriz y frontera de acceso profesional

Fecha: 2026-10-14. PC-01–PC-05 A aprobados por orden A0/D-040.
Base338617; contrato revisable por A1/A0, sin grants o implementación implícitos.
Complementa [modelo C03](../data/professional-context-schema.md). Auth, MFA,
revisión, publicación, membresía y propiedad son hechos diferentes.

## Actores y precondiciones

Principal sale exclusivamente de sesión validada C02; profesional y revisor no
se obtienen de user_metadata ni de rol `authenticated`. Privado exige Auth/MFA
con garantía de sesión activa. La aceptación HTTP real sigue pendiente aunque
su adapter esté implementado localmente; no habilitar C03 real por ese mock.

Primer incremento A0/A1: agregado privado draft + práctica preparing, campos
display_name/declared_area privados, sin cédula/legal_name. Solo lectura, edición y
withdraw propias; versiones CAS de ambos objetos y retiro atómico. Actores/editors
del borrador no son professional_work/manage_context. Dominio puro no demuestra
autenticación/CSRF/RLS real: futuros adaptadores deben exigir esas fronteras.
Actualización D-041: persistencia/API propias privadas en implementación local,
sin publicación/revisión/activación/invitaciones/despachos por este incremento.
Modelo físico y unidad transaccional acordada constan en modelo C03 actualizado.
Runtime exacto existente, FORCE RLS propietario y grants por columnas inmutables;
sin DELETE/TRUNCATE, lectura audit, Data API, rol nuevo o managedmembership.
Savepoint de negocio se mantiene hasta frontera Auth; error/indeterminación revierte
agregado/eventos y conserva renovación consumida fuera del savepoint, sin actividad.

| Actor/acción | Puede, bajo precondiciones | No puede |
|---|---|---|
| Visitante | Leer proyección publicada vigente de display_name/ámbito declarado/etiqueta precisa | Ver cédula completa, nombres declarados privados, decisiones de revisión, miembros o contextos privados |
| Titular | Editar datos propios permitidos, solicitar revisión, retirar perfil/publicación, ver declaración y decisiones propias mínimas | Editar resultado/actor/alcance de revisión, publicar versión no habilitada, autoaprobarse o alterar dueño |
| Revisor del producto | Revisar versión asignada, contraste mínimo y decidir alcance/resultado; Arturo inicial con capacidad explícita | Autoevaluación, consultar jurídicos/clientes, usar credenciales proveedor o nombrarse revisor desde perfil |
| Profesional práctica | Preparar práctica; activarla tras revisión; acciones privadas de su ámbito con habilitación vigente | Administrar prácticas de miembros por ser gestor de despacho |
| Miembro active professional_work | Acciones profesionales aprobadas del contexto vigente; futura asignación por objeto necesaria | Leer todo despacho, declarar permisos globales o actuar sobre otro contexto |
| Miembro active manage_context | Gestión mínima contexto/miembros, invitar/proponer capacidades, suspender/finalizar otros según transición | Leer evidencia profesional privada de colegas o futuros contenidos jurídicos por jerarquía |
| Destinatario invitación | Aceptar únicamente invitación propia válida, con MFA y condiciones/cardinalidad satisfechas | Acceso mientras pending, aceptar por otro, editar capacidades, usar token revocado/reutilizado |
| Miembro suspended/ended | Consultar lo propio permitido y tramitar retirada, según contrato mínimo | Profesional/administración derivada del vínculo, restaurar permisos/asignaciones de historia |
| Exmiembro como cliente | Ninguna facultad C03 añadida; futura participación cliente se evalúa aparte | Recuperar profesional_work por ser cliente, o perder automáticamente toda participación cliente al salir |

Capacidades manage_context/professional_work no son jerarquía ni roles proveedores.
El gestor solo ve datos mínimos de vínculo (UUID sujeto, estado, capacidades y
fechas); no email/contacto/cédula por inferencia. Perfil publicado se obtiene de la
misma proyección pública que cualquier visitante. Leer lista de miembros completa
por ser simple miembro no está concedido; errores/conteos/paginación no revelan
vínculos ajenos. No RPC/SQL público ni unión por correo con fuentes privadas.

## Revocación, revisión y propiedad

Retirar/suspender vínculo elimina facultades derivadas en la siguiente petición y
frontera de operación concurrente; no esperar JWTrefresh. Perfil no habilitado
deniega professional_work, incluso con membresía active. La regla de administración
cuando cambia habilitación necesita la precisión pendiente del modelo, no una
elección silenciosa. Operaciones de retirada propias/cierre de cuenta conservan
su garantía: nunca exigir conservar acceso por un relevo pendiente.

Cambio de nombre/cédula invalida revisión de esa versión y quita publicación no
vigente. Bajo estado solicitado/en revisión no etiquetar identidad como verificada.
Resultado `registry_record_checked` acota lo contrastado; no acredita titularidad,
experiencia, ausencia de conflictos o representación del despacho. Fuentes/datos
restringidos a titular/revisor explícito, sin scraping ni nuevos proveedores.

Creación de despacho no autoriza a cambiar práctica a firm, reasignar propietarios,
exportar datos de contexto o establecer permisos profesionales en objetos futuros.
Último administrador debe tener relevo aceptado o cierre controlado con responsable;
una obligación administrativa no crea facultades del producto. No apoyo con acceso
universal. Suspensión mantiene slot; finalización libera slot pero no transfiere
propiedad ni restaura asignaciones al reingresar.

## Matriz de negativos meaningful

Cada negativo incluye un control positivo con mismo servidor y rol real, observa
estado persistido y ausencia de datos ajenos; datos sintéticos, PostgreSQL/RLS reales
para aislamiento. No basta ocultar botón o responder403 con infraestructura apagada.

| ID | Intento | Evidencia necesaria |
|---|---|---|
| C03-01 | Cambiar profile_id/user_id/context_id de práctica propia a otro | Lectura/mutación privada denegadas; propietario intacto |
| C03-02 | Miembro/gestor de D1 solicita práctica propia de otro miembro | Sin campos, conteos o efectos sobre la práctica |
| C03-03 | manage_context pide cédula/evidencia privada o futuro contenido jurídico | Denegado pese a gestión vigente; no grants universales |
| C03-04 | Solicitante se cambia state/reviewer/capabilities o metadata Auth | Ninguna decisión/capacidad nueva; allowlist por campo |
| C03-05 | Revisor intenta aprobar propio perfil o versión anterior a nueva cédula | Denegado; revisión vigente liga actor distinto y versión exacta |
| C03-06 | Publicación de perfil pending/suspended/rejected o versión invalidada | Proyección ausente, sin PII en caché/prerender/bundle |
| C03-07 | Invitación pending/ajena/revoked/expired/repetida acepta membresía | Sin acceso/efecto duplicado, prueba destinatario y transacción |
| C03-08 | Aceptaciones simultáneas en D1/D2, incluyendo vínculo suspended | Como máximo un active/suspended persistido por User |
| C03-09 | Suspender/finalizar mientras petición profesional está en vuelo | Revalidación de frontera impide commit/resultado; no restauración por refresh |
| C03-10 | Exmiembro usa IDs, contexto elegido, claims o asignación viejos | Facultades profesionales denegadas; cliente se evalúa aparte |
| C03-11 | Último administrador sale/cierra cuenta sin relevo | Retirada de acceso efectiva; sin custodio implícito ni bloqueo de cierre de cuenta |
| C03-12 | Gestor se otorga capacidades o confirma unilateralmente relevo | No autoescalamiento; aceptación independiente explícita |
| C03-13 | Dos peticiones alternan subject/contexto en conexión reutilizada | Ninguna identidad/estado/capacidad se hereda; GUC local por transacción |
| C03-14 | Runtime cambia owner, TRUNCATE, grants, credencial ajena o audit histórico | Denegado por grants/RLS/columnas; controles mínimos no se elevan |
| C03-15 | Corte30d perfil/membresía; historia90d y suspensión nofinalizada | Datos retirados se eliminan sin borrar historia90d; lectura no reinicia draftTTL; suspended no ocupa fin ficticio |
| C03-16 | Purga/restore/caché vuelve a publicar perfil retirado | Ausencia de proyección; sin resurrección de revisión o permisos |
| C03-17 | Firma/iss/aud/sid/aal/cookie/CSRF inválidos o Auth indeterminado | No dato privado/commit; ningún fallback por ver perfil habilitado |
| C03-18 | Marcadores sintéticos de cédula/evidencia/contacto en errors/logs/build | Ausentes de outputs, telemetría, bundles y artefactos publicables |

## Datos y operación pendientes

PC-05: perfil/credencial/contexto retirados30d, rechazo/borrador abandonado30d;
membresía finalizada30d e historia mínima90d. No auditoría con perfil/cédula completa
ni cascada30d→90d. Consentimiento/publicación no autoriza todos los datos ni retención
indefinida. UUID lógico90d sigue clasificado privado, no anonimización asegurada.

Q-C03-01..03 A aprobadas (D-041): TTL invitación24h, recibos terminales30d/events90d;
revisor manual inicial Arturo con correo confirmado/MFA y capacidad review_professionals,
sin autoevaluación/administración proveedor; cierre excepcional Arturo con capacidad
separada y sin lectura jurídica. No se incorporan esas tablas/capacidades en este
incremento ni se entrega invitación externa. Contratos posteriores de transición
deben materializar aceptación/relevo/cierre, sin facultades implícitas.
No hay endpoint de reviewer universal, credencial administrativa ni prueba inventada
de retirada Auth. El gate C02 real se mantiene; scheduler/restore/credenciales
permanecen pendientes aunque exista modelo aprobado. LEGAL REVIEW REQUIRED.

Verificación local actual: store privado y19 negativos/positivos SQLruntime reales,
32 pruebas API Auth simulado/SQL real de A4 dentro fresh467 pasada por A4, sin CI
remoto/proveedor. Primer snapshot propio fresh432 pasó con16 de storage.
A4 revisión independiente store/migración sin bloqueantes; A2 revisión API/frontera
business sin bloqueantes. FK users RESTRICT
falla cerrado ante purga cuenta antes agregado30d; eventoslógicos90d no cascada.
Worker/job C03 aún no implementado: responsable Arturo, cumplimiento operacional
pendiente. Authclosed deniega acceso, no resucita perfil. Revisión independiente
A1/A4 requerida antes integrar/aplicar; no dato real, secreto o recurso Kova.
