# Definición de la solución Abogalia

Estado: Proposed. Fecha: 2026-10-12.

Esta propuesta se somete a una revisión adicional en [crítica estratégica](20_critical_review.md) y [fricciones del proceso](21_process_friction.md). La combinación marketplace y SaaS necesita demostrar valor comercial. Los estados de aprobación posteriores se detallan a continuación; no todas las recomendaciones funcionales de este documento están aprobadas.

Actualización de la sesión del 2026-10-12: Arturo aprobó atención clara y continua, independientes y despachos pequeños, relación de servicio como centro y búsqueda gratuita con rutas claras. La síntesis actual está en [producto refinado](23_refined_product.md); las reglas funcionales y la secuencia de implementación continúan pendientes.

Abogalia propone conectar el acceso a servicios legales en México con la operación comercial y el seguimiento de abogados y despachos. La solución debe mantener continuidad entre una necesidad, la selección de un profesional, la contratación y la atención posterior. Esta definición está pendiente de aprobación; las decisiones expresadas por Arturo se registran por separado en [el registro de decisiones](decisions/decision-log.md).

## Problema y propuesta central

La hipótesis central es que personas y profesionales pierden información, tiempo y oportunidades al pasar entre búsqueda, contacto, evaluación, cita, contratación y seguimiento. La documentación describe esos problemas, pero aún no aporta entrevistas, disposición a pagar, compromisos comerciales o mediciones del mercado mexicano que permitan cuantificarlos.

La propuesta es **una plataforma para encontrar, contratar y dar seguimiento a servicios legales, conectada con las herramientas que abogados y despachos usan para atender clientes propios y adquiridos en Abogalia**. El hilo conductor es la relación de servicio. Las funciones deben contribuir a crearla, organizarla, sostenerla o hacerla más confiable.

Para la persona, el resultado esperado es saber quién puede atender su situación, qué está contratando, cuánto cuesta y cuál es el siguiente paso. Para el profesional, es recibir solicitudes con contexto suficiente, decidir si puede atenderlas y gestionar atención, cobro y seguimiento sin reconstruir información en cada etapa. Para el despacho, es coordinar esas relaciones entre integrantes y oficinas con permisos claros.

Un flujo ilustrativo de arrendamiento sería: una persona identifica su situación; compara profesionales elegibles; comparte datos mínimos con el elegido; este revisa compatibilidad y conflicto; se acuerda una consulta; posteriormente, si ambas partes desean continuar, el profesional ofrece un servicio con alcance definido y se abre un asunto. Es un ejemplo de comportamiento propuesto, no una conclusión jurídica ni una especificación aprobada.

## Alternativas de producto

| Enfoque | Valor principal | Dependencia económica | Riesgo |
|---|---|---|---|
| Directorio y visibilidad | Encontrar y contactar profesionales | Tráfico y venta de exposición | Poca continuidad y dificultad para medir atención |
| Marketplace de consultas | Reservar y pagar un servicio concreto | Oferta disponible y demanda transaccional | Cobros, cancelaciones y salida después de la consulta |
| SaaS jurídico | Organizar la práctica con clientes propios | Uso recurrente y disposición a pagar | Migración y competencia con herramientas existentes |
| Marketplace conectado al SaaS | Conectar adquisición, contratación y operación | Valor recurrente y captación sostenible | Mayor alcance y complejidad de operación |

Recomiendo la última opción porque coincide con la visión existente y conserva utilidad con clientes propios. Su viabilidad exige demostrar el valor de cada lado: la disponibilidad de profesionales no demuestra demanda pagada, y el tráfico no demuestra retención SaaS. Una lista extensa de capacidades tampoco demuestra diferenciación.

## Valor y recorrido de cada usuario

| Usuario | Capacidad propuesta | Resultado verificable |
|---|---|---|
| Persona que busca abogado | Describir situación, comparar, solicitar atención y conocer condiciones | Obtiene una respuesta útil y puede decidir el siguiente paso |
| Cliente con profesional elegido | Consultas, acuerdos de servicio, documentos compartidos y seguimiento | Conoce pendientes, comunicaciones y estado de su atención |
| Abogado independiente | Perfil, servicios, intake, agenda, seguimiento y clientes | Gestiona solicitudes y atención con menos duplicidad |
| Despacho | Asignación, equipos, oficinas y supervisión | Tiene responsables claros y evita oportunidades sin atender |
| Asistente | Acciones administrativas autorizadas | Coordina citas y seguimiento con acceso limitado |
| Operaciones de Abogalia | Verificación, reportes, moderación y resolución administrativa | Puede atender excepciones con evidencia y trazabilidad |

