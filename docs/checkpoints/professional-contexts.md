# Checkpoint — Profesionales y contextos de Legalia (C03)

Actualización2026-10-14: Q-C03-01..03 A aprobadas expresamente por Arturo (D-041).
Las preguntas/opciones históricas no requieren nueva aprobación; implementación,
procedimiento de revisión e identificación de su actor real siguen pendientes.

Fecha: 2026-10-13. Estado: **Proposed / Awaiting decision** para C03.

Actualización 2026-10-14: **Approved, PC-01..PC-05 A (D-040)** por Arturo.
Avanzar modelo/contratos/matriz y su implementación revisada con las dependencias
vigentes. No reabrir las cinco opciones aprobadas. Sedes, entrega de invitaciones,
procedimiento antisuplantación y revisión jurídica conservan límites explícitos.
Estado Approved no significa operación profesional real verificada o C03 Done.
Orden A1 producto/datos; base `eba6cbedb631`, checkout del coordinador.
Revisor A0. Único entregable propio: este checkpoint; no tablas, migraciones,
backend, pantallas, permisos nuevos, datos reales o cambios remotos.

## Lo que entiendo

Legalia necesita distinguir quién inicia sesión, quién declara una actividad
profesional, qué información ha comprobado la plataforma y en qué práctica o
despacho opera. C03 prepara perfiles, credenciales, contextos, despacho, sedes y
membresías; no crea aún solicitudes, clientes, reservas, consultas o asuntos.
El segmento aprobado son independientes y despachos pequeños; no fija cobertura,
especialidades, número de integrantes, precios o promesas de captación.

Una persona puede ser cliente y profesional, tener práctica propia y pertenecer
a un despacho. Correo confirmado, MFA, perfil revisado, perfil publicado y
membresía activa son hechos diferentes. Ninguno concede acceso general a
relaciones jurídicas. Cambiar de contexto ayuda a trabajar; el servidor sigue
autorizando cada objeto y acción con estado vigente.

C02 tiene implementación y pruebas locales de Auth/sesiones; su operación real
mantiene gates y pendientes documentados. No se debe presentar C03 como utilizable
por dibujar un selector de contexto o por tener un proyecto Supabase creado.
La denominación vigente es Legalia; se conservan nombres técnicos del repositorio.

Fuentes locales: [README](../../README.md), [plan](../27_development_plan_agents.md),
[decisiones](../decisions/decision-log.md),
[Identity y contextos](identity-and-contexts.md),
[modelo conceptual anterior](../data/identity-model-proposed.md),
[personas](../03_users_and_personas.md), [alcance](../05_product_scope.md),
[producto refinado](../23_refined_product.md) y
[definición de solución](../19_solution_definition.md).
Las propuestas históricas no autorizan implementación; prevalecen sus
actualizaciones de aprobación y las decisiones expresas de Arturo.

## Decisiones tomadas

| Referencia | Se conserva sin pedir otra aprobación | Qué falta concretar en C03 |
|---|---|---|
| D-003 | Práctica independiente más un despacho por abogado | Creación/control de contexto, tratamiento del vínculo suspendido y transiciones concurrentes |
| D-031 / IC-02 A | Una identidad; funciones cliente/profesional separadas; contexto explícito | Alta profesional, perfil y capacidades concretas de administración |
| D-031 / IC-03 A | Relación futura pertenece operativamente a su contexto; responsable separado; sin cliente global ni transferencia automática | Integridad de referencias, reasignación, custodia y transferencias de C04/C05; no decidir titularidad jurídica aquí |
| D-031 / IC-04 A | Invitación aceptada; miembro no ve toda relación; administración no equivale a lectura jurídica; salida retira facultades profesionales derivadas y preserva práctica propia | Quién invita/cambia capacidades/suspende/finaliza, último administrador y resolución de pendientes |
| D-031 / IC-05–06 A | MFA para operaciones profesionales privadas/administración; revocación en siguiente petición privada; FastAPI media datos privados | Matriz C03 por acción/objeto, frontera transaccional, roles y RLS de nuevas entidades |
| D-032 | Evidencia mínima de membresía terminada 30 días y auditoría de acceso 90 días, con borrado/anonimización | Perfil, credencial, contexto y otras historias no tienen plazo aprobado por analogía |
| D-025/D-030/D-028 | React Router/Vite, FastAPI, Supabase Auth y monorepo | La arquitectura no elige tenencia física o grants de C03 |
| D-038 y README | Legalia y proyecto propio vigente; nombres técnicos conservados | No autoriza C03, hosting nuevo o uso del destino anterior |

