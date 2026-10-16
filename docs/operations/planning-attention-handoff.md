# Handoff A1 — Planificación de atención C04–C07

Fecha: 2026-10-16. Base común `4eb597c`, rama `codex/identity-design`.
Estado: **Proposed / Requires Arturo**, no implementación ni aprobación global.
Orden recibida: terminar diseño pendiente de C04/C05/C06/C07, cinco archivos
propios; A0 integra y A2 revisa de forma independiente. Sin otros agentes,
commits, dependencias nuevas, secretos, proveedores ni mutaciones remotas.

## Resultado entregado

| Capacidad | Checkpoint | Primer corte recomendado, todavía propuesto |
|---|---|---|
| C04 | [Solicitudes/conflicto](../checkpoints/c04-requests-conflicts.md) | Solicitud a profesional elegido, intake progresivo, respuesta y retirada; sin difusión, IA, cobro ni archivos |
| C05 | [Acuerdos/seguimiento](../checkpoints/c05-service-relationships.md) | Relación con responsable único, acuerdo versionado, aceptación, siguiente acción compartida y cierre |
| C06 | [Catálogo](../checkpoints/c06-discovery-catalog.md) | Directorio público voluntario y filtros deterministas sobre oferta elegible; no matching por relato ni patrocinio |
| C07 | [Reservas/consultas](../checkpoints/c07-bookings-consultations.md) | Coordinación manual con confirmación transaccional y ocupación transversal mínima; sin pago ni agenda externa |

Los cuatro checkpoints tienen las ocho secciones exigidas; propiedad operativa,
relaciones, estados propuestos, clasificación, historia y retención pendiente
explícitas. Cada uno incluye API/UX a contratar después de aprobar, invariantes,
negativos de aislamiento/concurrencia y dependencias. No se preparó SQL/DDL ni se
considera el modelo Approved por estar completo como propuesta.

## Reconciliación de decisiones

- D-015/016 ya aprueban relación de servicio central y búsqueda gratuita; no se
  vuelven a preguntar. Tampoco se reabre D-031/D-040/D-041 sobre C02/C03.
- C03 aprobado no significa profesional real habilitado: revisión/antisuplantación,
  asignaciones limitadas y aceptación operativa siguen con sus gates.
- D-007 (revisión antes de cobro), D-009 (clases de servicio), D-013 (atención con
  clientes propios primero), D-017 (respuesta supervisada) y D-010 (patrocinio)
  no se convierten en decisiones por aparecer en documentos históricos.
- Cuenta/membresía30d y auditoría90d de C02, y plazos específicos C03 aprobados,
  no fijan conservación de relato/partes/acuerdo/consulta/reserva. No herencia
  automática; no conservación indefinida. **LEGAL REVIEW REQUIRED**.
- Morelia, cobertura concreta, SLA, especialidades, tarifas, cancelaciones y
  proveedor de calendario no están aprobados. Nombre vigente Legalia; no piloto.

## Seis decisiones máximas para este alcance

A0 debe presentar solo la primera tanda que quepa en el límite global de6 preguntas
entre equipos. Orden recomendado: AT-01/02/03 y proceso AT-04; AT-05/06 después.
No interpretar respuestas de un paquete como aprobación de todos los demás.
A significa recomendación pendiente, B alternativa; ninguna está aceptada aún.

