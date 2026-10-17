# C17 — Operación interna con permisos limitados

Fecha: 2026-10-16. Estado: **Proposed** para operación adicional. D-041 conserva
aprobación de las capacidades limitadas que describe, sin concesión real automática.

## Lo que entiendo

El producto necesita resolver revisión profesional, reportes y excepciones. Un
operador no debe convertirse en lector universal de relaciones, documentos o
conversaciones. Separar soporte técnico, confianza profesional, controversias y
resolución excepcional de cierre; cada acción requiere contrato propio.

## Decisiones tomadas

D-040 aprueba PC-01..PC-05, incluida administración sin lectura jurídica universal,
salida inmediata y relevo. D-041 permite asignar manualmente a la futura cuenta
confirmada/MFA de Arturo `review_professionals`, sin autoevaluación y solo tras
aprobar procedimiento; permite capacidad separada para resolver cierre excepcional
de despacho, sin contenido jurídico. Invitaciones internas24h/recibo30d/audit90d
ya aprobadas. No volver a solicitar estos parámetros ni asumir permisos concedidos.

## Decisiones pendientes

Procedimiento proporcionado de cotejo/titularidad y suplantación profesional, fuente
y evidencia mínima, corrección/rechazo/recurso y revisor alterno para Arturo.
Definir cola de soporte, motivos, facultades por acción, apelaciones y responsable
de controversias. Prioridad/tiempo de atención y canal privado pendientes; no
prometer respuesta jurídica supervisada mientras D-017 siga Discussing. Retención
de reportes/disputas y evidencia nueva pendiente antes de tablas.

## Diseño propuesto

OperationalReport refiere una capacidad/objeto con categoría cerrada y datos mínimos;
InterventionDecision refiere reporte, actor autorizado, motivo y cambio concreto;
ProfessionalReview conserva su modelo C03 y no se duplica como reporte genérico;
Appeal refiere decisión discutida y revisor permitido. No entidad `case` para
mezclar solicitud, asunto, disputa e incidencia.

Reporte: recibido → clasificado → en atención → resuelto/cerrado; decisión puede
pasar a recurrida → confirmada/revisada. Las transiciones necesitan actor,
precondición, versión y efectos. Recomendación: paneles separados por capacidad,
con proyección mínima; cada ampliación de datos se aprueba antes de implementar.
No impersonación, bypassMFA o descarga de documentos como herramienta de soporte.

Suspender una facultad actúa en la siguiente petición y frontera transaccional.
No borra relación/contenido de terceros, no retrasa salida y no confiere al
operador representación profesional. Resolución excepcional de despacho no puede
transferir automáticamente asuntos o leerlos para decidir un relevo.

## Datos afectados

Clasificación restringida de reportes, motivo, referencia lógica, decisión y
fecha. Propiedad operativa de la cola no significa propiedad del contenido jurídico.
No adjuntos/relatos libres en el primer diseño; si resultan necesarios se diseña
minimización específica. Historia C03 conserva90d aprobados; reporte, recurso o
intervención nuevos no heredan ese plazo sin decidir finalidad y retención.
Retiro/recurso no altera fechas históricas para prolongar conservación.

## Seguridad

Capacidades separadas y asignación manual controlada; no rol superadmin de negocio.
No self-review, autoescalamiento, decisiones por metadata o membresías antiguas.
Negar lectura jurídica al administrador/revisor/resolutor sin autorización propia
por otro vínculo. Revisor alterno y conflicto de interés requieren reglas explícitas.
Ningún contacto a terceros, concesión remota o revisión de cédula real en esta
entrega. **LEGAL REVIEW REQUIRED** sobre acreditación, intervención y recursos.

## Impacto futuro

C17 depende de la capacidad donde interviene; resolver C03 no habilita resolver
pagos C08, reseñas C12 o conflictos C04. Una queja no autoriza abrir el expediente.
El diseño debe admitir separación de funciones futura sin aprobar ahora equipo,
turnos, automatización, contratación o facultades nuevas.

## Implementación propuesta

1. Preparar procedimiento de revisión y matriz acción/dato/actor/estado; obtener
   decisiones pendientes y revisión jurídica antes de habilitar revisión real.
2. A4/A5 implementan por paquetes aprobados; A3 controla migración única y A2
   revisa permisos. A0 integra sin conceder capacidades por este checkpoint.
3. Probar con sintéticos: self-review, otro contexto, MFA ausente, rol suspendido,
   revisión concurrente/cambio de credencial, cierre del último administrador,
   salida sin relevo y recurso de decisión propia. Todos deben impedir acceso o
   decisión indebidos y preservar retiro inmediato.
4. Aceptación: revisión con alcance visible y sin promesa excesiva; decisiones
   motivadas/versionadas, apelación operable y auditoría mínima; cero acceso
   jurídico incidental. C03 completo y operación real siguen pendientes.
