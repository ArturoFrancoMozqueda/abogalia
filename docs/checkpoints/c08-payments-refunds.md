# C08 — Pagos, reembolsos y conciliación

Fecha: 2026-10-16. Estado: **Proposed; no aprobado para implementar**.
Base documental: D-005, D-015, D-016, D-025; D-007 y D-008 permanecen pendientes.
Este checkpoint no selecciona proveedor, intermediación, precio ni política fiscal.

## Lo que entiendo

El cliente necesita conocer condiciones y estado del dinero; el profesional necesita
conciliar un cobro con una reserva o acuerdo concreto. Pago, aceptación profesional,
confirmación de reserva y prestación efectiva son hechos distintos. La navegación de
retorno del checkout no demuestra un cobro. C07 y C05 deben definir el hecho que
habilita cobrar y el efecto sobre la reserva. No hay prepago universal aprobado.

## Decisiones tomadas

- D-015 incluye cobros dentro de la relación de servicio; D-016 distingue búsqueda
  gratuita y servicios profesionales con precio o cotización.
- React/FastAPI y separación de prácticas permanecen; ninguna de estas decisiones
  determina quién es el vendedor, receptor del dinero o responsable de reembolsar.
- No existe aprobación de comisión, proveedor de pago, custodia de fondos ni fiscalidad.

## Decisiones pendientes

| ID | Alternativas y recomendación propuesta | Bloquea |
|---|---|---|
| PAY-01 | Profesional cobra directamente mediante proveedor, o plataforma intermedia con liquidaciones. Recomendar evaluar primero cobro directo para reducir operación, sujeto a viabilidad comercial y legal | Titularidad, contratación y selección de proveedor |
| PAY-02 | Pago al aceptar, anticipo, pago posterior o condición por servicio. Recomendar condición versionada por servicio, visible antes de aceptar; sin imponer prepago universal | Máquina reserva/pago |
| PAY-03 | Aprobar proveedor, cuenta propia, monedas, métodos, costos y límites después de comparación oficial actual | Adaptador y gasto |
| PAY-04 | Definir cancelación, ausencia, parcialidad, ventanas, responsable de disputa y prueba necesaria; no inventar porcentajes o plazos | Refund y disputas |
| PAY-05 | Definir evidencias contables, tratamiento fiscal, responsable y conservación mínima por categoría | Retención y puesta en producción |

Contratación, intermediación, reembolsos, contracargos y fiscalidad: **LEGAL REVIEW REQUIRED**.

## Diseño propuesto

Cobro creado en servidor desde versión aceptada de condiciones. El cliente no decide
importe, moneda, beneficiario ni contexto. Adaptador de proveedor aislado del dominio;
la URL de retorno solo solicita estado vigente a la API. Un evento autenticado del
proveedor se deduplica y procesa en transacción. Si llega fuera de orden, se conserva
su recibo mínimo y se concilia con el estado autoritativo; no se retrocede un pago
liquidado por una notificación antigua. Discrepancias van a operación C17.

| Entidad conceptual | Propiedad y relación | Estados propuestos |
|---|---|---|
| PaymentOrder | Un contexto vendedor por acordar; reserva C07 o acuerdo C05 tipado, nunca ambos implícitos | draft, awaiting_payment, paid, cancelled, reconciliation_required |
| PaymentAttempt | N intentos por orden, referencia opaca única de proveedor | created, pending, authorized, captured, failed, expired |
| Refund | N por pago capturado; motivo estructurado, actor y autorización específica | requested, approved, pending_provider, succeeded, failed, cancelled |
| ProviderEventReceipt | Integración + ID de evento únicos; enlaza intento/reembolso | received, applied, duplicate, reconciliation_required |
| ReconciliationItem | Diferencia concreta entre evidencia propia y proveedor | open, investigated, resolved |
| Dispute | Hecho separado del Refund; referencia al pago y operador autorizado | opened, evidence_due, submitted, resolved |