La propiedad operativa y aislamiento generales ya están acordados; **tenencia
concreta, actores/roles, verificación/publicación, transferencia/salida operativa,
clasificación e historial nuevos permanecen Proposed**. No se reabren los plazos
30/90 ni los límites de Identity. El rol PostgreSQL `authenticated` no es un rol
profesional; la administración del proveedor tampoco es un permiso del producto.

## Decisiones pendientes

A0 presenta **cinco decisiones** a Arturo. Todas las opciones siguientes son
Proposed; aprobar un paquete no aprueba lo pendiente de otro ni C04–C19.

| ID | Pregunta concreta | A recomendada | B alternativa y coste funcional |
|---|---|---|---|
| PC-01 | ¿Cómo nacen y se controlan los contextos profesionales? | Un perfil por User, una práctica propia personal y un contexto por despacho. Con Auth/MFA, el profesional puede preparar su práctica; solo tras revisión puede activarla y crear un despacho, quedando administrador inicial por transición explícita. La creación acredita control operativo, no personalidad o representación jurídica. Office pertenece a un despacho y no crea otro tenant; sedes/publicación de dirección se aplazan | Alta de contexto/despacho solo por operador autorizado del producto; reduce altas disputadas, añade revisión manual a cada creación |
| PC-02 | ¿Qué comprueba y publica Legalia antes de habilitar actividad profesional? | Revisión manual mínima a cargo de Arturo como responsable inicial, con capacidad del producto expresamente concedida y sin autoaprobación. Contrastar nombre y cédula declarados con fuente oficial pertinente tras revisión jurídica; guardar resultado/alcance/fecha, sin copias de identificación. Publicación separada y voluntaria: nombre de presentación, ámbito declarado y etiqueta precisa de lo comprobado. No publicar el número completo de cédula en este primer bloque. Cambios de identidad/cédula reabren revisión; especialidad/experiencia declaradas no reciben sello de verificación | Perfil privado declarado, sin publicación ni habilitación profesional hasta resolver el proceso de confianza; permite preparar contexto pero no activar operación |
| PC-03 | ¿Qué capacidades y ciclo de membresía se habilitan primero? | Dos conjuntos explícitos: administración de miembros/contexto y actividad profesional. Pueden coincidir en una persona, sin lectura jurídica universal. Administrador invita y propone capacidades; destinatario autenticado/MFA acepta; no autoescalamiento. Un vínculo activo o suspendido ocupa el único despacho permitido hasta finalizarlo; dos aceptaciones concurrentes no pueden activar dos despachos. Asistentes/recepción se aplazan hasta matriz específica | Administración central de membresías por operador del producto, manteniendo aceptación y aislamiento; menos delegación, mayor operación manual |
| PC-04 | ¿Cómo se resuelven suspensión, salida y último administrador? | Persona puede finalizar su vínculo profesional; administrador autorizado puede suspender/finalizar otro, sin acceder por ello a contenido jurídico. Retirar acceso de inmediato según IC-05, invalidar asignaciones profesionales dependientes y conservar contexto propietario. Último administrador debe nombrar/obtener aceptación de relevo o pasar despacho a cierre controlado con responsable explícito. No bloquear revocación de acceso por pendientes ni impedir cierre de cuenta por falta de relevo. Sin transferencia/exportación automática y sin custodio de soporte por defecto | Aplazar altas de despacho y delegación mientras no exista operación de relevo/cierre; continuar solo diseño de práctica propia, sin sustituir la salida por acceso residual |
| PC-05 | ¿Aprobamos los datos mínimos, historia y eliminación de C03 antes de tablas? | Metadatos mínimos, sin archivos de identidad/credenciales en C03 inicial. Perfil/credencial/contexto retirados: borrado o anonimización a 30 días de retiro/cierre; alta rechazada o borrador abandonado: 30 días de rechazo o última edición. Historial operativo mínimo nuevo: 90 días desde evento; nunca contenido profesional completo como auditoría. Son plazos nuevos propuestos, sujetos a LEGAL REVIEW REQUIRED, que no amplían D-032. Evidencia mínima de membresía 30 días tras fin y audit de acceso 90 días se conservan ya aprobadas. No borrar referencias de negocio aún sin contrato | Mantener campos/estados como diseño y aplazar su persistencia/publicación hasta definir estos plazos y revisión jurídica; no elegir retención indefinida |

