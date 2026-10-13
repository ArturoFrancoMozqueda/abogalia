# Checkpoint — Identidad y contextos

Fecha: 2026-10-12. Orden T01, A1; capacidades C02/C03. Estado: **Approved para recomendaciones A IC-01–IC-06; implementación pendiente**. Preparado para revisión de A0 y una sesión de seis decisiones con Arturo. Este documento no aprueba ni implementa registro, permisos, tenencia, sesiones o tablas. Base de trabajo: `codex/identity-design`, HEAD `c71fea298742a43994cf6026494ded080b3ef50d` más fundación y documentos locales sin commit, conservados.

## Aprobación y alcance vigente

Arturo respondió «aprobado, tu continua proactivamente» después de la entrega
T01–T04. Quedan aprobadas las recomendaciones A IC-01–IC-06, el modelo conceptual
aplicable a Identity y la matriz recomendada, incluida la distinción de salida
profesional y participación cliente. Las alternativas B/C se conservan como
antecedentes; los textos que indicaban Awaiting decision describen la preparación
anterior y quedan superados dentro de este alcance por D-031.

Retención elegida expresamente por Arturo: 30 días tras cierre de cuenta o fin de
membresía para evidencia mínima; 90 días para auditoría; borrado/anonimización
posterior. D-032 no decide retención de contenido jurídico, credenciales profesionales
ni relaciones de servicio futuras. Sesiones de aplicación: máximo 12 horas y 30
minutos de inactividad; al terminar se retiran tokens custodiados sin conservar
contenido de sesión como auditoría. Revisión jurídica sigue pendiente antes de
información real. No están autorizados hosting, gasto, correo externo, migraciones
remotas, despliegue ni verificación profesional C03 por esta aprobación.

Detalles técnicos de SameSite, CSRF, custodia cifrada y transacciones se concretan
en el contrato de implementación manteniendo estos objetivos y privilegios mínimos.
No se vuelve a pedir aprobación del diseño ya aprobado.

## Lo que entiendo

Una persona debe poder acceder a Abogalia como cliente y, si corresponde, trabajar como profesional con práctica propia y pertenencia a un despacho. D-003 ya aprueba esa convivencia; no define quién puede ver una relación ni qué ocurre al salir del despacho. Necesitamos distinguir identidad autenticada, actividad elegida, contexto profesional y acceso a cada recurso.

Supabase Auth está aprobado como proveedor, D-028; aún no hay integración. React + FastAPI, D-025, y el monorepo con React Router sobre Vite, D-030, fijan la base. La portada prerenderizada y el health local no demuestran autenticación o autorización. El proyecto vacío de D-029 tampoco representa un esquema de negocio aprobado.

T01 prepara el contrato de decisión para T02 (amenazas y acceso) y T03 (modelo conceptual); esos documentos deben conservar los identificadores IC-01 a IC-06. C03 incluye aquí separación de contextos y membresía; el proceso de verificación profesional, evidencias, responsables, apelaciones y publicación necesita la sesión posterior de Atención y confianza. Registrarse no certifica capacidad profesional.

## Decisiones tomadas

| Referencia | Alcance vigente | Límite que se conserva |
|---|---|---|
| D-003 Approved | Práctica independiente y pertenencia a un despacho por abogado | No aprueba pertenencia simultánea a varios despachos, roles, propiedad ni transferencia |
| D-025 Approved | Frontend React y backend central FastAPI | No selecciona transporte de sesión ni vía de acceso a PostgreSQL |
| D-028 Approved | Supabase Auth | No aprueba métodos de registro, MFA, recuperación ni duración/revocación de sesión |
| D-029 Implemented | Proyecto propio vacío Free/us-east-1 verificado | Sin usuarios de aplicación, tablas de negocio o permiso para modificar grants |
| D-030 Implemented | Monorepo, apps/web React Router/Vite y apps/api FastAPI; base local | Sin login, flujos privados, conexión de aplicación o despliegue |
| D-023/D-027 Approved | Recursos por producto; administración con posprojectsupport | Identidad administrativa distinta del usuario del producto; Kova excluido |
| D-005 Approved y AGENTS.md | Checkpoint previo y protección de secretos | Aprobar proveedor/base no aprueba capacidades posteriores |

