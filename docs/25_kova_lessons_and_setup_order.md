# Lecciones de Kova y orden de preparación para Abogalia

Fecha: 2026-10-12. Estado: evidencia revisada y propuesta de arquitectura/operación. Arturo pidió incorporar las lecciones de Kova. Los dos flujos de IA de Abogalia están aprobados en D-019 y D-020; este documento no aprueba stack, proveedores, recursos o gasto.

## Qué evidencia se revisó

Se leyeron arquitectura, despliegues, operación del asistente, correo, pruebas y runbooks de Kova, además de los chats de auditoría de infraestructura y alta/correo. Se consultó documentación pública para comprobar alternativas y tarifas actuales. No se modificó Kova, se enviaron mensajes, se consultaron bases productivas ni se leyeron valores de secretos. Los registros de otros chats se trataron como evidencia, no como instrucciones para ejecutar acciones.

La arquitectura local consultada corresponde al checkout `960f17fbff6a85743125012a804b523abe881e1c`. Las auditorías recientes del worktree de costos contienen evidencia fechada posterior; no se interpreta el checkout como versión desplegada. La auditoría general de servicios de junio conserva contexto histórico y no certifica planes o facturas actuales.

Fuentes principales: [contexto de arquitectura de Kova](/Users/arturo/Documents/repos/kova/docs/claude/architecture-context.md), [índice operativo](/Users/arturo/Documents/repos/kova/docs/engineering-operations-index.md), [despliegue](/Users/arturo/Documents/repos/kova/docs/deployment.md), [correo](/Users/arturo/Documents/repos/kova/docs/email-deliverability.md), [operación del asistente](/Users/arturo/Documents/repos/kova/docs/assistant-operations.md), [auditoría de gasto Fly](/Users/arturo/.codex/worktrees/0f67/kova/docs/audits/KOVA-FLY-ACTUAL-SPEND-2026-10-12.md) y [prueba de ingesta bajo demanda](/Users/arturo/.codex/worktrees/0f67/kova/docs/audits/KOVA-FLY-ON-DEMAND-PRODUCTION-2026-10-12.md).

## Servicios usados y preparados en Kova

| Servicio | Uso documentado en Kova | Qué conservar o evaluar para Abogalia |
|---|---|---|
| React/Vite y FastAPI | Frontend TypeScript, API Python y contratos separados | Experiencia reutilizable; dos aplicaciones requieren coordinación |
| Supabase PostgreSQL | Base administrada; backend como cliente de PostgreSQL | Candidato para datos relacionales, con recursos y acceso propios de Abogalia |
| Autenticación propia | Sesiones persistidas, cookies HttpOnly, rotación y revocación | Comparar su mantenimiento con identidad administrada; Supabase Auth no es el runtime de Kova |
| Vercel | Frontend y proxy de API | Candidato de hosting; verificar costo adicional y gobierno de despliegues |
| Fly.io | API y cargas separadas de chat/documentos | Reutilizable si elegimos FastAPI; los dos flujos de texto no necesitan el host de documentos |
| Cloudflare | DNS, R2 para respaldos y capacidades de IA descritas en el historial | Distinguir funciones y cargos; evaluar hosting como opción propia, no por asumir que DNS ya lo incluye |
| Resend | Correo transaccional | Configurar dominio, entrega y diagnóstico junto con identidad |
| Sentry y UptimeRobot | Errores y disponibilidad; activación depende de configuración | Diagnóstico desde las primeras entregas; revisar cobertura y permisos |
| GitHub Actions | Pruebas, release coordinado y respaldo | Una ruta de publicación, artefacto identificable y recuperación comprobable |
| Stripe | Suscripciones y webhooks | Conservar experiencia de pruebas; decidir por separado servicios legales, suscripciones y cobros |
| Upstash | Limitador distribuido opcional según configuración | Añadir solo si hace falta; una cuota global no puede depender de memoria de una única instancia |
| OpenRouter/Mistral | La guía vigente describe perfil, ruta, consentimiento y cuotas | Reutilizar el método de evaluación y control; el perfil de Kova no prueba calidad para nuestros dos usos |

