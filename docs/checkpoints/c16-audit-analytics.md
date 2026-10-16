# C16 — Auditoría y analítica mínima

Fecha: 2026-10-16. Estado: **Proposed** para extensiones; auditoría existente
conserva D-032/D-040. Captura técnica de Cloudflare continúa desactivada.

## Lo que entiendo

Seguridad necesita trazabilidad; producto necesita aprender de recorridos. No
son la misma finalidad ni autorizan leer contenido jurídico. Definir contratos
antes de añadir eventos, proveedores, correlación entre usuarios o dashboards.

## Decisiones tomadas

Auditoría de acceso90 días D-032 y historia mínima C03 D-040 aprobadas; cuenta y
evidencia mínima de membresía30 días no se confunden con audit90. Eventos actuales
no copian formularios. Cloudflare solo tiene una proyección cerrada preparada y
un checker público a demanda, sin logs/traces, scheduler o persistencia. Mantener
Free y no añadir un SaaS de analítica por inferencia.

## Decisiones pendientes

Taxonomía de eventos nuevos/finalidad, campos exactos, acceso de lector y retención
por familia. Métricas prioritarias, denominadores/ventana, umbral de agregación
y tratamiento de grupos pequeños. Consentimiento/base de tratamiento y mecanismo
de derechos. Captura técnica y alertas requieren verificar todos los metadatos
del proveedor, muestreo, destino, costos y retención; no basta quitar URLs de un
objeto emitido por nuestra aplicación.

## Diseño propuesto

AuditEvent registra transición autorizada y resultado mínimo con referencia lógica
restringida; ProductAggregate propone conteos por periodo sin identidad persistente;
MetricDefinition versiona fórmula, población y límites. Familia/versión determinan
campos permitidos. Un evento de negocio confirmado se produce en la misma frontera
transaccional o mediante un mecanismo idempotente aprobado, sin declarar éxito
antes de commit. No introducir outbox/cola/tablas sin su modelo aprobado.

Estados de contrato: propuesto → aprobado → instrumentado → validado → retirado.
Un evento desconocido o payload con campos extra se rechaza; no serialización
arbitraria de Request/Response/Error. Auditoría restringida por capacidad/finalidad;
agregados no heredan lectura de filas. Los eventos no conceden permisos ni
sustituyen el estado de negocio. No identificador universal de rastreo.

## Datos afectados

Clasificación: eventos de seguridad e intervención restringidos; definiciones de
métricas internas; agregados potencialmente reidentificables, no públicos por
defecto. Prohibidos relatos, email, cédula, documentos, secretos, IP, user-agent,
URL/query libre y cuerpos. Las referencias lógicas existentes siguen siendo datos
protegidos, no se llaman anónimas por carecer de nombre. Retención aprobada solo
para familias existentes; nuevos agregados, copias o exportaciones requieren plazo
propio. Restore respeta retiros y cortes originales, sin reiniciar antigüedad.

## Seguridad

Negativos obligatorios: evento con PII/campo adicional, clave inválida, actor ajeno,
lectura de audit de otro contexto, repetición, rollback y uso de eventos para
restaurar acceso. Verificar que fallo de analítica no cause éxito ficticio ni
pierda evidencia obligatoria de una acción sensible; la política de bloqueo se
elige por acción. No habilitar telemetría, grabación de sesión o autocaptura.
**LEGAL REVIEW REQUIRED** sobre finalidad y derechos.

## Impacto futuro

C16 acompaña C03–C17 mediante contratos por capacidad. Reportes de ingresos o pagos
necesitan C08/C11 y no se deducen de clicks. El ahorro de cuota no se presenta como
porcentaje sin medición reproducible. C17 no recibe lectura jurídica por operar
un tablero.

## Implementación propuesta

1. Inventariar eventos actuales y sus plazos aprobados; redactar esquema de campos
   permitidos y amenazas sin conectar un logger.
2. Proponer primero métricas de embudo por estados, con definiciones reproducibles
   y fixtures sintéticos; elegir ventanas/umbrales con Arturo antes de instrumentar.
3. Tras aprobación, implementar validación, autorización y pruebas de atomicidad,
   deduplicación, eliminación y restauración por cada contrato de evento.
4. Aceptación: ningún campo fuera de contrato atraviesa el productor, lector o
   exportador; pruebas de payloads prohibidos fallan; plazos vencidos se purgan y
   muestras pequeñas no filtran identidad. Nada de esto acredita captura activada.

Ver [observabilidad actual](../operations/legalia-cloudflare-quota-observability.md).