La opción PC-02 A no verifica que quien declara una cédula sea su titular por
coincidir nombre/número. El procedimiento debe resolver suplantación/disputa con
actor y comprobación proporcionados; hasta entonces no permite afirmar «identidad
profesional verificada» ni concluir habilitación jurídica. Para el propio perfil
del revisor se necesita otro revisor autorizado o permanece pendiente, sin
autoaprobación. No se aprueba consulta masiva, scraping, proveedor de verificación
o envío de PII por esta recomendación.

PC-05 exige decidir fecha de corte, minimización de referencias y tratamiento de
restauraciones/cachés antes de escribir tablas. La propuesta de 30 días de un
borrador necesita mostrar su consecuencia al usuario y permitir que siga editando
sin simular revisión. Si la revisión legal exige otro tratamiento, A0 vuelve con
el ajuste concreto; esta recomendación no afirma cumplimiento mexicano.

## Diseño propuesto

Modelo conceptual, no nombres de tablas ni SQL aprobados:

| Entidad | Relación/cardinalidad inicial propuesta | Propiedad operativa y límites |
|---|---|---|
| LawyerProfile | User → 0..1 perfil | Datos de su titular; revisión/publicación independientes; no permisos por tener perfil |
| CredentialDeclaration | Perfil → 0..N declaraciones | Declaración, fuente y resultado restringidos; C03 inicial sin adjuntos/ID/biometría |
| ProfessionalReview | Declaración/perfil → 0..N decisiones mínimas | Revisor autorizado, alcance, resultado, fecha y versión; solicitante no modifica decisión |
| ProfessionalContext | Práctica → un profesional responsable; despacho → una LawFirm | Ámbito privado de autorización, distinto de identidad, facturación o propiedad jurídica |
| LawFirm | Despacho → un contexto; contexto → 0..N membresías históricas | Administración operativa explícita; no dueño de prácticas de sus miembros |
| Office | Despacho → 0..N sedes | Sin acceso transitivo ni nuevo ámbito propietario; direcciones y publicación pendientes |
| Membership | User → 0..N históricas; abogado → como máximo un despacho según PC-03 | Vínculo y capacidades con vigencia/versiones; invitación no concede acceso |
| Invitation | Despacho/actor/destinatario → una invitación con estado | Destinatario probado y aceptación propia; evidencia/credencial de aceptación privada, sin tokens en URL/logs |
| ContextChangeEvent | Perfil/contexto/membresía → eventos mínimos | Historial restringido; no copia de documentos ni permanencia de acceso |

Las identidades de cliente, solicitud, consulta, reserva, asunto y relación de
servicio son dominios separados. C03 no crea ClientInContext o ServiceRelationship;
solo declara su futura referencia a un contexto propietario. No entidad `case`,
cliente global, unión automática por email ni movimientos automáticos de práctica
al ingresar/salir de un despacho. Tenencia lógica propuesta no decide bases por
tenant, suscripción o roles SQL genéricos; A3 diseñará almacenamiento tras aprobación.

Estados y transiciones propuestas:

- Perfil: borrador → solicitado → en revisión → corrección requerida / rechazado
  / habilitado; habilitado → suspendido / retirado. Publicación es una decisión
  separada de habilitación; perfil privado habilitado puede seguir sin publicarse.
- Credencial: declarada → revisada con alcance / rechazada; cambio relevante o
  reporte fundamentado → revisión pendiente. No inventar vencimiento de cédula
  ni afirmar validación de especialidad por validar otro registro.
- Contexto: preparación → activo → suspendido / cierre solicitado → cerrado.
  Cierre requiere responsable/pendientes resueltos conforme al contrato de sus
  datos; retirar acceso no espera a que se complete la eliminación.
- Invitación: pendiente → aceptada / rechazada / revocada / vencida. Vigencia y
  mecanismo de entrega deben definirse en contrato específico; no activar SMTP
  ni elegir números por este documento.
