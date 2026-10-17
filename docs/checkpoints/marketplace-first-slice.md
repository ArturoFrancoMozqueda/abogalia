# Checkpoint — Primer recorrido marketplace de Legalia

Fecha2026-10-16. Actualizado2026-10-17. **Directorio y flujo Approved por Arturo;
retención jurídica y habilitación real pendientes.**
Referencia común `7b88b4e`; A0 integra, tres agentes preparan contratos y revisión.

## Lo que entiendo

Arturo eligió catálogo → búsqueda → solicitud a un profesional como siguiente
recorrido. El visitante descubre perfiles públicos; para enviar una solicitud
entra con su cuenta y confirma exactamente a quién comparte información.
No se crea relación contratada, reserva o pago al enviar.

Fuentes: [plan](../27_development_plan_agents.md),
[decisiones](../decisions/decision-log.md), [C03](professional-contexts.md),
[C06](c06-discovery-catalog.md) y [C04](c04-requests-conflicts.md).
Este complemento concreta el corte; conserva los checkpoints generales para fases
posteriores y no transforma toda la visión marketplace en alcance aprobado.

## Decisiones tomadas

- Prioridad elegida expresamente por Arturo, sin volver a votarla.
- Búsqueda gratuita, publicación profesional voluntaria y separada de revisión.
- Nombre de presentación, ámbito declarado y etiqueta precisa de lo comprobado
  son la base pública C03; número completo de cédula sigue privado.
- Sesión activa, MFA profesional, autorización por objeto/contexto y permisos
  mínimos siguen vigentes; administrar despacho no permite leer solicitudes.
- Hosting, presupuesto Free, responsables y capacidades D-040/041 no se reabren.

## Decisiones pendientes

Arturo aprobó expresamente los paquetes1 y2 el2026-10-17. El paquete3 no está
aprobado; la aprobación del flujo no fija su retención ni autoriza sus tablas.

1. **Directorio inicial:** campos públicos C03, búsqueda por nombre/ámbito declarado,
   orden alfabético estable y consulta máxima80 caracteres; sin patrocinio ni
   inferencia de especialidad/ubicación. La etiqueta pública de contexto permite
   distinguir a quién se envía sin exponer el identificador privado.
   Jurisdicción/modalidad como filtros requieren atributos y vocabulario aprobados.
2. **Solicitud dirigida:** un profesional en un contexto visible, datos mínimos
   progresivos: relato1..2000 caracteres, sin borrador persistido; solicitante
   confirmado con sesión C02, MFA para el profesional. Respuesta inicial
   estandarizada para continuar evaluación o no poder atender, con retirada del
   solicitante. Sin bandeja colectiva ni reenvío automático. Los parámetros
   técnicos propuestos del contrato (paginación20/máximo50, JSON8192 bytes,
   versiones/idempotencia) forman parte de este paquete para revisión.
3. **Política de datos C04:** plazo y evento inicial por contenido, versiones, recibos
   e historia, excepciones justificadas y tratamiento en backups/restore. No heredar
   30/90 de Identity. Antes de tablas, modelo y matriz necesitan aprobación.

El procedimiento de revisión/antisuplantación pendiente de C03 debe concretarse
para habilitar profesionales reales; no equivale a pedir de nuevo quién revisa.
**LEGAL REVIEW REQUIRED** para el tratamiento jurídico correspondiente.

## Diseño propuesto

El [flujo UX](../ux/marketplace-first-flow.md) concreta pantallas y campos.
El [contrato API](../contracts/marketplace-first-api.md) delimita proyección pública,
comandos privados, versiones y errores. La [matriz de preparación](../operations/marketplace-first-readiness.md)
identifica código existente, dependencias y tareas locales ya autorizadas C03.
Los parámetros del directorio y del flujo aprobados rigen la implementación local;
los documentos no acreditan endpoints desplegados o persistencia jurídica autorizada.

Secuencia: completar habilitación/publicación C03 con negativos; entregar catálogo
y búsqueda sobre proyección vigente; añadir solicitud C04 tras aprobar su modelo,
matriz y retención. Un catálogo sin profesionales muestra vacío honesto. No se
publican fixtures ni se convierte la ausencia de datos en prueba de marketplace listo.
C05 dará continuidad después; C07/C08 requieren sus propios paquetes.

## Datos afectados

| Familia | Propiedad/acceso | Política |
|---|---|---|
| Proyección pública | Profesional/contexto elegible, campos voluntarios permitidos | Origen C03; retirada efectiva, sin copia permanente en build/índice |
| Búsqueda | Visitante, criterios públicos acotados | No persistir historial de búsquedas en aplicación, propuesto; no equivale a garantizar ausencia en proveedor/navegador |
| Solicitud y entregas | Solicitante y destinatario explícito vigente | Contenido confidencial, historia y estados C04; plazos pendientes |
| Recibos/transiciones | Acceso restringido por finalidad | Sin duplicar relato; plazo propio pendiente, no retención indefinida |

No copiar datos jurídicos a C06, URLs, métricas o logs. No tabla genérica case,
contactos importados, documentos de identidad ni IA.

## Seguridad

Proyección construida con allowlist en servidor. Revalidar elegibilidad C03 al
listar, abrir ficha y enviar; retirada durante una petición debe impedir divulgación
o commit posterior. No devolver datos privados y ocultarlos después en React.
C04 exige sujeto de sesión, destinatario/contexto exactos, control por objeto,
CSRF, versiones e idempotencia. MFA profesional no concede lectura universal.
Mantener API no-store; caché pública de perfiles requiere diseño de invalidación
antes de activarse. Observabilidad permanece sin captura por este paquete.

## Impacto futuro

La solicitud puede conducir a acuerdo C05, sin crearlo automáticamente. Ofertas
transaccionables, jurisdicciones ampliadas, agenda, pagos, reseñas y matching
personalizado requieren decisiones posteriores. El orden inicial no promete calidad
jurídica ni garantiza que un profesional acepte.

## Implementación propuesta

1. Integrar contratos y revisión independiente de esta tanda documental.
2. Continuar C03 local en el alcance ya aprobado, mediante órdenes con archivos
   exclusivos y criterios de la matriz; mantener gates de operación real.
3. Resolver la política C04/modelo/matriz antes de su persistencia. Directorio y
   flujo ya aprobados; no volver a preguntarlos.
4. Un único responsable de migraciones; API/web en archivos separados y revisión
   independiente. Probar aislamiento, autoaprobación, retirada concurrente,
   repetición de envío, cambios de versión, errores y restauración.
5. Aceptación real exige C02/C03 y recorrido integrado con datos autorizados.
   Esta entrega es diseño; no crea perfiles públicos ni solicitudes reales.

## Evidencia de esta tanda

Tres agentes entregaron flujo UX, contrato API y auditoría de preparación, con
revisión cruzada. A0 alineó búsqueda80, descripción2000, contexto público explícito
y respuesta estandarizada `can_continue_evaluation` / `cannot_assist`. No se
implementaron endpoints, tablas o pantallas nuevas. A0 comprobó enlaces locales de10 archivos Markdown, las ocho secciones de este
checkpoint y diff sin errores. Escáner8.30.1:242 archivos e historial, cero hallazgos.
No se ejecutaron pruebas de software en esta tanda documental.