Si un documento histórico propone roles globales, un cliente compartido o un camino de datos distinto, se mantiene como antecedente y se reconcilia mediante IC-02, IC-03 o IC-06; no modifica estas decisiones. D-024 permanece Proposed y D-026 Discussing. No se seleccionan hosting, gasto, precios, retención o proveedores adicionales.

## Decisiones pendientes

Las seis preguntas siguientes constituyen el contrato compartido, en este orden. **Todas las alternativas y recomendaciones son Proposed / Awaiting decision.** Arturo puede aprobar, cambiar o aplazar cada paquete; A0 debe registrar sus parámetros concretos, sin interpretar una respuesta parcial como aprobación completa.

### IC-01 — Registro, acceso inicial y recuperación

**Pregunta:** ¿Iniciamos con cuenta por correo y contraseña, correo confirmado y recuperación acotada, permitiendo registro público de clientes y solicitud de alta profesional, con invitación para ingresar a un despacho?

- **A, recomendada:** correo/contraseña y confirmación; identidad inicial sin permisos profesionales; alta profesional separada; membresía solo por invitación aceptada. Recuperación mediante Supabase Auth, respuestas que no revelen si existe una cuenta y destinos de retorno permitidos expresamente. No altas anónimas, teléfono ni proveedores sociales en este primer bloque.
- **B:** acceso por código/enlace de correo, conservando los mismos límites de alta profesional y membresía. Reduce gestión de contraseñas, depende más de entrega y disponibilidad del correo.
- **C:** piloto solo por invitación para todos. Reduce exposición inicial, añade operación manual y restringe registro abierto.