- Membresía: pendiente de aceptación → activa → suspendida / finalizada. Retorno
  exige transición autorizada y nueva evaluación; no restaura asignaciones o
  facultades retiradas por recordar una membresía histórica.

Cada transición debe fijar actor, precondición, estado final, efectos de permisos,
evento mínimo y tratamiento concurrente. La sesión Auth no almacena contexto como
autorización: el contexto elegido puede recordarse como preferencia, pero cada
petición verifica existencia, pertenencia, capacidad y estado actuales.

Una revisión de datos de cédula no garantiza resultado jurídico, ausencia de
conflicto, experiencia declarada, vínculo con despacho ni representación legal.
La [SEP presenta su consulta de cédulas](https://www.gob.mx/cedulaprofesional/es)
como referencia oficial; se consultó su resultado público indexado, pero la página
devolvió 403 al abrirse en esta revisión. No se consultó ninguna persona ni se
certifica el procedimiento/criterio de aceptación. **LEGAL REVIEW REQUIRED**.

## Datos afectados

Entrega actual: exclusivamente documentación pública de diseño, sin identidad
real, cédula real, cliente, contacto o credencial. Futuro catálogo conceptual:

| Familia | Clasificación/acceso propuesto | Historial y eliminación |
|---|---|---|
| Perfil | Datos privados de titular; proyección pública limitada por PC-02 | Conservar versión publicada actual; estados/resultados mínimos, sin duplicar datos completos. Retiro quita proyección pública/cachés; plazo PC-05 |
| Cédula/declaración | Datos profesionales personales restringidos a titular y revisor autorizado | Fuente/alcance/resultado/fecha mínimos; no CURP, RFC, identificación, escaneo o selfie en alcance inicial. Plazo PC-05 |
| Despacho/contexto | Metadatos privados de administración; presentación pública requiere proyección aprobada | Autor y controlador actual distintos; cierre no borra datos jurídicos de terceros. Plazo PC-05 y contratos futuros |
| Sede | Ubicación de operación privada por defecto | No domicilio personal publicable por inferencia; publicación/retención concreta antes de persistir |
| Invitación/membresía | Datos privados de organización; contacto solo para destinatario y actor autorizados | Estado/capacidades/versiones mínimos. Evidencia de membresía finalizada 30 días según D-032; invitación/token requieren minimización y vigencia del contrato antes de implementación |
| Eventos | Seguridad/historia restringidas | Actor/objeto lógicos, transición, fecha, resultado/versiones; sin email/cédula/tokens. Audit acceso 90 días D-032; historia nueva propuesta PC-05 |

La exposición en una fuente pública no autoriza reproducir todos sus campos en
Legalia. Separar finalidad de revisión, publicación y administración; no usar
consentimiento genérico como acceso universal. Los derechos del titular y la
retención legal son distintos de propiedad operativa. Auditoría no debe retener
un perfil completo después de su borrado; no cascada de 30 días que elimine audit
de 90 días ni referencias de terceros cuya política aún está pendiente.
Respaldos, exportaciones, cachés/builds y restauración necesitan reglas para que
un retiro no reaparezca publicado. No cargar contenido jurídico en C03.

## Seguridad

PC-01..PC-05 y modelo completo aprobado son condiciones previas a tablas.
No usar `user_metadata` o claims antiguos para membresía/capacidades; Auth/MFA
prueban identidad/nivel, no autorización profesional. Ruta privada web → FastAPI
→ PostgreSQL, con autorización de contexto/objeto/acción, roles/grants mínimos
y RLS probado; ningún navegador accede directamente a evidencia o membresías.
Errores uniformes no deben revelar existencia de objetos de otra práctica.

Salida/suspensión/revisión deben revocar acceso en la siguiente petición y en la
frontera transaccional de una acción ya iniciada. No retrasar revocación al refresco
JWT ni conceder continuidad por pestaña, token de invitación reutilizado o
asignación residual. Una participación legítima como cliente se evalúa aparte;
no recupera facultades profesionales ni se elimina automáticamente por la salida.
Ningún control puede retirar una copia ya descargada; no prometerlo.

Administrar miembros no concede lectura jurídica. Revisor de confianza tampoco
necesita clientes, asuntos, configuración de proveedores o secretos. Autoalta de
despacho, autoaprobación, cambios de roles y traslado de ámbito requieren controles
independientes. No soporte con superpoderes, RLS desactivado, BYPASSRLS ni
`service_role` universal para resolver fallos. No se habilitan funciones privilegiadas.

Contrastar privacidad, identidad profesional, representación, revisión/rechazo,
recursos y solicitudes de derechos con especialista mexicano: **LEGAL REVIEW
REQUIRED** antes de personas/datos reales. No aceptar apariencia de verificación
profesional como prueba. No se contactan terceros, consultan cuentas reales,
instalan dependencias o leen `.env`/credenciales/cookies; Kova fuera de alcance.

## Impacto futuro

C03 fija vocabulario y límites para C04 solicitudes/conflicto, C05 relaciones,
C06 descubrimiento y C09 documentos. Perfiles publicables no implementan ranking,
captación, servicios, precios, disponibilidad, reservas o cobro. Oficinas no deben
crear fragmentación de clientes ni mover propiedad de una relación.

Una membresía o capacidad mal delimitada contaminaría agenda, documentos, CRM y
futura IA; por eso el aislamiento y la salida preceden a esas funciones. IA
conserva alcance D-019/D-020/D-022; no verificará profesionales ni procesará
credenciales de C03. No nuevos proveedores o servicios de pago.

La cardinalidad de un despacho, soporte limitado y revisión manual restringen
operación real; no se inventan tiempos de respuesta o automatización para
ocultarlo. Métricas futuras mínimas: altas por estado, tiempo a decisión, rechazos
y cambios/retiradas de acceso; no publicar cifras personales ni historias de
credenciales. No declarar C03 Done hasta resolver confianza y probar recorridos
con aislamiento, negativas y operación de datos.

## Implementación propuesta

1. A0 revisa este checkpoint, reconcilia PC-01..PC-05 con D-031/D-032 y registra
   respuestas de Arturo. No volver a pedir aprobación de práctica propia más
   un despacho, mediación API, límites de sesión o retirada de facultades ya
   acordados. Aprobaciones parciales no habilitan entidades dependientes.
2. A1/A3 concretan modelo aprobado por dato: propietario operativo, cardinalidad,
   estados/transiciones, clasificación, historia, finalidades y retención. A2
   revisa amenazas/matriz por acción. No tablas mientras falte alguna de estas
   condiciones para la entidad correspondiente; no transformar entidades de
   este documento en migraciones por inferencia.
3. Después del checkpoint aprobado, A4/A5 preparan contratos API/UX: alta,
   revisión/publicación, creación/contexto, invitación/aceptación, capacidades y
   suspensión/salida/relevo. No añadir endpoints, pantallas o envío en esta entrega.
   A0 asigna archivos y revisor distintos; A3 controla migraciones.
4. A7/A2 deben probar con datos sintéticos aislados: práctica propia inaccesible
   desde despacho; contexto/ID ajeno denegado; administración sin lectura jurídica;
   invitación pendiente/ajena/reutilizada sin acceso; aceptación concurrente en
   dos despachos; pérdida de acceso con JWT/pestaña/asignación anteriores;
   participación cliente separada tras salida; reingreso sin restauración automática;
   autoaprobación y cambio de cédula/publicación denegados; aislamiento al reutilizar
   conexión; bloqueo/retorno de último administrador y cierre de cuenta sin acceso
   residual; retiro público y eliminación conforme a cada plazo aprobado.
5. Revisar negativos de rol/grants/RLS y transacciones reales; conservar pendientes
   de C02 real en vez de usar mocks como aceptación de producción. Verificar datos
   mínimos/retención y outputs saneados antes de commit o publicación por A0.
   C03 no habilita silenciosamente C04/C05 ni migra remoto por ese hito.

Verificación de esta entrega: contexto obligatorio y documentos relacionados
leídos; ocho secciones y cinco paquetes PC-01..PC-05; referencias locales revisadas.
Skill Supabase ya aplicada al trabajo de Identity; esta entrega no usa proveedor
ni SQL nuevo. Solo lectura de documentación pública; sin consultas a personas,
pruebas de aplicación, mocks funcionales, datos privados, commits o despliegue.