Dos entradas deben poder converger en la misma operación: clientes adquiridos por el marketplace y clientes que el profesional invita o registra. La procedencia debe distinguirse para medir valor; no autoriza a compartir documentos o clientes entre prácticas ni fija todavía una comisión.

El recorrido propuesto es: solicitud → selección → evaluación → cita o servicio → contratación adicional cuando corresponda → asunto → seguimiento → cierre. No toda solicitud llega a una consulta y no toda consulta llega a un asunto. Una contratación directa o un cliente ya existente no debería requerir una consulta ficticia para usar el sistema; esta flexibilidad necesita aprobación.

## Capacidades del producto completo

| Grupo | Dominios | Papel y dependencias |
|---|---|---|
| Identidad y acceso | Identity, Authentication, Authorization, Users | Identidad, contextos y permisos antes de gestionar información privada |
| Práctica profesional | Lawyers, Law firms, Offices, Memberships, Credentials | Oferta verificable y equipos; depende de identidad y permisos |
| Necesidad y elegibilidad | Legal catalog, Legal requests, Intake, Conflict checking | Recopilación progresiva y evaluación previa; depende de catálogo y profesionales |
| Descubrimiento | Matching, Search, Ranking | Opciones explicables según criterios; depende de oferta, servicios y datos de disponibilidad |
| Atención y cobro | Availability, Booking, Consultations, Payments, Refunds | Coordinar el servicio; depende de aceptación, políticas y proveedores de pago |
| Relación profesional | Leads, CRM, Clients, Legal matters, Documents | Continuidad y operación; depende de permisos, acuerdos y accesos a documentos |
| Confianza y operación | Reviews, Reputation, Moderation, Trust & Safety, Admin, Disputes | Evidencia, reportes y excepciones a lo largo del recorrido |
| Plataforma y negocio | Notifications, Subscriptions, Billing, Audit, Analytics, AI, Integrations | Comunicación, monetización y medición; acompaña las capacidades anteriores |

Identidad, permisos, privacidad, auditoría y métricas atraviesan todo el producto. La IA es una capacidad asistiva y los datos sustentan operación y aprendizaje; no se ha aprobado vender un producto de datos independiente.

La propuesta preserva gestión de asuntos y documentos dentro de la visión completa. Queda por decidir su profundidad: colaboración y seguimiento del servicio, o gestión jurídica interna de expedientes, tareas, plazos y honorarios. Firma, facturación, integraciones e IA avanzada siguen siendo capacidades posibles cuyo problema, costo y prioridad deben acordarse individualmente. No se elige stack, proveedor, arquitectura física o esquema de tablas en este análisis.

## Hallazgos críticos y contradicciones

| Hallazgo | Fuente local | Consecuencia y propuesta |
|---|---|---|
| El recorrido del cliente paga sin mostrar aceptación previa | 06_user_journeys | Un rechazo posterior puede generar devolución; discutir aceptación antes del cobro |
| Marketplace, pagos y reputación preceden a intake, conflictos y consulta en el roadmap | 15_delivery_roadmap | Entregar el recorrido completo requiere reordenar dependencias, pendiente de aprobación |
| Agenda y pagos aparecen separados entre marketplace y SaaS | 05_product_scope, 15_delivery_roadmap | Diseñar una capacidad compartida para ambos orígenes; evitar sistemas duplicados |
| El alcance cubre consultas y asuntos, pero los recorridos detallan principalmente la consulta | 05_product_scope, 06_user_journeys | Definir oferta, aceptación del servicio y seguimiento posterior |
| La métrica principal mide consultas, pero la plataforma debe ser útil con clientes propios | 01_product_vision, 16_product_metrics | Medir por separado marketplace y uso recurrente SaaS |
| Hay segmentos de despachos de 1–5 y 2–20 abogados sin distinguir etapas comerciales | 02_market_strategy, 03_users_and_personas | Confirmar audiencia prioritaria sin convertir recomendaciones previas en decisiones |
| Morelia como piloto está en los documentos, pero Arturo pide diseñar el proyecto completo | 02_market_strategy y conversación | Cobertura nacional y estrategia de lanzamiento deben decidirse aparte; Morelia no queda ratificada |
| Se exige revisión humana de IA de alto riesgo con soporte limitado | 13_ai_strategy y conversación | Definir responsables y flujos disponibles; no prometer revisión que no existe |
| Verificación se presenta junto a confianza y calidad | 08_marketplace_strategy, 09_operating_model | Diferenciar identidad, cédula y evidencia de experiencia; verificar credenciales no garantiza calidad |

