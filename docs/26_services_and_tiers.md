# Servicios y tiers para una suite independiente de Abogalia

Consulta: 2026-10-12. React + FastAPI aprobado en D-025. Este documento conserva comparación y tarifas; la suite vigente está en el checkpoint de base técnica, D-026. Proveedores, tiers, presupuesto y contratación siguen pendientes. Tarifas públicas en USD; no constituyen una factura ni un techo de gasto. No se han creado cuentas, recursos o claves.

## Alcance y criterio

**Propuesta vigente tras revisar Kova:** Cloudflare Static Assets Free para React + una API FastAPI Fly de 1 GB + Supabase Free + Resend Free en recursos propios: referencia US$6.70 por 30 días de cómputo en iad/ewr, antes de consumo, dominio, IA, impuestos y excedentes. No es un total garantizado ni selección aprobada. [Checkpoint vigente](checkpoints/platform-foundation-low-cost.md). Las recomendaciones anteriores de Vercel/Render y escenarios pagados se conservan como alternativas; la prioridad actual es continuidad con la operación de Kova y bajo costo inicial.

Supabase Free permite dos proyectos activos entre las organizaciones administradas, no dos por nueva organización; proyectos pausados no cuentan. El conector muestra Kova activa y CENEVAL inactiva: confirmar cupo antes de crear Abogalia, sin modificar esos proyectos. Resend permite equipos con claves, uso y facturación propios bajo el mismo administrador. [Supabase billing](https://supabase.com/docs/guides/platform/billing-on-supabase), [Resend Teams](https://resend.com/docs/dashboard/settings/team). La separación de recursos y facturación conserva D-023; no obliga a otra identidad personal por proveedor.


### Alternativas para empezar con hosting gratuito, investigadas el 2026-10-12

Arturo pidió alternativas gratuitas que conserven React + FastAPI y permitan pagar después. No se elige proveedor ni se contrata infraestructura por esta pregunta. La recomendación previa de Vercel era por integración operativa, no porque fuera indispensable.

- **Render:** React como sitio estático gratuito y FastAPI como Web Service Free. La guía oficial incluye FastAPI. La API se suspende tras 15 minutos sin tráfico y tarda aproximadamente un minuto en volver; hay 750 horas gratuitas compartidas por workspace. Render desaconseja expresamente las instancias Free para producción. Para quitar la suspensión se paga cómputo del servicio, no basta subir el workspace de plan. La tarifa consultada directamente en el HTML oficial es US$7/mes para 512 MB en el primer tamaño pagado; el workspace Hobby tiene cuota US$0 y permite una persona, con consumo aparte. Esto ofrece construcción gratuita y operación inicial económica con Python convencional, no una garantía de capacidad o alta disponibilidad. [Free y limitaciones](https://render.com/docs/free), [FastAPI](https://render.com/docs/deploy-fastapi), [tarifas](https://render.com/pricing), [workspace](https://render.com/docs/platform-features-by-plan). Su Postgres Free caduca a los 30 días: no se propone para persistencia de Abogalia; Supabase sigue siendo candidato externo. React estático no resuelve automáticamente el renderizado del catálogo público.
- **Cloudflare Workers:** la documentación actual confirma FastAPI en Python Workers y frontend estático con Static Assets. El hosting podría tener cuota US$0 dentro de Free; Paid parte de US$5/mes y consumo. Free limita ejecuciones a 100,000 solicitudes diarias y 10 ms de CPU por invocación. Python usa Pyodide/WebAssembly: no se garantiza compatibilidad con las bibliotecas de Kova, drivers PostgreSQL, criptografía o recursos del sistema. Verificar acceso a Supabase, transacciones y aislamiento, sesiones/JWT, paquetes y CPU antes de adoptarlo. Esta opción se omitió en la comparación anterior de Python y debe evaluarse, sin convertir soporte del framework en validación de toda la aplicación. [FastAPI y frontend](https://developers.cloudflare.com/workers/languages/python/packages/fastapi/), [paquetes](https://developers.cloudflare.com/workers/languages/python/packages/), [runtime](https://developers.cloudflare.com/workers/languages/python/stdlib/), [precios](https://developers.cloudflare.com/workers/platform/pricing/).
- **Vercel Hobby:** uso personal no comercial; la condición no depende solo de cobrar o de superar capacidad. Promocionar servicios con fin económico está incluido en la definición. No se propone para alojar Abogalia como negocio. [Fair use](https://vercel.com/docs/limits/fair-use-guidelines).

Con Supabase Free y Resend Free, Render durante construcción puede sumar US$0 de bases; al activar una API pagada de US$7, la base sería US$7 si los demás siguen en Free. Cloudflare completo podría sumar US$0 de bases si la prueba de compatibilidad y CPU resulta suficiente, o al menos US$5 con Workers Paid. Todos estos escenarios excluyen dominio, IA, impuestos y excedentes; cuotas, recuperación de datos y uso comercial se revisan antes de operar. D-026 sigue Discussing. No existe código ni prueba de carga que confirme la adecuación de un tamaño.

### Ajuste vigente: comenzar con capacidad pequeña y pagar al necesitarla

Arturo cuestionó las cuotas iniciales y pidió crecer verticalmente. No se registra aprobación de proveedores o presupuesto. La recomendación revisada evita contratar Resend Pro y una segunda base alojada de inicio: Vercel Pro US$20 + Supabase Pro con una Micro US$25 + Resend Free US$0 = **US$45 mensuales de base** para producción. Free de correo exige margen dentro de 100 mensajes diarios y 3,000 mensuales; cambiar de plan antes de comprometer acceso y notificaciones. Añadir otra Micro lleva la base a aproximadamente US$55; Resend Pro añade US$20 cuando sus funciones o cuotas lo justifiquen. [Vercel](https://vercel.com/docs/plans/pro-plan), [Supabase](https://supabase.com/pricing), [Resend](https://resend.com/pricing).

Construcción y pruebas locales aisladas pueden tener US$0 de cuotas de estos servicios; no se propone pagar producción antes de necesitarla. Supabase Free también sirve para desarrollo alojado si hay cuota disponible, pero puede pausarse por inactividad y carece de backups automáticos. El uso inicial de Pro con clientes reales se recomienda por continuidad y recuperación, no por necesidad anticipada de gran capacidad. Hobby de Vercel está restringido a uso personal no comercial. [Hobby](https://vercel.com/docs/plans/hobby).

El crecimiento vertical de base es gradual: Pro con Micro suma US$25; con una Small, US$25 de plan + US$15 de cómputo − US$10 de crédito = aproximadamente US$30. No exige Team ni otra base. Functions crece por ejecuciones por demanda y tiene sus propios límites de memoria; no funciona como una sola VM que se redimensiona. Aumentar recursos solo tras medir latencia, memoria, CPU y conexiones y corregir consultas o trabajo innecesario. Los ejemplos no garantizan capacidad para un número de usuarios ni incluyen excedentes, dominio, IA, pagos o impuestos.

Las comparaciones siguientes de US$65–75 conservan el supuesto de correo pagado: son escenarios anteriores de operación, no mínimos de lanzamiento. La reserva previa de US$100 no es un gasto obligatorio ni presupuesto aprobado. El checkpoint contiene la propuesta inicial vigente.

### Recomendación revisada: conservar React + FastAPI y simplificar hosting

Arturo pidió una solución semejante a Kova, mejorando costes y operación. React + FastAPI continúa Approved en D-025. La recomendación de hosting pasa a evaluar ambos componentes en Vercel Pro, con Resend y Supabase; servicios y gasto siguen Discussing en D-026.

La comparación anterior omitió FastAPI en Vercel. La documentación vigente confirma soporte nativo en Python Functions y permite dos proyectos del mismo repositorio. Se propone un proyecto frontend y otro API dentro del mismo equipo Pro, con un pipeline coordinado. También existe Services para agruparlos en un despliegue, pero está en beta y no se propone como dependencia obligatoria. [FastAPI en Vercel](https://vercel.com/docs/frameworks/backend/fastapi), [monorepos](https://vercel.com/docs/monorepos), [Services beta](https://vercel.com/docs/services).

| Escenario comparable con Resend Pro | Producción: una base | Producción y base de pruebas separada |
|---|---:|---:|
| Cloudflare Paid y Fly: dos API producción, una API de pruebas cuando corresponde | US$63.40 | ≈US$80.10 |
| Vercel Pro para React y FastAPI | US$65 | ≈US$75 |
| Vercel para React y Fly para FastAPI, conservando separación de proveedores semejante a Kova | US$78.40 | ≈US$95.10 |

Son sumas de cuotas base, no comparaciones de factura o capacidad equivalentes ya medidas. Supuestos: un seat de despliegue, Resend US$20, Supabase US$25/≈US$35; Fly a US$6.70 por máquina de 1 GB en regiones de referencia y mes de 30 días. Vercel Pro US$20 incluye un seat y US$20 de crédito de consumo compartido; funciones, builds y recursos por encima del crédito añaden coste. Previews y pruebas también consumen recursos. No se cobran automáticamente US$20 por cada proyecto del equipo, ni se duplica el crédito por tener dos proyectos. [Vercel Pro](https://vercel.com/docs/plans/pro-plan), [Fly](https://docs.fly.io/about/pricing), [Supabase](https://supabase.com/pricing), [Resend](https://resend.com/pricing).

En producción Vercel suma US$1.60 más de base que la propuesta Cloudflare/Fly; con pruebas suma US$5.10 menos. La simplificación operativa es una razón más fuerte que esa diferencia pequeña. El consumo puede invertirla. Al mantener Fly y añadir Vercel en lugar de Cloudflare, la base sube US$15. No se puede concluir que cambiar solo el frontend a Vercel ahorre.

Para tareas breves se propone evaluar eventos durables y Supabase Queues/Cron, con consumidor acotado en FastAPI, sin máquina permanente de jobs ni contrato Cloudflare Paid obligatorio. Comparten capacidad PostgreSQL y generan consumo de ejecución; requieren diseño, reintentos, deduplicación y límites. [Queues](https://supabase.com/docs/guides/queues), [Cron](https://supabase.com/docs/guides/cron). Si se conservan Cloudflare Queues, su plan Paid añadiría al menos US$5 en los escenarios sin hosting Cloudflare; no se oculta ese cargo.

Funciones tienen límites de duración, memoria y payload; FastAPI debe mantener estado externo. Para archivos básicos, proponer carga directa autorizada a Storage en lugar de enviar archivos grandes a través de una función. La carga segura, autenticación, conexiones, sesiones, cold starts y previews se verificarán antes de elegir hosting definitivamente. [Límites de Functions](https://vercel.com/docs/functions/limitations).

Las mejoras propuestas respecto de Kova son identidad administrada por evaluar, una única ruta de release y comprobación de versiones, permisos de base adecuados a Abogalia, métricas de entrega de correo, restauración comprobada y cuotas/alertas sin servidores documentales permanentes. No se cambian frameworks aprobados ni se presume que una guía haya validado nuestra aplicación.

Arturo confirmó una suite nueva para Abogalia. La comparación supone recursos, credenciales, dominios y medición propios, sin descontar créditos o suscripciones de Kova. Las lecciones de Kova orientan configuración y operación, no reutilización de infraestructura.

Se aplaza el procesamiento documental con IA: OCR, extracción e indexación. Continúan las dos funciones de texto aprobadas: resumen revisable y borrador editable. La decisión no elimina la gestión básica de documentos de la visión del producto.

Se distinguen hechos de las fuentes, recomendaciones de diseño y ejemplos calculados. Antes de contratar se volverán a revisar tarifas, condiciones y disponibilidad. Las promociones, impuestos, región, volumen y configuración pueden modificar la factura. La comparación inicial omitió Cloudflare Email Service; esta omisión se corrigió durante la misma sesión tras la pregunta de Arturo. No se considera obligatorio contratar Resend.

## Base de datos e identidad

**Hechos:** Supabase Free cuesta US$0, ofrece 500 MB de base de datos y puede pausar proyectos tras una semana de inactividad; carece de backups automáticos. Pro parte de US$25 por organización y mes, incluye US$10 de crédito de cómputo para una instancia Micro, backups diarios conservados siete días y 100,000 usuarios activos mensuales de Auth. Los proyectos adicionales parten de US$10 mensuales cada uno. [Tarifas de Supabase](https://supabase.com/pricing).

**Recomendación:** desarrollo local y Supabase Pro con Micro cuando se opere con clientes reales. Pro se justificaría por recuperación y continuidad, no por anticipar miles de usuarios. Proponer Supabase Auth en ese mismo proyecto evita contratar otro proveedor de identidad inicialmente; los permisos de cliente, práctica independiente y despacho requieren nuestro diseño y verificaciones.

**Alternativa:** Clerk Hobby es gratuito hasta 50,000 usuarios retenidos mensuales por aplicación, pero no incluye MFA. Pro cuesta US$25 con pago mensual o US$20 al mes facturados anualmente. La oferta B2B básica incluye 100 organizaciones retenidas al mes y hasta 20 miembros por organización; el complemento ampliado cuesta US$100 mensuales. MRU y MAU son unidades distintas. [Tarifas de Clerk](https://clerk.com/pricing).

Preferiría Supabase Auth si elegimos Supabase para datos y sus funciones cubren los requisitos. Clerk merece una evaluación si sus interfaces y funciones de identidad compensan una integración y facturación adicionales. La autenticación propia de Kova implica mantenimiento continuo; no la escogería solo para evitar una tarifa.

**Control de costo:** el Spend Cap de Supabase excluye cómputo y otros recursos contratados explícitamente. No fija toda la factura en US$25. Dos proyectos Micro mantenidos durante un mes se presupuestan en aproximadamente US$35 de base en una organización Pro, antes de excedentes. [Control de costos](https://supabase.com/docs/guides/platform/cost-control), [factura y créditos](https://supabase.com/docs/guides/platform/your-monthly-invoice).

**Recuperación:** los backups de la base no incluyen los archivos guardados en Storage. Cuando se diseñe la carga básica de documentos habrá que definir recuperación de archivos aparte; no implica aprobar ingesta con IA. [Backups](https://supabase.com/docs/guides/platform/backups).

## Dónde ejecutar la aplicación

| Camino | Tier y tarifa verificada | Recomendación y condición |
|---|---|---|
| Next.js integrado en Vercel | Pro: US$20/mes de plataforma, una persona con permisos de despliegue y US$20 de crédito de consumo incluidos. Cada persona adicional que despliega cuesta US$20/mes | Mi preferencia si priorizamos integración y menos componentes operativos; aplicación y API pueden compartir proyecto |
| Aplicación compatible con Workers | Workers Paid: mínimo US$5/mes por cuenta; 10 millones de solicitudes y 30 millones de milisegundos de CPU al mes incluidos | Alternativa si priorizamos base económica y validamos framework, dependencias y operación en ese entorno |
| Frontend más API Python en Fly.io | Machines por consumo, sin cuota mensual de plataforma. Una shared-cpu-1x de 512 MB cuesta US$3.69 por 30 días encendida en iad/ewr | Considerarla si FastAPI aporta una ventaja concreta; el frontend y el despliegue de API se presupuestan aparte |

Fuentes: [Vercel Pro](https://vercel.com/docs/plans/pro-plan), [Workers pricing](https://developers.cloudflare.com/workers/platform/pricing/), [Fly.io resource pricing](https://docs.fly.io/about/pricing).

Vercel Hobby está limitado al uso personal no comercial: no es el tier propuesto para este negocio. Pro puede cobrar consumo que supere el crédito y complementos. [Condiciones de Hobby](https://vercel.com/docs/plans/hobby).

Workers cobra después de sus inclusiones US$0.30 por millón de solicitudes y US$0.02 por millón de milisegundos de CPU. Los US$5 no incluyen nuestra base Supabase ni proveedor de IA; el plan sí incluye cuota de Cloudflare Email Service, detallada abajo. Los activos estáticos tienen solicitudes gratuitas sin límite. Su tier Free limita la ejecución a 100,000 solicitudes diarias y 10 ms de CPU por invocación; no lo propondría como compromiso de operación antes de medir el flujo completo. [Tarifas y límites](https://developers.cloudflare.com/workers/platform/pricing/).

Cloudflare también documenta Next.js: actualmente recomienda vinext como camino predeterminado, y conserva OpenNext para aplicaciones existentes con brechas de compatibilidad. Por tanto, Next.js no obliga a usar Vercel, pero no se debe asumir equivalencia de entornos ni copiar instrucciones antiguas. [Guía vigente de Next.js](https://developers.cloudflare.com/workers/framework-guides/web-apps/nextjs/).

Los US$3.69 de Fly corresponden a una máquina y una región concretas, no a una capacidad comprobada para Abogalia. Réplicas, memoria, región, almacenamiento y transferencia pueden añadir costo. Evitaría una máquina permanente para asistencia de texto si podemos resolver las peticiones en el backend elegido.

## Correo de acceso y notificaciones

### Cloudflare Email Service como alternativa

**Hechos verificados:** Email Sending permite correo transaccional y aparece en beta en la documentación vigente. Ofrece bindings de Workers, REST API y SMTP; no exige alojar toda la aplicación en Workers. [Servicio oficial](https://developers.cloudflare.com/email-service/).

Workers Paid incluye 3,000 envíos mensuales por cuenta; el excedente cuesta US$0.35 por 1,000 correos. Esta cuota está dentro del plan Paid ya presupuestado, no requiere sumar otra cuota base de correo. Enviar a destinatarios arbitrarios requiere Paid; el envío gratuito a direcciones de destino verificadas de la cuenta no resuelve el registro público de usuarios. [Precios de Email Service](https://developers.cloudflare.com/email-service/platform/pricing/).

El dominio debe utilizar Cloudflare DNS y darse de alta para envío. [Preparación del dominio](https://developers.cloudflare.com/email-service/get-started/send-emails/). Las cuentas nuevas comienzan con una cuota diaria conservadora, ajustable según uso y reputación. La página pública no fija un número universal: hay que comprobar la cuota de la cuenta y solicitar ampliación si hace falta. [Límites actuales](https://developers.cloudflare.com/email-service/platform/limits/).

**Recomendación revisada:** si elegimos Workers Paid, evaluar primero Email Service para acceso y notificaciones. Podría sustituir Resend para ese alcance y reducir proveedores. Antes de usarlo con clientes, validar disponibilidad de beta, cuota diaria, SMTP con Supabase Auth, recuperación de acceso, entrega en los proveedores de correo previstos y seguimiento de rebotes. Esta propuesta no supone equivalencia de todas las funciones ni una integración probada. Resend queda como alternativa según los resultados, sin contratar ambos de inicio.

Email Routing reenvía correo entrante; Email Sending es la capacidad pertinente para enviar confirmaciones y notificaciones a clientes. No se aprueba aquí un sistema que ejecute acciones a partir de correos entrantes.

### Resend como alternativa

**Hechos:** Resend Free incluye 3,000 correos al mes, máximo 100 diarios, tres dominios y un endpoint de webhooks. Pro cuesta US$20/mes, incluye 50,000 correos, diez dominios, cinco endpoints y elimina el límite diario del proveedor. El excedente publicado es US$0.90 por 1,000 correos cuando se habilita pay-as-you-go en un plan pagado. Los planes son mensuales. [Tarifas de Resend](https://resend.com/pricing).

**Recomendación:** Free durante construcción y uso que quepa holgadamente en ambas cuotas; pasar a Pro antes de que registros, recuperación de acceso y notificaciones puedan agotar el límite diario. El número de cuentas no equivale al número de correos. Definiríamos una alerta previa al agotamiento, por ejemplo al 70%, como regla nuestra, no como condición del proveedor.

Si usamos Supabase Auth, configuraremos correo propio antes de abrir registros reales: su SMTP predeterminado se limita a direcciones del equipo, actualmente dos mensajes por hora, y no está destinado a producción. [SMTP de Supabase](https://supabase.com/docs/guides/auth/auth-smtp).

Lección de Kova: preparar dominio y autenticación de correo antes del flujo de acceso; distinguir aceptado, entregado, rebotado y llegada a bandeja. Registrar fallos y eventos de entrega. El borrador de IA aprobado termina en copia manual y no necesita integración de envío.

## Errores y diagnóstico

**Hechos:** Sentry Developer es gratuito, limitado a un usuario del panel e incluye 5,000 errores. Team tiene tarifa base de US$29 con pago mensual o US$26/mes en modalidad anual; incorpora usuarios ilimitados y 50,000 errores. Las cantidades incluidas corresponden al ciclo mensual de cuota. [Tarifas de Sentry](https://sentry.io/pricing/).

**Verificación:** la herramienta de navegación no pudo interpretar esa página; se consultó directamente el HTML oficial. Developer y cuotas aparecen en el texto; el dato estructurado de precios confirma US$29 mensual y US$312 anual para Team. No se usaron precios de terceros.

**Recomendación:** Developer si una sola persona atenderá errores; Team si varias necesitan acceso operativo o se supera la capacidad útil del plan gratuito. Configurar filtrado de datos antes de instrumentar relatos y mensajes; no capturar su contenido en telemetría. La vigilancia de disponibilidad se decidirá junto con hosting y operación, sin contratar otro tablero por anticipación.

## Dos funciones de IA mediante API

**Hechos:** GPT-6 Luna publica US$0.10 por millón de tokens de entrada y US$0.50 por millón de salida en modo Standard y contexto corto; GPT-6.1 Sol publica US$2 y US$10 respectivamente. Son tarifas de API por consumo. [Precios de OpenAI](https://developers.openai.com/api/docs/pricing).

**Recomendación:** evaluar una API directa con Luna como candidato económico y compararla con Sol en fidelidad al texto, omisiones, compromisos inventados y latencia. Elegir después del resultado; el menor precio no prueba calidad suficiente. No necesitamos un servidor de modelos propio para esta propuesta.

**Ejemplo calculado, no pronóstico:** 1,000 generaciones de 3,000 tokens de entrada y 500 tokens de salida facturables cada una costarían US$0.55 con Luna o US$11 con Sol. La entrada incluye instrucciones y texto; la salida facturable incluye razonamiento cuando corresponda. No incorpora herramientas, reintentos, escritura de caché, primas regionales o impuestos. [Características y modalidades de Luna](https://developers.openai.com/api/docs/models/gpt-6-luna).

El consumo deberá limitarse desde Abogalia con tamaño máximo, cuotas y reserva global antes de cada generación. Los importes siguen pendientes. Para información real también está pendiente aprobar el tratamiento: la API no usa datos para entrenamiento por defecto, pero los registros de control de abuso pueden conservar contenido hasta 30 días, sujetos a las excepciones documentadas. No equivale a retención cero. [Controles de datos](https://developers.openai.com/api/docs/guides/your-data). **LEGAL REVIEW REQUIRED** para tratamiento de información jurídica personal.

## Escenarios de base mensual

Supuestos: suite nueva; una persona que despliega; Supabase Micro; Sentry gratuito dentro de sus restricciones. Correo con Resend Free o, si se elige Workers Paid, Cloudflare Email Service dentro de su cuota incluida y de los límites efectivos de la cuenta. Staging significa entorno de pruebas separado, sin datos de clientes reales.

| Escenario | Hosting | Supabase | Base calculada |
|---|---:|---:|---:|
| Vercel Pro y una base de producción | US$20 | US$25 | US$45 |
| Vercel Pro y dos bases Micro: producción y staging | US$20 | ≈US$35 | ≈US$55 |
| Workers Paid y una base de producción | US$5 | US$25 | US$30 |
| Workers Paid y dos bases Micro: producción y staging | US$5 | ≈US$35 | ≈US$40 |

Son sumas de bases, no paquetes de precio cerrado. Añadir IA, excedentes, dominio y renovación, impuestos, cambio de moneda y cualquier complemento o servicio operativo adicional. Resend Pro añadiría US$20; Sentry Team mensual añadiría US$29. Si se eligiera Clerk Pro en vez de Supabase Auth, su tarifa se añadiría a la base de datos.

Durante desarrollo local podemos evitar cuotas de hosting y probar con recursos gratuitos cuando estén disponibles; esa alternativa no es una infraestructura de producción aprobada. No se recomienda pagar producción meses antes de usarla, ni mezclar staging con datos reales para ahorrar una instancia.

## Orden de decisión y configuración propuesto

1. Elegir camino de aplicación y hosting, comparando mantenimiento, coste y requisitos.
2. Diseñar identidad, contextos profesionales y permisos; elegir proveedor y regiones.
3. Preparar entornos y secretos propios; desarrollo local y migraciones verificables.
4. Preparar correo y recuperación de acceso antes de invitar usuarios reales.
5. Instrumentar errores y comprobar restauración y despliegue del recorrido completo.
6. Activar las dos funciones de IA después de tratamiento, evaluación y cuotas.

Pagos, liquidaciones, suscripciones del producto, calendario externo y almacenamiento de archivos tendrán decisiones específicas cuando se definan sus flujos. Este documento no aprueba ni estima esas integraciones. El nombre y dominio siguen pendientes; no se supone su disponibilidad.

La recomendación de Vercel de esta sección es una alternativa anterior; la propuesta inicial vigente es Cloudflare/Fly con Supabase y Resend Free, descrita al inicio; el ajuste vigente al principio de este documento detalla una base inicial US$45 con Resend Free y una Micro, o ≈US$55 si se añade otra Micro de pruebas. React + FastAPI están Approved en D-025; hosting, identidad, regiones, renderizado y gasto permanecen Discussing, D-026. Los escenarios anteriores se conservan como comparación histórica, sin tratarse como factura vigente. [Checkpoint actual](checkpoints/platform-foundation.md).
