# Handoff A2 — Planificación de servicios C08–C13

Fecha: 2026-10-16. Referencia asignada: `4eb597c`, rama `codex/identity-design`.
Alcance: siete documentos nuevos; sin código, migraciones, proveedores contratados,
lecturas remotas, pruebas externas, cambios de permisos o secretos. Arturo autorizó
Agent Teams para terminar planificación; no se interpreta como aprobación de negocio.

## Resultado y límites

Preparados seis checkpoints con ocho secciones obligatorias, modelos conceptuales,
propiedad/relaciones, estados, clasificación, historial, retención pendiente, límites
API/UX, descomposición implementable y aceptación negativa. Todos son **Proposed**;
C13 conserva el alcance funcional **Approved** D-019/D-020. No se crearon tablas ni se
implementó capacidad. C02/C03 conservan sus aprobaciones específicas; no se trasladan
30/90, SMTP o permisos de revisor a estos dominios por analogía.

| Capacidad/documento | Dependencia de producto | Bloqueo específico antes de código/datos | Trabajo posterior aprobable |
|---|---|---|---|
| [C08 pagos](../checkpoints/c08-payments-refunds.md) | C05 acuerdos/C07 reserva y condición de cobro | Vendedor/custodia, momento/precio, proveedor/gasto, reembolso/disputa/fiscal y retención | Transacciones, adaptador, webhooks, conciliación, aceptación sintética |
| [C09 documentos](../checkpoints/c09-private-documents.md) | C05 relación/permisos | Storage/tratamiento/costo, visibilidad, límites/escáner y conservación | Versiones privadas, cuarentena, descarga y borrado verificable |
| [C10 avisos](../checkpoints/c10-notifications.md) | Eventos de capacidad dueña y destinatarios | Finalidades/canales, preferencias, conservación; correo externo además dominio/presupuesto | Bandeja y outbox con consumo controlado; sin ampliar correo C02 |
| [C11 billing](../checkpoints/c11-subscriptions-billing.md) | C03/C05 comprador/contexto; C08 si se comparte integración | Oferta/precio, derechos, mora/cambio/baja, proveedor y retención fiscal | Evaluación de derechos, lifecycle y conciliación separados de honorarios |
| [C12 reseñas](../checkpoints/c12-reviews-reputation.md) | C07/C05 evidencia de prestación; C17 moderación | Elegibilidad, identidad pública, moderación/apelación, agregación y retención | Proyección pública mínima y revisión privada con separación de funciones |
| [C13 asistencia](../checkpoints/c13-ai-assistance-delivery.md) | C04 fuente de resumen; C05 borrador | Proveedor/tratamiento, persistencia, consentimiento, límites/gasto y calidad | Dos flujos aprobados con adaptador sin herramientas, sin enviar |

No citar cuotas, precios o reglas actuales de proveedor sin volver a documentación
oficial al comparar alternativas. No se aplicó skill de proveedor porque no se operó,
seleccionó ni revisó técnicamente un servicio externo en esta orden documental.
No preparar instaladores/migraciones aparentando que modelos Proposed están aprobados.

## Seis paquetes de decisión para A0; presentar por sesiones futuras

Estos paquetes agrupan decisiones, no son seis aprobaciones automáticas ni seis
preguntas para enviar ahora. Cada sesión debe concretar parámetros faltantes y
registrar alcance exacto; no basta «apruebo recomendado» cuando no hay cifras o proveedor.

1. **Dinero C08:** quién vende/cobra y condición por servicio; comparar proveedor con
   costos oficiales; aprobar cancelación/reembolso/disputa, responsable, fiscalidad y
   conservación. Recomendación a evaluar: cobro directo profesional y sin prepago universal.
2. **Oferta C11:** comprador/contexto, capacidades/planes/precio/moneda, ciclo y mora,
   baja/exportación y retención. Recomendar derechos explícitos por contexto, sin acceso
   jurídico por pagar. No adoptar precios/planes del documento histórico.
3. **Documentos C09:** proveedor/región/tratamiento/costo, matriz de compartir/revocar,
   tamaños/tipos/cuotas, escaneo/aislamiento y plazos de todas las versiones/backups.
   Recomendar cuarentena fail-closed y descarga con autorización vigente.
4. **Comunicación C10:** primeras finalidades internas y preferencias, TTL/retención,
   presupuesto/cola/responsable; después decidir dominio/remitente y correo externo.
   Recomendar bandeja interna primero, sin cambiar invitación interna C03.
5. **Confianza C12:** prestación elegible, exposición mínima de identidad, moderación
   y apelación con responsable, cálculo público, plazos/retención. Recomendar publicar
   solo tras capacidad operativa verificable; no vincular reputación a importe pagado.
6. **IA C13:** seleccionar proveedor/modelo/tratamiento y categorías permitidas,
   consentimiento, persistencia, cuotas cuantificadas/tope monetario y corpus/umbrales.
   Recomendar no guardar intentos por defecto y sin reintentos automáticos ambiguos;
   generación externa bloqueada hasta aprobar estos puntos.

Orden sugerido: completar decisiones de atención C04/C05 y reserva C07; documentos y
avisos internos pueden discutirse antes de monetización. IA no bloquea recorrido manual.
Si C15 incluye pagos, su aceptación depende de C08 completo, no solo checkout. Publicar
reseñas sin moderación operativa o cobrar suscripciones sin derechos definidos no es
un incremento entregable. Todas estas prioridades son propuestas para el coordinador.

## Invariantes afinados por revisión cruzada

Son requisitos **Proposed**, no decisiones aprobadas ni implementación:

- C08 revalida contexto, participantes, versión aceptada C05 y vigencia al crear orden
  y antes de captura; pagar no acepta cambios posteriores del acuerdo.
- C09 compartir se limita a participación/permisos C05; uploader o administrador no
  amplían audiencia por sí mismos. Descarga tras cierre exige política expresa.
- C10 reautoriza inmediatamente antes de cada envío externo, además de materializar
  y abrir; retirada/relevo suprime destinatarios pendientes que ya no sean elegibles.

## Revisión y aceptación documental

A0/A2 independiente debe comprobar consistencia con los checkpoints C04–C07 y C16/C17
que otros agentes redactan en paralelo. Enlaces a esos futuros archivos no se inventan;
las dependencias se expresan por capacidad. Revisión jurídica mexicana pendiente en
pagos/fiscalidad, contenido, privacidad/transferencias, moderación y contratación:
**LEGAL REVIEW REQUIRED**. No se emiten recomendaciones jurídicas normativas.

No pruebas de software ejecutadas: no cambió código. Verificar encabezados, enlaces y
salida de secretos redactada antes de commit/push; solo el coordinador integra/publica.
Ningún ejemplo usa email real, datos de cliente, credenciales ni valores privados.
