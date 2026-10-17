# C13 — Entrega de resumen y borrador asistidos

Fecha: 2026-10-16. Estado: **Proposed diseño técnico; flujos Approved D-019/D-020**.
Complementa [checkpoint funcional de IA](ai-assistance.md), sin sustituir su alcance.

## Lo que entiendo

AI-01 prepara un resumen revisable de solicitud a petición de quien la escribe.
AI-02 prepara un borrador editable a partir del texto autorizado que el profesional
selecciona, con copia manual como acción final. El original se conserva. No hay envío,
investigación jurídica, herramientas autónomas o decisiones tomadas por el modelo.

## Decisiones tomadas

- D-019/D-020 aprueban solo esos dos flujos, generación expresa, revisión/edición,
  aceptación/descarte y copia manual; no generación continua al escribir.
- D-022 aplaza OCR, embeddings, extracción, indexación y RAG documental.
- React/FastAPI están aprobados. Proveedor/modelo, tratamiento, retención, presupuesto
  y cantidades de cuota siguen pendientes; no se transmite información jurídica.
- Cerrar planificación no permite probar con clientes ni contenido real en un proveedor.

## Decisiones pendientes

| ID | Opciones y recomendación propuesta | Bloquea |
|---|---|---|
| AI-01D | Elegir proveedor/modelo, región/tratamiento, uso para entrenamiento, subencargados y tratamiento de entrada/salida; recomendar comparar garantías necesarias antes de precio | Adaptador externo/datos |
| AI-02D | Aviso/consentimiento y categorías permitidas; recomendar previsualización exacta de selección y exclusión de datos no necesarios, revisada jurídicamente | Datos reales |
| AI-03D | Persistir solo resultado aceptado o también borradores/intentos; recomendar no guardar intentos por defecto, con plazos explícitos para todo estado | Modelo de datos |
| AI-04D | Fijar límites de entrada/salida, concurrencia, cuota por contexto y tope monetario global; responsable y corte sin sobregasto | Habilitación/costo |
| AI-05D | Aprobar corpus sintético, umbrales de calidad/seguridad, manejo de errores y quién autoriza activar | Aceptación/release |

Consentimiento, información jurídica y transferencias: **LEGAL REVIEW REQUIRED**.
Este diseño no elige proveedor ni establece garantías contractuales no verificadas.

## Diseño propuesto

API autoriza fuente/actor/contexto → usuario previsualiza selección exacta → confirma
acción → servidor valida límites y reserva presupuesto de forma atómica → adaptador
sin herramientas procesa la selección → valida formato/salida → reautoriza acceso →
UI muestra resultado asociado a versión de entrada → usuario edita/acepta o descarta.
No lectura automática del expediente, de documentos C09 o de otros mensajes.

| Entidad conceptual | Propiedad y relaciones | Estados propuestos |
|---|---|---|
| GenerationRequest | Actor/contexto + función AI-01 o AI-02 + fuente tipada/versionada | requested, budget_reserved, running, ready, failed, cancelled, stale, discarded |
| AcceptedSummary | Solicitud C04/version original + texto editado aceptado y autor | current, needs_review, superseded |
| MessageDraft | Actor profesional/contexto/fuente autorizada; no registro de entrega | editing, copied, discarded |
| BudgetReservation | Generación/contexto/periodo y tope global, sin texto | reserved, settled, released, reconciliation_required |
| UsageReceipt | Consumo medido/modelo/version/función/código de resultado | estimated, confirmed, unknown |

El original permanece fuente de hechos; el resumen aceptado no reemplaza relato ni
certifica información. Si cambia la entrada durante generación, respuesta queda stale
y no se acepta silenciosamente. Antes de copiar AI-02 se exige revisión de la versión
visible; copied no significa enviado ni recibido. Si se pierde acceso, resultado no
se entrega aunque el proveedor haya terminado. Si proveedor ya consumió, consumo sigue
contando; cancelar localmente no demuestra cancelación/facturación cero del proveedor.