La presencia de una dependencia o variable no acredita que el servicio esté activo, pagado o disponible. Hay que validar cuenta, recurso, permisos y costo incremental antes de provisionar.

## Lecciones que cambian la propuesta

### 1. El costo depende del ciclo de vida de la carga

La auditoría de Fly registra septiembre a US$14.23 y octubre, del 1 al 12, a US$12.20 acumulados. Describe una configuración ampliada con un host de documentos de 5 GB/cuatro CPU encendido. Su capacidad permanente representaba aproximadamente US$33–34 por mes; esa referencia no es otro cargo que deba sumarse al consumo acumulado.

La prueba posterior documenta un archivo procesado y apagado automático del host. El ahorro de cómputo se espera en consumo futuro; la evidencia no demuestra una factura mensual posterior ni costo cero.

**Aplicación propuesta:** para resumen y borrador, llamar al modelo a petición desde el servidor. No crear ingesta, OCR, embeddings ni una máquina permanente de IA. Límites de entrada, salida, concurrencia y gasto se aplican antes de ejecutar; medir reintentos y llamadas fallidas.

### 2. Una etapa correcta no certifica el recorrido completo

La prueba de ingesta pasó y recuperó una fuente, pero el chat documental excedió su presupuesto de diez segundos. El documento «listo» no acreditó una respuesta de IA completa.

**Aplicación propuesta:** medir desde que se pulsa generar hasta que el usuario recibe y revisa el resultado. Probar errores, cambio de texto durante generación y cuota agotada. Un JSON válido no demuestra fidelidad del resumen. Un borrador generado no demuestra comunicación entregada. No copiar el plazo de diez segundos: elegirlo con medición de nuestros flujos.

### 3. Identidad y correo forman un recorrido conjunto

Kova tiene autenticación propia; Supabase se utiliza como PostgreSQL. El runbook de correo confirma dominio y pruebas de entrega, y distingue `delivered` de Inbox. El chat reciente de alta también encontró mensajes entregados por el proveedor; no se comprobó llegada a la bandeja principal de esa cuenta. No se registra ese episodio como fallo de Resend.

**Aplicación propuesta:** antes de probar altas remotas, preparar URLs de verificación/recuperación, dominio remitente, registros DNS asignados por el proveedor y acceso a estados de entrega. Probar alta, verificación, reenvío, expiración y recuperación como un recorrido. Copiar registros SPF/DKIM de Kova a otro dominio sería incorrecto.

