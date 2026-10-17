# Checkpoint — Resumen de solicitud y borrador de mensaje

Fecha: 2026-10-12. Alcance: Approved en D-019. Flujos funcionales: Approved en D-020. React + FastAPI: Approved en D-025. Servicios, proveedor de IA, permisos, presupuesto, límites, retención y tratamiento de datos: pendientes. Implementación: pendiente; el repositorio aún no contiene una aplicación.

## Lo que entiendo

Arturo quiere implementar únicamente las dos funciones de menor complejidad discutidas: resumir una solicitud a petición del usuario y preparar un mensaje con información seleccionada por el abogado. El objetivo es reducir trabajo de redacción y reconstrucción con consumo acotado. La aprobación no extiende IA a búsquedas sobre expedientes, documentos, canales externos ni decisiones jurídicas.

## Decisiones tomadas

- Dos funciones de IA, D-019.
- Procesamiento documental con IA aplazado, D-022; no afecta la aprobación de estas dos funciones de texto.
- Flujos de resumen revisable y borrador editable con copia manual, D-020; revisión humana y generación a petición, sin envío automático.
- Atención clara y continua, D-011; independientes y despachos pequeños, D-014.
- Relación de servicio como centro, D-015; práctica propia más un despacho, D-003.
- Autoservicio con soporte limitado, D-004; checkpoints antes de implementar capacidades, D-005.

## Decisiones pendientes

| Decisión | Propuesta para revisión | Por qué importa |
|---|---|---|
| Tratamiento de la información seleccionada | Mantener texto visible y seleccionado explícitamente; definir consentimiento y procesamiento por proveedor antes de usar datos reales | La selección de entrada está aprobada; el tratamiento por terceros requiere decisión |
| Persistencia | Guardar texto final aceptado en su contexto; no conservar todos los intentos por defecto | Afecta privacidad, recuperación e historial; plazo de conservación pendiente |
| Consumo | Límite de entrada y salida, cuota y tope global aplicados por el servidor | Evita procesamiento excesivo; cantidades y presupuesto pendientes |
| Servicios e integración | Usar React + FastAPI aprobados; acordar identidad, permisos y proveedor antes de programar IA | No existe aún aplicación; la elección de stack no aprueba servicios ni tratamiento |

Tratamiento por proveedor, consentimientos y retención: **LEGAL REVIEW REQUIRED**. No se aprueba gasto ni transmisión de información por registrar este checkpoint.

## Flujos funcionales aprobados

### AI-01 — Resumen de solicitud

El usuario escribe su solicitud y pulsa «Preparar resumen». Antes de generar, puede ver qué texto se utilizará y la información necesaria sobre tratamiento. La salida es una síntesis editable de lo que relató, manteniendo la atribución de hechos no comprobados. El original permanece como fuente; aceptar un resumen no envía la solicitud a profesionales.

Puede corregir, aceptar o descartar. Si cambia el relato, la interfaz indica que el resumen anterior necesita revisión. No se generan resúmenes continuamente al escribir. Un fallo permite continuar con la descripción original y ofrece reintento manual.

### AI-02 — Borrador de mensaje

El abogado elige el contexto profesional y el destinatario, selecciona el texto autorizado y describe brevemente qué desea comunicar. Ve la información seleccionada antes de generar. Obtiene un borrador editable; puede corregirlo, descartarlo o copiar la versión revisada.

El borrador conserva el carácter incierto de datos o decisiones pendientes. No agrega hechos, honorarios, fechas ni compromisos ausentes. No se envía automáticamente ni cambia el estado de la relación. En esta capacidad la acción final propuesta es copiar: cualquier entrega dentro de Abogalia o por canales externos pertenece al diseño de comunicación correspondiente.

## Datos afectados

Conceptualmente: solicitud y relato fuente, contexto profesional, relación de servicio, destinatario y texto final aceptado. No se crean tablas ni se aprueba un modelo de datos aquí.

La fuente de los hechos continúa siendo la información proporcionada y los registros confirmados, no la salida del modelo. Un resumen no certifica hechos; un borrador no acredita entrega. El registro operativo propuesto conserva actor, contexto, función, estado, versión, duración y consumo; no vuelca relatos o borradores en logs o analítica general.

Estados propuestos de la generación: pendiente, generando, listo, fallido y descartado; aceptación separada de entrega. Cambiar entrada durante una generación debe invalidar o identificar claramente un resultado basado en texto anterior.

## Seguridad

- Autorizar cada operación en servidor, con el contexto independiente/despacho y la relación correspondiente; seleccionar datos no concede acceso.
- Claves del proveedor únicamente en servidor; aplicar límites también en servidor.
- Tratar texto de usuarios como contenido no confiable: no ejecutar instrucciones incluidas en relatos, conceder permisos, acceder a otros datos ni activar herramientas.
- Validar salida y formato; mostrar revisión humana; evitar acciones derivadas automáticamente.
- Definir tratamiento y retención del proveedor antes de habilitar datos reales. Los valores concretos siguen pendientes.
- Mantener una alternativa manual ante errores o agotamiento de cuota.

## Impacto futuro

Estas funciones dependen de solicitudes, identidad, permisos y relación de servicio. Comparten gestión de generación y costos; sus reglas de contenido son distintas. No necesitan inicialmente búsqueda vectorial, conexión a WhatsApp, lectura de expedientes, creación automática de tareas o investigación jurídica. Incorporar otra función de IA requiere nueva decisión de alcance y checkpoint.

## Implementación propuesta

Epic: asistencia de redacción. Dos capacidades completas:

| Capacidad | Valor para usuario y negocio | Dependencias | Criterios de aceptación |
|---|---|---|---|
| AI-01 | Descripción comprensible y menos reconstrucción en admisión | Solicitudes, identidad, permisos, tratamiento de datos y consumo | Generación manual; original preservado; resumen editable y atribuible al relato; no añadir hechos; descarte, cambio de entrada, error y cuota resueltos |
| AI-02 | Menos redacción repetitiva con control del profesional | Contexto profesional, permisos, destinatario y consumo | Solo datos seleccionados y autorizados; borrador editable; copia revisada; sin envío, cambios de estado ni compromisos inventados |

Trabajo técnico posterior a aprobación: interfaz y API según stack acordado, reglas de autorización y límites, persistencia aprobada, medición sin contenido sensible, manejo de errores y verificaciones de los dos recorridos.

Métricas propuestas: uso por función, aceptación y descarte, correcciones, tiempo total incluyendo revisión, errores, latencia y costo por resultado aceptado. No se usan resúmenes generados como prueba de ahorro.

Verificaciones necesarias cuando exista código: fidelidad a hechos y atribuciones, resistencia a instrucciones incluidas en el texto, aislamiento entre prácticas y asuntos, edición de entrada durante generación, fallos del proveedor, reintentos, concurrencia y cuotas. No afirmar calidad por un ejemplo exitoso.

Los flujos funcionales están aprobados. Arquitectura, proveedor y presupuesto se decidirán por separado. Ninguna función se marcará Implemented hasta que el recorrido completo y sus controles estén verificados.

La preparación de arquitectura incorpora la [experiencia de Kova y el orden de servicios](../25_kova_lessons_and_setup_order.md), por instrucción de Arturo. La generación de texto se propone a petición, sin trasladar la infraestructura de ingesta documental de Kova. Identidad, permisos, proveedor y límites necesitan sus decisiones antes de implementación.

La suite será propia de Abogalia, D-023. La [comparación de servicios y tiers](../26_services_and_tiers.md) usa tarifas oficiales consultadas el 2026-10-12; no supone recursos compartidos, elección de proveedor ni aprobación de gasto.