Idempotencia por intención/versión y función, con conflicto si se reutiliza clave para
otra entrada; no caché de texto compartida entre contextos. Fallo/timeout ambiguo no
reintenta automáticamente una generación potencialmente facturada. Reserva se liquida
contra consumo comprobable o queda conciliable; no se libera para permitir gasto
ilimitado. Agotamiento de cuota siempre ofrece edición manual de texto original.

API candidata: `POST /api/ai/summary-generations` desde solicitud propia,
`POST /api/ai/message-draft-generations` desde selección profesional autorizada,
consulta/cancelación por generación y aceptación explícita de resumen con versión.
No endpoint de enviar mensaje, subir documentos, recuperar expediente completo ni
consultar modelo libre. La UI muestra fuente, estado/revisión necesaria y error/cuota
sin perder trabajo manual. Contrato de errores sin detalles internos del proveedor.

## Datos afectados

Entrada/salida jurídica altamente restringida; no logs de prompts, respuestas o IDs
externos enlazables en telemetría. Fuente y selección mínimas en proceso; persistencia
exacta pendiente AI-03D. Resultado aceptado comparte control de acceso de su fuente,
con procedencia humana/IA y versión. Metadatos de consumo también tienen clasificación
restringida cuando se vinculan a actor/contexto.

Retención propia y del proveedor **pendientes y separadas**. No heredar 30/90 de C02.
Definir descarte, caducidad de solicitudes, conservación de resultado aceptado, recibos
mínimos y backups; eliminar entrada local no demuestra borrado del proveedor. No crear
tablas antes de aprobar estados/propiedad/plazos definitivos.

## Seguridad

Tratar texto seleccionado como datos no confiables, incluso si contiene instrucciones.
Proveedor no tiene herramientas, conexiones a recursos, navegación ni secretos del
sistema. Autorizar antes y después; seleccionar un ID no amplía permiso. Secretos del
proveedor solo en runtime; redactar errores y deshabilitar captura de contenido en SDK,
trazas y retries. Ningún fallo se resuelve con service_role o contexto profesional global.

Validar longitud/tipo de salida y renderizar texto seguro. El prompt no incorpora datos
ajenos ni instrucciones de usuario como autoridad de sistema. Evitar inventar hechos,
honorarios, fechas o compromisos; revisión humana no sustituye evaluación sistemática.
No prometer anonimización mediante filtro superficial ni ocultar transferencia externa.

## Impacto futuro

La gestión de consumo puede servir a ambos flujos; cada uno mantiene permisos y pruebas
propios. Suscripción C11 no habilita IA sin tratamiento y presupuesto separados. Nuevas
funciones, envío, OCR/RAG/documentos requieren nuevo checkpoint; no se activan al añadir
un proveedor. La alternativa manual preserva utilidad si IA se aplaza.

## Implementación propuesta

1. C04/C05 proveen fuentes/versiones y permisos; A1/A2 cerrar AI-01D..05D sin reabrir
   los dos flujos ya aprobados. A3 valida modelo/retención antes de tablas.
2. A8 adaptador sintético determinista y reserva de presupuesto; A4 autorización,
   idempotencia/estados; A5 revisión/manual copy; A7 evaluación reproducible.
3. Después de proveedor/tratamiento/gasto aprobados, prueba externa solo con corpus
   sintético y costo autorizado; datos reales esperan revisión y autorización aplicable.

Negativos: inyección no ejecuta acciones ni obtiene otras fuentes; selección ajena se
rechaza; modificación de entrada marca stale; membresía retirada impide obtener salida;
doble clic no duplica gasto; dos procesos no superan tope; timeout no reintenta a ciegas;
fallo mantiene original; resumen no envía solicitud; copiar borrador no envía mensaje;
salida peligrosa no ejecuta HTML; logs no contienen marcadores sintéticos de contenido.
Evaluar fidelidad/omisiones/atribuciones y hechos inventados con corpus de casos difíciles;
umbrales y responsables pendientes. No generación, transmisión ni evaluación ejecutada aquí.