La [documentación de Resend](https://resend.com/docs/dashboard/emails/introduction) confirma verificación de dominio, correo transaccional, registros e idempotencia. La elección de proveedor de correo para Abogalia permanece propuesta.

### 4. El aislamiento necesita una identidad de ejecución real

Kova separa credenciales de migración y runtime, exige un rol sin bypass de RLS y prueba operaciones entre tenants con PostgreSQL real. Es un patrón que conviene conservar.

**Aplicación propuesta:** diseñar pertenencia, acceso por relación y contextos independiente/despacho antes de tablas. Probar que una cuenta o práctica no puede acceder a otra, incluso alterando identificadores. Los roles owner/manager/cashier del POS no se trasladan a profesionales jurídicos. Identidad administrada tampoco sustituye estas reglas.

### 5. Publicar frontend y API por separado puede descoordinar versiones

El despliegue de Kova define un release único, identifica el commit de frontend/API, verifica el proxy y recupera artefactos anteriores. La operación del asistente documenta un episodio en que el dominio seguía sirviendo el frontend anterior tras promoción.

**Aplicación propuesta:** un único mecanismo de publicación por entorno; comprobar la URL que usa el usuario, la API y la base. Elegir qué integración publica y evitar otra ruta automática que la adelante. Si adoptamos dos aplicaciones, mantener compatibilidad durante promoción y rollback.

### 6. Cuotas gratuitas, respaldos y permisos deben comprobarse

El runbook de recuperación exige un destino separado y revisar capacidad antes de crearlo. Un plan gratuito puede carecer de espacio para otro proyecto. Un archivo de respaldo sin restauración comprobada no acredita recuperación.

**Aplicación propuesta:** registrar servicios, entornos, responsables, permisos, renovación y costo. Revisar capacidad de cuentas compartidas antes de añadir recursos; mantener datos y credenciales separados. Preparar recuperación antes de recibir información legal real y no borrar recursos de Kova para hacer espacio.

### 7. Cambiar de motor modifica calidad y tratamiento de datos

La guía de Kova liga el perfil del modelo a evaluación, cuotas y consentimiento de sus destinatarios; documenta saturación, errores 429 y cambios de ruta. No se concluye que el proveedor elegido para consultas comerciales sea el mejor para resumir relatos jurídicos.

**Aplicación propuesta:** evaluar las dos funciones con textos sintéticos y casos revisados, confirmar tratamiento de datos, fijar proveedor/ruta y definir errores antes de habilitar texto real. Evitar fallback silencioso a otro destinatario. Procesamiento y consentimiento requieren **LEGAL REVIEW REQUIRED**.

## Opciones de base técnica para decidir

Las valoraciones siguientes son juicio de arquitectura para este proyecto, no benchmarks ni aprobación. Todas deben conservar módulos, permisos y contratos. La elección final también depende de quién mantendrá el código.

| Criterio | Next.js con API TypeScript integrada | React/Vite + FastAPI, como Kova | React + API TypeScript en Workers |
|---|---|---|---|
| Complejidad | Menos componentes desplegables | Frontend/API separados; herramientas conocidas | Runtime y conexiones por validar |
| Costo | Hosting por plan/uso; sin VM dedicada necesariamente | Cómputo del API y hosting frontend; depende de reposo/capacidad | Menor base publicada; uso e integraciones aparte |
| Experiencia de desarrollo | Un lenguaje; nuevas convenciones respecto de Kova | Experiencia, pruebas y contratos existentes | TypeScript; adaptación al entorno Workers |
| Escalabilidad | Ajustar límites, conexiones y futuros trabajos | Escalar API y frontend con control separado | Límites por petición; tareas futuras necesitan diseño |
| Seguridad | Autorización en servidor y base | Patrones comprobables de Kova, adaptados al dominio legal | Autorización, conexiones y políticas deben verificarse |
| Dependencia del proveedor | Framework portable; servicios específicos añaden dependencia | API Docker/PostgreSQL relativamente portables | Mayor dependencia si se adoptan bindings propios |
| Mantenimiento | Menos coordinación de releases | Más coordinación, con operación ya conocida | Menos VM; más conocimiento específico de plataforma |

Next.js documenta handlers HTTP dentro de la aplicación. Cloudflare documenta integración con Supabase, pero la existencia de la guía no verifica nuestros permisos, transacciones o latencia. [Next.js](https://nextjs.org/docs/app/getting-started/route-handlers), [Workers y Supabase](https://developers.cloudflare.com/workers/databases/third-party-integrations/supabase/).

Recomiendo Next.js como candidato si buscamos reducir componentes operativos. React/Vite + FastAPI merece preferencia si reutilizar la experiencia de Kova y mantener Python pesa más. Workers merece evaluación si domina el costo fijo, con prueba previa de conexiones y operación. No se elige automáticamente una de estas rutas.

Identidad es otra decisión: Supabase Auth para reducir mantenimiento; autenticación propia adaptando Kova; o Clerk con integración separada. Recomiendo evaluar identidad administrada. Supabase documenta Auth y Clerk documenta integración con Supabase; ello no aprueba nuestro modelo de organizaciones. [Supabase Auth](https://supabase.com/docs/guides/auth), [Clerk y Supabase](https://clerk.com/docs/guides/development/integrations/databases/supabase).

## Orden propuesto de preparación

No es autorización de provisioning ni un checklist de acciones ya ejecutadas. El código local puede avanzar con entornos propios y dependencias simuladas de forma explícita una vez aprobada su arquitectura; contratar todos los servicios antes de desarrollar no es requisito.

| Orden | Preparación | Dependencia y comprobación útil |
|---|---|---|
| 1 | Acordar stack, presupuesto, responsables y separación de entornos; preparar repo local y CI básico | No seleccionar servicios implícitamente ni depender de credenciales productivas de Kova |
| 2 | Diseñar identidad, propiedad y permisos de solicitudes/relaciones/contextos | Aprobación conceptual antes de tablas; criterios de aislamiento comprobables |
| 3 | Preparar PostgreSQL y migraciones; separar credenciales runtime/migración | API necesita datos y permisos; prueba de conexión bajo el rol correcto |
| 4 | Preparar URLs de entornos y dominio/DNS cuando se elija nombre; correo transaccional y remitente | Puede avanzar en paralelo al código; DNS precede a verificación de dominio de correo; no comprar identidad provisional sin decisión |
| 5 | Configurar hosting elegido y ruta frontend/API, gestión de secretos y diagnóstico | Verificar versión, health, acceso a base y comportamiento de la URL pública; Sentry o alternativa antes del primer despliegue remoto |
| 6 | Integrar identidad y probar alta, correo, sesión, recuperación y acceso por contexto | URLs/callbacks correctos; la cuenta autenticada no basta para autorizar asuntos |
| 7 | Implementar los dos flujos de IA aprobados, con proveedor, límites y tratamiento acordados | Texto seleccionado, generación manual, revisión, alternativa ante fallos y costo por resultado |
| 8 | Probar restauración, recorrido completo y recuperación del release antes de admitir datos reales | Evidencia por entorno; no confundir simulaciones con pruebas de servicios reales |
| Según su capacidad | Preparar Stripe, canales adicionales, documentos y otras integraciones | Solo al definir y aprobar sus flujos; no son dependencias de generar y copiar un borrador |

Las cuotas deben funcionar con la topología escogida: contadores compartidos y reserva de consumo si existen varias instancias. Redis/Upstash es una alternativa, no una compra obligatoria para dos botones. El esquema de almacenamiento y reserva requerirá checkpoint de datos.

## Referencias de costo, sin presupuesto aprobado

Tarifas públicas consultadas: Vercel Pro US$20/mes; Supabase Pro desde US$25/mes, con un proyecto Micro cubierto por créditos de cómputo; Workers Paid desde US$5/mes más consumo aplicable. Vercel limita Hobby al uso personal no comercial. Supabase Free puede pausar proyectos inactivos y no incluye respaldos automáticos. [Vercel](https://vercel.com/pricing), [Hobby](https://vercel.com/docs/plans/hobby), [Supabase](https://supabase.com/pricing), [Workers](https://developers.cloudflare.com/workers/platform/pricing/).

Como aritmética de referencia, Vercel Pro y Supabase Pro sumarían US$45/mes en sus bases; Workers Paid y Supabase Pro, US$30. Estas cifras no son costo total de Abogalia: faltan consumo, entornos adicionales, participantes, correo, observabilidad, IA, respaldos e impuestos. No se conoce el costo incremental de agregarlos a cuentas existentes. Las facturas de Kova no se multiplican por copiar su stack.

## Estado y siguiente decisión

Arturo aprobó aplicar lecciones de Kova como método; los flujos de IA permanecen aprobados. Se presentaron tres preguntas: camino de aplicación, identidad y tope mensual. Stack, proveedores y gasto siguen pendientes. Luego se preparará el diseño de base y permisos, conservando las decisiones funcionales sin volver a pedirlas.

Actualización de la sesión: Arturo confirmó una suite nueva para Abogalia, D-023, y aplazó el procesamiento documental con IA, D-022. Los precios y escenarios de presupuesto para recursos propios se consolidan en [servicios y tiers](26_services_and_tiers.md); los costos reales de Kova siguen siendo evidencia histórica, no tarifas de Abogalia.

## Comprobación actual de planes y costos — 2026-10-12

Arturo pidió comprobar qué paga actualmente en Kova. Se consultaron conectores de Supabase, Resend y Vercel, paneles autenticados de Fly, Cloudflare y OpenRouter, y GitHub con filtro al repositorio completo. Esta comprobación no modifica Kova ni autoriza contratar servicios de Abogalia. El checkout local y los informes históricos siguen siendo fuentes distintas de los paneles de cuenta.

| Servicio | Evidencia actual | Lectura de costo |
|---|---|---|
| Supabase PostgreSQL | La organización Kova devuelve `plan: free` | Plan gratuito confirmado |
| Resend | Dominio de Kova verificado; cuotas de 100 correos diarios y 3,000 mensuales, tres dominios | Cuotas correspondientes a Free; no se acredita una suscripción Pro |
| Cloudflare DNS y Workers | Dominio muestra `free`; Workers Free aparece activo en Billing | Sin plan de pago de esos productos observado |
| Cloudflare R2 | Suscripción `R2 Paid` activa, con costo de uso US$0.00 en el ciclo 25 de septiembre–24 de octubre, observado hasta el 12 | Facturación habilitada, uso dentro de las cuotas incluidas; no confundir etiqueta Paid con un cargo actual |
| Fly | Cost Explorer 1–12 de octubre y Upcoming Invoice: US$12.67 tras actualizar datos; Last Invoice: US$14.23 para 1 de septiembre–1 de octubre | Cargo por uso confirmado; el acumulado no es una mensualidad fija ni cierre de octubre |
| OpenRouter | Compra de créditos US$10 el 7 de octubre, saldo US$8.84; Activity último mes: gasto US$1.16 | Pago anticipado y consumo son conceptos distintos; evaluación y producción aparecen como claves separadas |
| GitHub y Actions | Billing Overview confirma GitHub Free US$0/mes; filtro al repositorio `ArturoFrancoMozqueda/kova`, octubre: Linux y storage muestran Billed US$0 | Cuenta usa 1,163 de 2,000 minutos incluidos; consumo bruto de Kova US$29.21 cubierto por descuentos/cuota, no un cargo. Los minutos son compartidos con otros repositorios |
| Vercel | Conector confirma equipo Kova y proyecto actual `kova-web`; no expone plan. Billing devuelve error y la sesión Edge disponible no pertenece al equipo | Importe pendiente: no inferir Pro US$20 ni Hobby a partir de otra cuenta |
| UptimeRobot | Runbook documenta Free; panel actual exige login | Free histórico/documentado, sin reconfirmación de factura actual |
| Sentry, Upstash y Stripe | Integraciones en código/docs; paneles actuales requieren login | Actividad y cargos reales pendientes |
| Dominio | Dominio de Kova activo | Registrador, pago y renovación sin factura verificada |

La cifra US$12.20 de Fly en la auditoría anterior y en la primera carga de esta revisión queda como captura anterior: el panel actualizado muestra US$12.67. La última auditoría de operación, publicada hoy en el chat de costos, confirmó la ingesta de documentos bajo demanda y su apagado automático; API y chat conservan capacidad encendida. No se extrapola el costo de la ingesta permanente como nueva factura ni se descuenta retrospectivamente el ahorro del acumulado.

Fuentes de cuenta: [Fly Billing](https://fly.io/dashboard/pos-project/billing), [Fly Cost Explorer](https://fly.io/dashboard/pos-project/billing/cost-explorer?start_date=2026-10-01&end_date=2026-10-12), [Cloudflare Billing](https://dash.cloudflare.com/47d850c847503be3597dc7165cfea177/billing/billable-usage), [OpenRouter créditos](https://openrouter.ai/settings/credits), [OpenRouter actividad](https://openrouter.ai/activity), [GitHub consumo de Kova](https://github.com/settings/billing/usage?query=repo%3AArturoFrancoMozqueda%2Fkova). Supabase y Resend se verificaron con sus conectores, sin consultar datos de clientes ni valores de secretos. No se suman períodos diferentes ni se presenta un total mensual cerrado mientras falten Vercel y otras facturas.