| ID/prioridad | Pregunta a Arturo | A recomendada y consecuencia | B alternativa y consecuencia |
|---|---|---|---|
| AT-01 / primera | ¿El primer recorrido funcional se centra en atención directa con un profesional ya elegido, antes de captación/reservas/pagos? | Sí: C04 mínimo + C05 responsable único, acuerdo y siguiente acción. Cliente autenticado actuando por sí mismo; sin importación de contactos, consulta artificial o cobro gestionado por Legalia. Da utilidad de seguimiento sin depender de tráfico; condiciones del servicio deben ser suficientes y revisadas | Empezar por descubrimiento→consulta→pago C06/07/08. Exige catálogo, disponibilidad, política comercial, proveedor de pagos y excepciones antes de un recorrido completo; mantener C04/05 en diseño hasta esos gates |
| AT-02 / primera | ¿La solicitud inicial se dirige a un solo profesional habilitado del contexto elegido, con revisión manual antes de ampliar información/acordar atención? | Sí: información progresiva, profesional elegido como lector, rechazo compartible sin datos de otro cliente, retirada y no reenvío automático. No SLA numérico ni sanciones hasta definir capacidad/horarios; estado/fechas y salida visibles. Reasignación requiere destinatario autorizado y acción explícita | Bandeja del despacho con intake delegado. Antes de habilitar hay que aprobar quién ve qué, asignación y revocación; administrador no recibe lectura jurídica por ser administrador |
| AT-03 / primera | ¿El primer C05 usa responsable único, acuerdo versionado aceptado por cliente/profesional y portal mínimo compartido, manteniendo notas internas separadas? | Sí: solo acuerdo/estado/responsable/próxima acción y actualizaciones explícitamente compartidas. Relevo ordinario requiere aceptación del cliente y nuevo responsable; retiro urgente del anterior no espera relevo. Sin firma avanzada, poderes, cálculo procesal o transferencia entre contextos | Preparar desde inicio equipo con varios participantes jurídicos. Requiere matriz de colaboración y delegación, reasignación, audiencias y concurrencia antes de implementación; no acceso general del despacho |
| AT-04 / primera, gate | ¿La persistencia de contenido jurídico espera una política por familia revisada, sin trasladar automáticamente30/90d de Identity? | Sí: preparar la matriz de relato/partes/acuerdo/reserva/consulta, plazo y evento inicial, derechos/bloqueos justificados, backup/restore y responsable para revisión jurídica. Ninguna tabla/familia nueva con retención pendiente queda Ready; se puede avanzar contratos/datos sintéticos sin crear almacenamiento del dominio | Separar un corte solo público de catálogo mientras se resuelve política jurídica. No habilita solicitudes/acuerdos reales ni permite guardar metadatos personales sin su propio plazo; reduce utilidad inicial a descubrimiento |
| AT-05 / posterior | ¿El primer descubrimiento usa solo directorio orgánico, publicación voluntaria, filtros explícitos y orden por nombre de presentación con desempate estable, sin patrocinios? | Sí: no promete mejor abogado, disponibilidad o calidad; no texto jurídico libre, personalización ni historial de búsqueda persistido por aplicación. Lista concreta de áreas/jurisdicciones, editor y condiciones de oferta se revisa antes de cargar catálogo | Posponer buscador público y continuar selección directa consentida; evita aparentar cobertura sin oferta y deja captación para el checkpoint propio |
| AT-06 / posterior | ¿La primera agenda es coordinación manual interna, con aceptación coincidente y confirmación atómica tras revisión, sin integrar calendarios/cobro? | Sí: una ocupación profesional común evita doble reserva sin revelar contexto ajeno; propuesta no reserva. Política concreta de duración/buffers/zona/cambios/no-show y retención se aprueba antes de programarla | Autoservicio de reservas unido a C08. Requiere holds/vigencia/pago/cancelación/reembolso/conciliación y operación de excepciones completos; sin esos contratos la agenda sigue en diseño |

AT-04 propone el proceso de cierre, **no un plazo numérico ya decidido ni autorización
de guardar contenido mientras llega revisión**. A0 debe preparar la matriz concreta
y devolver modelo, matriz y política por familia a Arturo para aprobación antes
de tablas. Con esas aprobaciones puede asignarse implementación local sintética;
la revisión jurídica permanece pendiente como gate para activar tratamiento real,
sin afirmar dictamen ni exigir certificación jurídica previa a todo trabajo local. No
se agrega una séptima pregunta a esta sesión ni se oculta ese gate en un default.
AT-05/06 también tienen parámetros de catálogo/servicio que siguen explícitamente
pendientes y se resuelven en sus checkpoints; aprobar dirección no equivale a Ready.

## Órdenes listas para emitir una vez aprobados sus gates

| Orden posterior | Dueño propuesto | Dependencia y entrega verificable |
|---|---|---|
| AT-DATA | A3 único escritor de migraciones | Modelo y retención por familia aprobados → diccionario, referencias de contexto, invariantes/versiones, grants/RLS y pruebas aisladas; sin destino remoto automático |
| AT-SECURITY | A2 distinto del autor | AT-02/03 → matriz actor/objeto/acción/estado, amenazas de partes/acuerdo/audiencia, negativos y revisión del plan de eliminación |
| AT-CONTRACT | A4 con A5 | Datos y matriz revisados → contrato HTTP/versiones/idempotencia/errores, estados UX y permisos de cada campo; no endpoints a partir de esta tabla por inferencia |
| AT-VERTICAL | A4/A5 en archivos distintos asignados por A0 | Gates C02/C03 y checkpoint correspondiente → mínimo C04/C05 integrado en local con fixtures sintéticos; sin IA/cobro/documentos/agenda implícitos |
| AT-QA | A7 y revisión A2 | Contrato estable → autorización ajena, admin sin lectura, revocación/concurrencia, aceptación obsoleta, no filtrado de notas, borrado/restore y E2E; no declarar Done por mocks |
| AT-DISCOVERY / AT-SCHEDULE | Nueva orden de A0 después | AT-05 o AT-06 y sus parámetros completos → corte propio probado, sin bundlearlo como consecuencia automática de AT-01 |

A0 asigna rutas exactas al emitir órdenes; aquí solo se propone secuencia, no se
habilita a agentes a tomar archivos compartidos o comenzar implementación.

## Verificación y límites

Se leyeron instrucciones y fuentes obligatorias, documentos de producto relevantes
y checkpoint C03 con sus aprobaciones posteriores. Se validaron los ocho encabezados de cada checkpoint y
todos los enlaces relativos de los cinco entregables; pasan. No prueba de API/SQL/browser, correo,
reserva, pago, contrato jurídicamente válido o retención real ejecutada en esta
entrega. Ningún secreto/dato de usuario consultado ni incluido. C02 real, C03
profesional, restauración y responsable jurídico siguen dependencias operativas.
