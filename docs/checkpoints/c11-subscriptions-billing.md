# C11 — Suscripciones, derechos de uso y billing

Fecha: 2026-10-16. Estado: **Proposed; no aprobado para implementar**.
La hipótesis de suscripción D-008 no es una decisión de monetización.

## Lo que entiendo

Legalia puede vender herramientas recurrentes a independientes y despachos pequeños,
sin confundir esa compra SaaS con los honorarios que el cliente paga al profesional.
Un plan describe oferta comercial; una suscripción registra el contrato; un derecho
de uso autoriza una capacidad, sujeto siempre a permisos del recurso. Falta aprobar
qué se vende, a quién, por cuánto y con qué consecuencias al incumplir el pago.

## Decisiones tomadas

- D-014 prioriza independientes y despachos pequeños; D-003 permite práctica propia y
  un despacho. Esto no determina una sola factura, cantidad de asientos ni plan.
- D-016 mantiene búsqueda gratuita; cobrar por herramientas no cobra por buscar.
- Los planes conceptuales de `07_business_model.md` son hipótesis, sin precios aprobados.
- Cloudflare Free y la VM aprobada son presupuesto de infraestructura, no pricing SaaS.

## Decisiones pendientes

| ID | Opciones y recomendación propuesta | Bloquea |
|---|---|---|
| SUB-01 | Suscripción por contexto, por asiento, por usuario o híbrida; recomendar evaluar por contexto con derechos explícitos y no mezclar práctica/despacho | Comprador, titularidad y planes |
| SUB-02 | Aprobar catálogo de capacidades, límites, periodos, precios, moneda/impuestos y alcance gratis; decidir si existe trial | Oferta y contrato |
| SUB-03 | Proveedor propio y flujo de cobro/factura; evaluar reutilizar proveedor de C08 solo si sirve sin mezclar fondos/contextos | Integración/gasto |
| SUB-04 | Aprobar mora, gracia, cambio/cancelación/reembolso, reactivación y acceso/exportación tras baja; recomendar degradación explícita sin borrado automático | Entitlements y ciclo |
| SUB-05 | Definir conservación financiera/contractual, autoridad operativa y obligaciones fiscales | Datos y operación |

Términos, renovación, cancelación, información fiscal y retención: **LEGAL REVIEW REQUIRED**.

## Diseño propuesto

| Entidad conceptual | Propiedad y relación | Estados propuestos |
|---|---|---|
| PlanVersion | Catálogo comercial de Legalia, inmutable tras contratar | draft, available, retired |
| BillingAccount | Un comprador/contexto por definir SUB-01, representantes explícitos | active, restricted, closed |
| Subscription | Cuenta de billing + versión aceptada de plan, periodo y proveedor | pending, active, past_due, cancellation_scheduled, cancelled, ended |
| EntitlementGrant | Contexto + capacidad + límite + origen/periodo; evaluado con permisos C03/C05 | active, exhausted, suspended, expired |
| BillingInvoice | Cuenta/periodo/importes/ref proveedor; comprobante fiscal separado si procede | draft, issued, paid, void, disputed |
| BillingAdjustment | Cambio, crédito o reembolso trazable, relacionado con factura | requested, approved, applied, failed |

Una suscripción activa no concede acceso a expedientes ajenos. Un cobro tardío no activa
indefinidamente una versión de plan vencida; se concilia contra periodo/intención.
El servidor calcula derechos desde estado propio confirmado y contrato aprobado;
no confiar en precio de navegador ni claim editable. Webhooks deduplicados y firmados
según proveedor; recibos no bastan para actualizar automáticamente todo el contexto.

Cambios de plan preservan versión y fecha efectiva; efecto inmediato, prorrateo y
créditos quedan pendientes SUB-04. Concurrencia de dos cambios produce una decisión
serializada/conflicto, no dos contratos. Si el proveedor no responde, mostrar pending;
no bloquear arbitrariamente consulta de datos preexistentes ni fingir pago exitoso.

Contratos candidatos: listar planes publicados, consultar suscripción/derechos del
contexto, solicitar alta/cambio/cancelación, consultar facturas propias. El pagador y
el administrador del despacho pueden ser actores diferentes; permisos específicos
pendientes, sin otorgar acceso jurídico al pagador. UI muestra costo/periodicidad,
próxima fecha efectiva y consecuencias antes de confirmar. No casillas de renovación
preseleccionadas o promesas de devolución sin contrato aprobado.

## Datos afectados

Cuenta de facturación, representantes autorizados, referencia opaca de pago, importes,
moneda, impuestos si se requieren, versión aceptada y tiempos. Datos fiscales con
clasificación financiera restringida separada de contacto jurídico. Historial de
contrato y cambios; métricas agregadas sin identidad del cliente o asunto.

Retención **pendiente SUB-05**; 30/90 de C02/C03 no decide duración de facturas ni
contratos. Cancelar no borra datos jurídicos ni sustituye la política C05/C09. Definir
acceso mínimo/exportación tras cierre y ruta de eliminación según cada categoría;
conservar prueba de obligaciones requiere motivo y plazo explícitos, no infinito.

## Seguridad

Autorización en servidor por comprador/contexto/acción; validación de roles vigentes.
No rutas de pago a fondos de profesionales por confusión con C08. Secretos solo en
runtime y proveedor de captura; ningún PAN/CVV en Legalia. Límites por capacidad
atómicos frente a concurrencia; caída de facturación no se resuelve dando admin o
ignorando autorización. Webhooks autenticados con replay/idempotencia y conciliación.

## Impacto futuro

Comisiones C08 y suscripciones C11 se contabilizan por separado. Add-ons, enterprise,
SSO, créditos por IA y promociones son futuras decisiones; no incluidas por existir
una entidad Plan. C13 necesita presupuesto independiente incluso si se vende en plan.

## Implementación propuesta

1. A1/A2 cerrar SUB-01..05 y dependencias C03/C05/C08; validar matriz y retención.
2. A3 modelo/migraciones locales; A4 evaluación de derechos; A8 billing sintético;
   A5 condiciones y estados; A7 pruebas de límites y transición concurrente.
3. Proveedor/sandbox/conciliación y aceptación antes de cobrar recurrentemente.

Negativos: pagar plan no da acceso a otro contexto; usuario retirado no cambia billing;
precio manipulado no se acepta; webhook duplicado no renueva dos periodos; cancelación
repetida no cobra; límite concurrente no se excede; mora no elimina expedientes;
comprobante ordinario no se presenta como CFDI; fallo de proveedor queda conciliable.
No se ejecutaron cobros ni implementaron entitlements en este checkpoint.
