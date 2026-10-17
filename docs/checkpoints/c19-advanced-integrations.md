# C19 — Integraciones avanzadas futuras

Fecha: 2026-10-16. Estado: **Proposed / Deferred**. No conexiones externas ni permisos
nuevos autorizados por este documento.

## Lo que entiendo

Calendarios externos, WhatsApp/SMS, exportación y API pueden reducir duplicidad,
pero amplían datos, destinatarios y superficie de acceso. Se reabren según una
necesidad medible, después de aceptar la capacidad propietaria de esos datos.

## Decisiones tomadas

Suite y credenciales propias de Legalia; Kova excluido. El correo transaccional
aprobado usa Supabase/Resend y no se sustituye por esta visión. Hosting y presupuesto
actuales permanecen. Un conector autenticado no autoriza sincronización, envío,
exportación, lectura de terceros o tokens con scopes más amplios.

## Decisiones pendientes

Seleccionar necesidad/proveedor y dirección (lectura, escritura o bidireccional),
campos, actor que autoriza y cuenta destinataria. Consentimiento, tratamiento,
retención local/proveedor, presupuesto, cuotas y soporte. Política de conflictos,
reintentos, backfill, eliminación/desconexión y recuperación. Para API/exportación:
autorización por objeto, formato, límites, caducidad y custodia de descarga.
No elegir valores ni un estándar OAuth concreto sin proveedor/flujo definido.

## Diseño propuesto

ExternalConnection pertenece a actor/contexto autorizados y capacidad específica;
ScopeGrant refiere conexión y alcance mínimo; SyncOperation refiere versión de
objeto fuente y destino; DeliveryReceipt guarda resultado mínimo, no mensaje completo.
ExportRequest pertenece a solicitante autorizado y alcance congelado. Modelos
conceptuales sin tablas, tokens persistidos o webhooks reales.

Conexión: propuesta → consentimiento pendiente → activa → suspendida/revocada →
retirada. Operación: pendiente → confirmada/fallo/indeterminada; respuesta perdida
no es entrega confirmada. Diseñar idempotencia y reconciliación antes de reintentar
una escritura. Revocación detiene nuevas acciones; no promete retirar copias ya
entregadas. El calendario externo no decide propiedad ni autorización interna.

## Datos afectados

Identificadores externos y tokens privados en custodia separada; payload jurídico
fuera de alcance por defecto hasta decidir campos exactos. Propuesta de minimización:
calendario ocupado/libre antes de títulos o participantes; exportación acotada antes
de API general. Son alternativas a evaluar, no permisos concedidos. Retención,
historia de sincronización, tombstones y copias externas pendientes; no aplicar
30/90 de Identity ni afirmar borrado remoto por retirar conexión.

## Seguridad

No secretos en URLs/logs/chat. Webhooks futuros requieren autenticidad, replay y
límites; contenido entrante es no confiable y no controla herramientas/agentes.
Evaluar necesidad de skill específica antes de implementar correo entrante. Tokens
mínimos, separación por producto/conexión y revocación real; no service_role como
API de integración. **LEGAL REVIEW REQUIRED** para destinatarios/tratamiento.

## Impacto futuro

Dependencias por integración: calendario C07, mensajes C10, exportación C05/C09,
cobros C08/C11. C14/C16 deben soportar fallos, auditoría y costo con privacidad.
No todas se incluyen en una entrega ni se contratan servicios para anticiparlas.

## Implementación propuesta

No implementar C19 ahora. Reentrada: problema medido, dominio dueño aceptado,
proveedor/scopes/costo y modelo aprobados, revisión jurídica y plan de desconexión.
Entonces investigar documentación oficial vigente y preparar sandbox sintético.
Pruebas futuras: firma inválida/replay, 429, doble entrega, timeout con efecto
indeterminado, edición concurrente, miembro retirado, contexto ajeno, token revocado
y exportación caducada. Aceptación exige reconciliación sin duplicados ni permisos
residuales y evidencia de revocación/desconexión, no solo una conexión exitosa.