Invariantes propuestos de vinculación: al crear la orden y antes de solicitar captura,
revalidar contexto, participantes autorizados, versión aceptada del acuerdo C05 y su
vigencia. Un pago no acepta una versión nueva del acuerdo ni sustituye consentimiento;
si cambian condiciones o participantes, detener y resolver mediante el flujo C05/C07
aprobado antes de cobrar. Una confirmación externa tardía se concilia sin fingir que
la versión nueva fue aceptada.

Invariantes: suma de reembolsos exitosos y reservados no supera importe capturado;
concurrencia de dos solicitudes se serializa sobre ese saldo. Una captura tardía tras
expirar reserva produce excepción conciliable y nunca asigna horario ocupado.
Fracasar al reembolsar no marca dinero devuelto. La confirmación del proveedor se
interpreta según su contrato documentado, sin asumir equivalencia entre autorización
y captura. Cada operación externa tiene clave de idempotencia por intención; repetir
una clave con otro contenido devuelve conflicto.

Contratos candidatos: `POST /api/payment-orders` desde objeto elegible,
`GET /api/payment-orders/{id}`, `POST /api/payments/{id}/refund-requests` y webhook
server-to-server específico del proveedor que se elija. Endpoint separado de operación
para aprobar/conciliar; cliente no puede autocertificar pagos. La UI muestra importe,
moneda, condiciones vigentes y estados pendientes/fallidos; no promete factura fiscal
por mostrar un recibo de pago. Contratos y permisos finales requieren aprobación.

## Datos afectados

Datos financieros restringidos: importes en unidades menores y moneda, referencias
opacas de proveedor, versión de condiciones, actor/contexto, tiempos y códigos de
resultado permitidos. No almacenar tarjeta, CVV, credenciales ni payload crudo de
webhooks. Evidencia fiscal identificable, si se requiere, tendrá clasificación y
acceso separados. Historial de transiciones con antes/después estructurados; sin
relato jurídico, email o descripción del servicio en logs generales.

Retención: **pendiente por categoría y revisión jurídica**; 30/90 de C02/C03 no se
extiende a dinero. Definir conservación de registros conciliados, disputas, recibos
webhook e idempotencia, y tratamiento de backups. No hardcodear borrado por cierre de
cuenta cuando existan obligaciones por resolver. Dicha obligación debe documentarse;
no equivale a autorizar conservación ilimitada.

## Seguridad

Autorizar objeto/contexto/acción en API y datos; miembros de despacho sin capacidad
financiera no ven pagos. Operación financiera no concede acceso al asunto. Webhooks
verifican autenticidad y anti-replay según contrato aprobado antes de encolar; fallos
no alteran dinero. El secreto de webhook queda en runtime, nunca navegador/logs.
Comprobar límites, revisión reforzada para reembolsos y atribución del operador;
no seleccionar ahora una nueva capacidad o umbral monetario. Proveedor alojará captura
de tarjeta si esa alternativa se aprueba; no construir formularios que custodien tarjetas.

## Impacto futuro

C07 consume resultado de pago sin acoplar horarios al proveedor. C11 tendrá su propio
ciclo de facturación; un cobro profesional no activa una suscripción SaaS. C12 no usa
importe pagado como prueba suficiente de atención. Liquidaciones, escrow y fiscalidad
avanzada requieren alcance y responsabilidad específicos, no un campo añadido.

## Implementación propuesta

1. A1/A2 cerrar PAY-01..05 y contrato C07/C05; A3 modelo/matriz revisados antes de SQL.
2. A8 adaptador sintético de pago y contrato de firma/idempotencia; A4 transacciones,
   saldos y conciliación; A5 estados y condiciones; A7 aceptación independiente.
3. Tras proveedor/costo aprobados, sandbox propio y reconciliación real antes de cobros.

Aceptación negativa: adulterar importe/moneda/beneficiario no cobra; webhook sin firma,
repetido o desordenado no duplica efectos; pago ajeno no se enumera; dos reembolsos no
exceden saldo; captura tardía no ocupa horario ajeno; fallo de red y reintento no duplican
cargo; recibo no se etiqueta factura fiscal; rollback no borra evidencia financiera.
No se ejecutaron pagos, webhooks ni pruebas en esta entrega documental.