La expresión de la propuesta de valor que dice que Google no permite reserva o disponibilidad es demasiado absoluta. La propia oferta de Doctoralia incluye Reserva con Google. Debemos comparar el recorrido, la elegibilidad jurídica y la continuidad del servicio, no atribuir exclusividad a funciones aisladas. [Oferta oficial de Doctoralia](https://pro.doctoralia.com.mx/precios/medicos-y-especialistas).

## Contratación y momento del cobro

Recomiendo distinguir tres servicios conceptuales: evaluación comercial breve, consulta profesional y servicio legal posterior. La primera podría ser gratuita y opcional; la segunda debe explicar alcance, duración, precio y qué recibirá el cliente; el tercero necesita acuerdo específico. Esta separación es una propuesta y su encuadre requiere **LEGAL REVIEW REQUIRED** en México.

Para una primera consulta, la recomendación pendiente es: preclasificación → selección → datos mínimos para revisión → aceptación profesional → pago → confirmación → información ampliada. La espera exige plazos, vencimientos y opciones cuando el profesional no responde. No se fijan aún duraciones ni reglas de cancelación. Los clientes ya evaluados podrían tener una ruta más directa si se aprueban sus condiciones.

Clio recomienda revisión de conflicto antes de programar consultas. Su referencia se vincula a reglas estadounidenses; sirve como antecedente operativo y no determina obligaciones mexicanas. [Referencia de Clio](https://www.clio.com/blog/conflict-check-how-to/).

Una preautorización puede reducir pasos, pero retiene fondos y tiene vencimiento; no equivale a cobro ni a custodia indefinida. La viabilidad depende del proveedor y método elegidos. [Documentación de Stripe](https://docs.stripe.com/payments/place-a-hold-on-a-payment-method).

## Modelo de negocio y aprendizaje de Doctoralia

Doctoralia México publica Starter a $1,740, Plus a $2,340 y VIP a $2,970 MXN por mes más IVA, facturados anualmente, consultados el 12 de octubre de 2026. Ofrece complementos y visibilidad comercial. Su oferta permite observar monetización por herramientas y exposición; los precios no demuestran disposición a pagar de abogados ni revelan el margen de Doctoralia México. [Precios oficiales](https://pro.doctoralia.com.mx/precios/medicos-y-especialistas).

Doctoralia Pagos aplica una comisión por transacción más IVA que varía por plan y se informa en contrato. Su ayuda contempla prepago y, para ciertos perfiles con dLocal, tarjeta guardada con cargo posterior. No permite concluir que toda consulta captada tenga una comisión. [Ayuda oficial de pagos](https://help.docplanner.com/9/doc/preguntas-frecuentes-pagos-dp).

El tipo de suscripción participa en el ranking de Doctoralia. Para Abogalia recomiendo que las promociones estén identificadas y no alteren compatibilidad orgánica; la política comercial sigue pendiente. [Descripción oficial del ranking](https://pro.doctoralia.com.mx/hubfs/2023%20PDFs%20for%20the%20footer/ES_search_ranking_25.04.2023.pdf).

Mi hipótesis económica preferida es una suscripción por operación profesional con valor verificable, más servicios adicionales cuyo costo crece con uso. Una comisión de adquisición solo tiene sentido si el origen aporta valor demostrable, se puede atribuir y supera sus costos. No está aprobada ni fijada. Tampoco está decidido cobrar posicionamiento.

Debe modelarse la contribución de cada fuente de ingreso después de pagos, mensajes, IA, almacenamiento, verificación, soporte y adquisición. Importes pagados por servicios del abogado deben distinguirse de ingresos propios de la plataforma; tratamiento contable, fiscal y contractual: **LEGAL REVIEW REQUIRED**. No corresponde estimar rentabilidad sin volumen, precios, retención y costos.

## Datos y separación de prácticas

Arturo aprobó que un abogado opere como independiente y pertenezca a un despacho. Eso no aprueba compartir automáticamente información entre contextos. Proponemos identidad profesional común y operación distinguible por práctica; ownership, permisos, facturación y salida de un despacho se diseñarán en su sesión.

Una relación comercial en un contexto no concede acceso a un expediente de otro. La disponibilidad debe coordinarse para evitar doble reserva sin revelar los detalles de las citas. Una revisión de conflictos tampoco debe transformarse en un buscador global de clientes de otros despachos. El alcance de búsqueda y las alertas compatibles con confidencialidad necesitan diseño y revisión jurídica.

Solicitud, intake, match, reserva, consulta, lead, cliente y asunto deben conservar significados separados. Una persona puede aparecer en relaciones de servicio de distintas prácticas, sin que exista por ello una ficha privada universal visible a todos. El acceso del cliente a documentos compartidos y las notas internas del profesional deben distinguirse.

Los eventos de producto deben registrar lo necesario para medir el recorrido sin incorporar narrativas, identificaciones o documentos sensibles por defecto. Las transiciones de negocio y acciones de auditoría deben distinguirse de vistas y clics. IA, retención, consentimiento y accesos quedan pendientes de políticas explícitas.

## Confianza con autoservicio

Autoservicio con soporte limitado es una decisión aprobada sobre el modelo operativo, no aprobación de verificaciones automáticas, decisiones jurídicas automáticas o ausencia de administración. Debe determinarse qué casos son automáticos, cuáles requieren al profesional y cuáles requieren a Abogalia.

La comprobación de conflictos se propone bajo control del profesional; Abogalia facilita información y evidencia. Operaciones necesita capacidad para revisar identidad dudosa, reportes, accesos indebidos, pagos y disputas administrativas. La plataforma no debería prometer valoración de mérito jurídico, respuesta de emergencia o resolución profesional que no pueda prestar. El tratamiento de estos casos requiere **LEGAL REVIEW REQUIRED** y responsables definidos.

Reseñas y reputación deben reflejar la experiencia del servicio, no convertirse en una garantía de resultados judiciales. Debe acordarse quién puede reseñar y cómo se trata una consulta gratuita, un cliente propio, una disputa o una información sensible antes de definir reseñas como exclusivamente transaccionales.

## Criterios para evaluar la solución

Estos criterios son propuestas de producto; sus umbrales y fuentes de medición requieren aprobación.

- Acceso: proporción de solicitudes que obtiene opciones elegibles y una respuesta en el plazo prometido, segmentada por jurisdicción y servicio.
- Atención: consultas o servicios realizados, cancelaciones, desacuerdos y claridad del siguiente paso.
- SaaS: prácticas que gestionan relaciones activas de forma recurrente, incluyendo clientes propios, y tiempo administrativo medido frente a su situación previa.
- Continuidad: solicitudes con responsable, seguimientos realizados y acuerdos de servicio que llegan a un asunto cuando corresponde.
- Economía: contribución por práctica y canal, retención de suscripción y costo de adquisición; distinguir volumen de pagos de ingresos.
- Confianza: comprobaciones trazables, tiempos de resolución y controles efectivos de acceso; un incidente de acceso indebido requiere investigación aunque otras métricas mejoren.

Las hipótesis comerciales deben contrastarse con entrevistas sobre herramientas y gastos actuales, observación de flujos reales y decisiones de compra. La validación es parte del desarrollo del proyecto completo; no supone producir un prototipo desechable. Los resultados adversos deben poder cambiar posicionamiento y prioridades antes de consolidarlos en arquitectura.

## Decisiones que deben cerrar la definición

Las cinco preguntas ya presentadas siguen abiertas y se consolidan en [preguntas de producto](product/open-questions.md): valor principal de la suscripción; evaluación comercial y consulta pagada; posicionamiento comercial; evidencia y acceso a usuarios; recursos de construcción, operación y adquisición.

También debe concretarse la profundidad de gestión de asuntos, el límite de responsabilidad de la plataforma y la cobertura comercial. Ninguna recomendación de este documento sustituye aprobación de diseño. Las decisiones de stack, multi-tenancy, tablas, eventos, proveedores y políticas sensibles requieren sus propios checkpoints. La documentación original se conserva y cualquier revisión sustantiva deberá aprobarse explícitamente.