La aprobación debe indicar método, quién puede registrarse, condición de acceso antes de confirmar correo y recuperación. Activar envío de correo exige remitente, límites y operación aprobados en su bloque; esta propuesta no contrata ni configura correo. El proveedor de correo predeterminado de Supabase está limitado a miembros de la organización; no basta para registro público. Los proyectos Free nuevos con ese proveedor tampoco pueden personalizar plantillas Auth desde el 2026-06-03. Evaluar SMTP propio o hook con su aprobación independiente, sin seleccionar proveedor aquí. [Destinatarios de correo predeterminado](https://supabase.com/changelog/29370-supabase-auth-changes-to-default-email-provider), [cambio de plantillas Free](https://supabase.com/changelog/46599-changes-to-email-template-customisation-on-free-tier). Términos, aviso, consentimientos y recuperación administrativa requieren especificación y **LEGAL REVIEW REQUIRED** donde corresponda antes de datos reales.

### IC-02 — Una identidad con varias funciones y cambio de contexto

**Pregunta:** ¿Usamos una sola identidad personal con función de cliente y habilitación profesional separadas, práctica propia más un despacho activo, y elección explícita de contexto en cada acción profesional?

- **A, recomendada:** una identidad; cliente y profesional pueden coexistir; práctica propia y un despacho activo respetan D-003. La selección de contexto orienta navegación, pero el servidor vuelve a comprobar acceso por objeto y acción. No rol profesional global que abra todos los datos.
- **B:** cuentas separadas para actividad cliente y profesional; el profesional sigue teniendo práctica propia y despacho. Aumenta logins y complejidad al vincular identidades.
- **C:** una identidad y varias membresías de despacho activas desde el inicio. Amplía D-003 y requiere aprobación expresa de cardinalidad, UX y controles adicionales.

La aprobación define cardinalidad y convivencia de funciones; la matriz de permisos por acción debe aprobarse con IC-04 antes de código. El rol técnico `authenticated` de PostgreSQL no equivale a abogado, cliente, administrador de despacho ni operador de Abogalia.

### IC-03 — Propiedad de relación y alcance del cliente

**Pregunta:** ¿Cada relación pertenece a un contexto profesional, con responsable asignado y participación del cliente acotada a esa relación, sin compartir su ficha entre prácticas o despachos?

- **A, recomendada:** práctica propia o despacho es el contexto propietario; abogado asignado es responsable y puede cambiar conforme al contrato aprobado. El mismo usuario cliente puede participar en relaciones distintas; cada ficha/contexto conserva información y permisos separados. No transferencia automática al salir del despacho.
- **B:** cada relación pertenece al abogado que la inicia, con colaboración explícita del despacho. Facilita continuidad personal, complica gestión institucional y salida.
- **C:** propiedad pactada individualmente por relación. Es flexible, aumenta reglas, UX contractual y combinaciones de acceso.

La aprobación define propiedad operativa, participantes y quién autoriza cambios; no concluye titularidad jurídica de expedientes o derechos de datos. Para cualquier transferencia futura se requiere diseño de consentimiento, autorización, historial y límites; **LEGAL REVIEW REQUIRED**. Solicitud, consulta, reserva y asunto siguen siendo conceptos distintos; no crear `case` genérico ni un cliente global accesible por todos.

### IC-04 — Membresía, permisos, suspensión y salida

**Pregunta:** ¿Adoptamos invitación aceptada, permisos por capacidad y relación asignada, salida/suspensión sin nuevas facultades profesionales derivadas de la membresía y continuidad de la práctica propia, con reasignación explícita de responsabilidades y evaluación separada de cualquier participación como cliente?

- **A, recomendada:** administración de miembros separada del acceso al contenido jurídico. Ser miembro no abre todas las relaciones; asignación y acción autorizada gobiernan contenido. Invitación pendiente no da acceso. Suspensión/salida retira facultades profesionales derivadas de la membresía; la práctica propia permanece aislada. Si esa persona también participa como cliente en una relación del despacho, su acceso por esa participación se reevalúa por separado conforme a IC-03 y a la matriz aprobada: no se niega automáticamente toda participación legítima ni se conservan privilegios profesionales por ser cliente. Reasignación pertenece al contexto conforme a IC-03, con responsable y auditoría; no se copian expedientes al exmiembro. Esta distinción también sigue Proposed / Awaiting decision.
- **B:** miembros activos acceden a todas las relaciones del despacho, con restricciones por acciones. Menos administración, mayor exposición y alcance que Arturo tendría que aprobar expresamente.
- **C:** permisos personalizados por objeto desde el inicio. Mayor precisión y carga de gestión/pruebas.

La aprobación debe fijar actores autorizados para invitar, aceptar, suspender, expulsar, salir y reasignar; si hay un último administrador, se recomienda bloquear su salida hasta transferir administración por flujo autorizado. Esta restricción también está pendiente. A2 propone la matriz concreta. Cambiar membresía debe ser transaccional frente a una operación concurrente; datos históricos y responsabilidades pendientes no se eliminan automáticamente. Retención y borrado quedan abiertos en el modelo de T03, bloqueando las tablas afectadas hasta aprobarse.

### IC-05 — Sesión, MFA y revocación

**Pregunta:** ¿La API custodia la sesión de Supabase, el navegador usa una cookie opaca HttpOnly y MFA TOTP se exige a profesionales y administradores antes de acciones privadas, con revocación efectiva en la siguiente petición privada?

- **A, recomendada:** FastAPI media autenticación/renovación y custodia tokens de Supabase en un mecanismo de servidor por diseñar. Cookie opaca Secure/HttpOnly, política SameSite acordada, protección CSRF para acciones con efecto y origen permitido. Ningún cliente Auth del navegador que necesite leer esos tokens. MFA TOTP obligatorio para acceso profesional privado/administración, opcional para cliente; recuperación de factor requiere contrato separado sin bypass de soporte. Propuesta cuantificada: JWT de 15 minutos, sesión de aplicación máxima de 12 horas y 30 minutos de inactividad. Cierre/revocación bloquea la siguiente petición privada del ámbito revocado; baja de membresía se evalúa contra estado vigente sin esperar refresco JWT.
- **B:** SDK Auth en navegador y JWT hacia FastAPI; MFA y objetivos anteriores pueden conservarse. Simplifica integración cliente; tokens accesibles a JavaScript requieren controles frente a XSS y almacenamiento acordado.
- **C:** B, con revocación de sesión limitada a expiración del JWT y MFA opcional. Menos validación activa, ventana explícita de acceso residual; requiere aceptar ese riesgo y un máximo numérico.

La aprobación debe fijar transporte, persistencia, MFA/acciones protegidas, recuperación, tiempos, dispositivos y alcance de cierre (actual/todos). Los números anteriores son propuesta, no configuración aplicada. Ante imposibilidad de comprobar revocación o membresía, A propone denegar nuevas operaciones privadas; las peticiones ya iniciadas requieren comprobación en su frontera transaccional y prueba de concurrencia. Ningún mecanismo puede retirar contenido ya descargado.

Supabase documenta que cerrar sesión no invalida por sí mismo todo JWT aún vigente y describe comprobación de `session_id` contra `auth.sessions`; el mecanismo concreto de verificación activa, con privilegios mínimos, queda pendiente. Los límites nativos de duración/inactividad/número de sesiones requieren Pro; no se presupone esa función en Free ni se aprueba cambiar tier. A exige controles de sesión de aplicación revisados, sin sustituir Supabase Auth. Una cookie opaca de aplicación con tokens custodiados en API es un diseño propio, no el patrón de SDK cliente ni una capacidad demostrada de `@supabase/ssr`. [Sesiones oficiales](https://supabase.com/docs/guides/auth/sessions).

### IC-06 — Camino de datos e identidad hasta PostgreSQL

**Pregunta:** ¿Todo dato privado de negocio pasa por FastAPI, con autorización de contexto/objeto/acción y conexión PostgreSQL de privilegio mínimo, sin una segunda vía privada desde el navegador?

- **A, recomendada:** web → FastAPI → PostgreSQL para datos privados; Auth permanece Supabase. La API verifica identidad y sesión según IC-05 y consulta membresía/asignación vigente. Rol de runtime acotado, grants explícitos, RLS como defensa adicional y contexto transaccional por diseñar y probar; no usar conexión propietaria/BYPASSRLS o `service_role` universal. El transporte de identidad al contexto de base se define en T03/T05, sin asumir que `auth.uid()` existe en una conexión SQL directa.
- **B:** navegador → Data API con JWT y RLS para operaciones simples; FastAPI para lógica adicional. Exige demostrar reglas equivalentes en ambas superficies y pruebas de acceso directo que eviten saltarse la API.
- **C:** gateway Data API usado solo por FastAPI con identidad de usuario y RLS. Conserva mediación de API, añade dependencia y contrato de transacciones/RPC.

La aprobación incluye exposición de cada superficie, identidad de conexión, grants y políticas por operación. Perfil público/catalogación tendrán un contrato público separado de C06; esta decisión no publica perfiles. No desactivar RLS ni ampliar permisos para resolver errores. El proyecto vacío tiene privilegios residuales documentados: ninguna opción permite omitir revisión de privilegios de tablas, funciones, vistas, secuencias y propietarios. Grants permiten operaciones; RLS restringe filas. El cambio de exposición automática del proveedor no revoca grants existentes ni cambia permisos de conexiones PostgreSQL directas. [Seguridad de Data API](https://supabase.com/docs/guides/api/securing-your-api), [cambio oficial de exposición de tablas](https://supabase.com/changelog/45329-breaking-change-tables-not-exposed-to-data-and-graphql-api-automatically).

## Diseño propuesto

Modelo conceptual previo a tablas: `User` representa identidad; `LawyerProfile` representa presentación profesional y un estado de habilitación distinto de Auth; `ProfessionalContext` identifica práctica propia o despacho; `LawFirm` y `Office` distinguen organización y sede; `Membership` vincula usuario/contexto con estado y capacidades; `Client` es participación/ficha de una relación dentro de un contexto, opcionalmente vinculada a un usuario. `LegalRequest`, `IntakeSubmission`, `Booking`, `Consultation` y `LegalMatter` pertenecen a bloques futuros y se conservan separados. Nombres y cardinalidades son propuesta de T03, sin tablas ni contratos HTTP implementados.

Estados propuestos para discutir: identidad pendiente de confirmación/activa/restringida; alta profesional solicitada/en revisión/habilitada/rechazada/suspendida; membresía invitada/activa/suspendida/finalizada; sesión activa/expirada/revocada. Autenticación, verificación de correo, verificación profesional y membresía son estados distintos. Responsables y transiciones de verificación profesional quedan pendientes de Atención y confianza. T03 debe definir historial y retención antes de usar estos estados en esquema.

Recorridos verificables con datos sintéticos:

| Escenario | Resultado propuesto | Negativo imprescindible |
|---|---|---|
| Cliente | Registro y recuperación conforme a IC-01; ve participaciones autorizadas de sus relaciones | Cambiar ID, contexto o correo no abre relaciones de otra persona; no ve notas internas por ser cliente |
| Práctica propia | Profesional habilitado elige práctica y opera sobre relaciones asignadas y acciones permitidas | El despacho no ve fichas propias; elegir otro contexto en la petición no otorga acceso |
| Despacho | Invitación pendiente sin acceso; aceptación activa capacidades; asignación permite contenido definido | Otro miembro sin asignación no obtiene contenido si se aprueba IC-04 A; administración de miembros no lo habilita |
| Persona multifunción | Usa vista cliente o contexto profesional manteniendo identidad | Combinar funciones no suma permisos sobre un objeto fuera de la relación autorizada |
| Salida/suspensión | Se retiran facultades profesionales derivadas de la membresía; conserva práctica propia; responsables pendientes se reasignan explícitamente. Su eventual participación como cliente se reevalúa por relación y acción, separadamente | JWT anterior, pestaña abierta, ID guardado o invitación reutilizada no recuperan facultades retiradas; ser cliente no restaura privilegios profesionales y salir no niega automáticamente una participación legítima de cliente |
| Revocación/recuperación | Cierre, expiración y recuperación siguen alcance aprobado, con estados visibles y sin secretos en salidas | Sesión revocada/MFA incompleto no alcanza acciones protegidas; recuperación no da privilegios profesionales |

La API futura debe distinguir falta de autenticación, falta de autorización, MFA pendiente, contexto inválido y transición no permitida sin revelar existencia de objetos ajenos. T05 fijará errores y contrato; T06 diseñará UX accesible. Todas las comprobaciones se aplican en servidor, también si la UI ofrece solo contextos legítimos.

## Datos afectados

La entrega actual solo crea este documento público. El diseño futuro afecta identificador de usuario Auth, correo, estado de cuenta, perfiles profesionales/públicos, membresías/asignaciones, contexto propietario, relación con cliente, consentimientos versionados y eventos mínimos de autorización. Tokens, factores MFA y credenciales son material sensible de autenticación: no forman parte de perfiles, eventos, analítica o fixtures del repositorio. Datos de verificación profesional no son públicos por defecto.

T03 debe clasificar cada dato, fuente, responsable, finalidad, acceso, historial, retención/eliminación y vínculo con Auth. En particular, vincular una ficha de cliente a una cuenta requiere verificar destinatario y autorización; coincidir correos no permite fusionar ni revelar fichas entre contextos. No se ha aprobado duración de conservación de membresías, consentimientos, auditoría o perfiles, ni qué ocurre con relaciones tras eliminación de identidad. Las seis decisiones no resuelven esos vacíos; las tablas correspondientes siguen bloqueadas hasta aprobar su modelo completo. Uso de datos reales, ubicación/transferencias y obligaciones jurídicas: **LEGAL REVIEW REQUIRED**.

## Seguridad

Se conservan AGENTS.md y las reglas del plan: sin lectura de `.env`, credenciales, cookies, pantallas de claves, clientes reales o recursos de Kova. La identidad administrativa de proveedor no otorga permisos de soporte del producto. No se ejecutan MCP de proyecto, SQL o cambios remotos para este diseño.

FastAPI debe validar firma con biblioteca mantenida, algoritmo permitido, claves confiables del emisor acordado, `iss`, `aud`, `exp` y sujeto requerido. No confiar en decodificación sin verificación, URL de claves aportada por atacante o claims de membresía obsoletos. No usar `user_metadata` editable como autorización; incluso claims administrados/firmados pueden requerir consultar estado vigente. [JWT oficiales](https://supabase.com/docs/guides/auth/jwts), [RLS y metadatos](https://supabase.com/docs/guides/database/postgres/row-level-security).

MFA debe comprobarse en API/base según el camino aprobado; una pantalla de segundo factor no protege el endpoint. Supabase distingue niveles `aal1` y `aal2`; deben ligarse al contrato de acciones de IC-05 y probar recuperación/desinscripción, sin conceder permisos por el simple nivel MFA. [MFA oficial](https://supabase.com/docs/guides/auth/auth-mfa).

La autorización requiere pruebas de ID ajeno, reasignación de propietario, rol escalado, membresía revocada, sesión obsoleta y acceso directo alternativo. T02 añade amenazas de CSRF/XSS, enumeración, invitaciones, logs/bundles/caché, administración y fuga entre contextos. Las auditorías propuestas registran actor/contexto/acción/resultado y correlación mínima; contenido jurídico, correo, tokens y cookies se excluyen. Retención y acceso de eventos aún pendientes. Privilegios residuales, funciones/vistas y el rol efectivo deben probarse con roles sujetos a políticas, además de la revisión documental.

## Impacto futuro

IC-03 e IC-04 determinan propiedad y acceso para CRM, solicitudes, documentos y agenda; no deben improvisarse en cada módulo. IC-05/IC-06 determinan manejo de XSS/CSRF, observación de revocación, latencia, conexión a base y complejidad operativa. La propuesta de custodia de sesión requiere diseño de almacenamiento, rotación, renovación concurrente, fallos y operación; no es un proxy sin estado demostrado. Los controles de aplicación en Free tienen costo de desarrollo que se debe comparar con capacidades de proveedor sin contratar por inferencia.

No se habilitan pagos, IA, correo de negocio, documentos ni soporte con acceso amplio. La futura IA conserva D-019/D-020 y D-022: dos flujos revisables, sin envío automático ni OCR/embeddings. Pertenencia múltiple a despachos, transferencias y publicación profesional requieren alcance explícito posterior si no se aprueban ahora. C03 completo no se declarará terminado sin resolver y probar confianza/verificación profesional.

## Implementación propuesta

1. A0 revisa T01/T02/T03, concentra IC-01..IC-06 y registra respuestas de Arturo. Conservar pendientes parciales y excluir de implementación sus datos/flujos dependientes; no volver a preguntar D-003/D-025/D-028/D-030.
2. Completar modelo conceptual de T03 y matriz de T02 con propiedad, relaciones, estados, historial, clasificación y retención aprobados. Antes de tablas, resolver los vacíos señalados; las seis recomendaciones por sí solas no cumplen Definition of Ready.
3. Preparar contratos API/UX y estrategia de aceptación T05/T06/T07; diseñar la sesión y su persistencia sin instalar paquetes ni crear recursos mientras no estén aprobados. Dependencias, archivos, referencia común segura y revisor se asignan por A0. A3 será único escritor de migraciones locales.
4. Implementar C02 por etapas aprobadas: datos/controles locales, API/web, integración y revisión independiente. Los mocks temporales deben identificarse y no sirven como aceptación. C03 añade contextos/membresía y luego confianza bajo su checkpoint; ninguna bandera sustituye autorización.
5. Aceptación real: registro/confirmación/recuperación, sesión/MFA/expiración, negativa de acceso ajeno, cambio de contexto, salida y revocación; pruebas transaccionales concurrentes; roles efectivos y vías alternativas; revisión redactada de secretos/logs/bundles y evidencia local reproducible. Las pruebas deben fallar si se rompe el control. CI remoto, proveedor real, despliegue y restore son comprobaciones separadas, pendientes.

Verificación de esta entrega: lectura de contexto requerido y skill Supabase; contraste con documentación pública de sesiones/JWT/MFA/Data API el 2026-10-12; revisión de ocho secciones, seis IDs y alcances Approved/Implemented. El índice `https://supabase.com/changelog.md` devolvió error en la consulta; se consultó el [changelog público HTML](https://supabase.com/changelog) como alternativa. No se certifica compatibilidad de una versión o implementación inexistente; antes de implementar se deben revalidar cambios relevantes y fijar dependencias. Sin código, SQL, instalación, conexión de proyecto, secretos, pruebas de runtime, commit, push o despliegue. Revisión final de A0 pendiente.
