# Primer corte marketplace — disponibilidad y puertas mínimas

2026-10-16. A3, orden de A0; referencia común `7b88b4e`, rama
`codex/identity-design`. Prioridad expresa de Arturo: **catálogo → búsqueda →
solicitud dirigida**, sin reservas ni pagos. El [complemento del checkpoint](../checkpoints/marketplace-first-slice.md)
y el [contrato API propuesto](../contracts/marketplace-first-api.md) concretan la tanda.
Esta selección fija recorrido y orden;
no resuelve silenciosamente taxonomía, permisos nuevos, datos, retención o reglas
profesionales. No se repite el roadmap completo.

## Resultado de la revisión

La infraestructura y el borrador profesional son una base reutilizable; **todavía
no existe una oferta profesional publicable ni una API de catálogo o solicitudes**.
La ausencia de reservas/pagos no bloquea diseñar un directorio que termina en una
solicitud de evaluación. Debe decir qué se solicita y evitar prometer consulta,
contratación o atención urgente confirmadas.

Se puede avanzar localmente en C03 ya aprobado, con datos sintéticos y gates
cerrados, sin volver a pedir PC-01..PC-05/D-041. No se puede publicar perfiles,
conceder un revisor real o persistir contenido C04 apoyándose solo en esta orden.
La apertura real depende de pruebas C02 y de cerrar procedimiento/datos concretos
pendientes. **LEGAL REVIEW REQUIRED** para confianza, divulgación y conservación.

## Matriz de disponible y pendiente

| Pieza mínima | Disponible en código o evidencia | Pendiente para este corte |
|---|---|---|
| Transporte web/API | Worker con destino API exacto, no-store privado y bypass solo assets públicos; hosting ya publicado | Añadir/verificar rutas reales nuevas sin fallback falso; no cambiar plan Free o permisos |
| Identidad cliente | Registro/acceso/recuperación y sesión custodiada; validación activa y CSRF implementados | Cuenta APP confirmada, entrega OTP/recuperación, MFA/revocación reales y operación de retención/restore; no confundir pruebas mock con aceptación |
| Alta profesional privada | `ProfessionalService.execute` requiere aal2 y unidad de negocio Identity; read/create/edit/withdraw propios | No es habilitación profesional; el esquema C03 sigue sin aplicación remota según evidencia vigente |
| Perfil/contexto | `Profile` solo draft/withdrawn; `Practice` preparing/closed; `view` fuerza publication private/review null/capabilities vacías | Declaración, solicitud/revisión, habilitación, activación y publicación voluntaria reales |
| Revisión C03 | PC-02/D-040 y revisor limitado D-041 aprobados conceptualmente | Procedimiento de cotejo/titularidad/suplantación, recursos, revisor alterno, almacenamiento exacto e implementación; no capacidad real concedida |
| Publicación | Router mantiene submit/publication/activate/review en FEATURE_UNAVAILABLE y tests verifican no efectos | Proyección permitida, consentimiento/publicación separados de revisión, versión de lo revisado y retiro/invalidation; nunca exponer el draft directamente |
| Catálogo editorial | Propuesta C06 de área/situación/jurisdicción/modalidad | Taxonomía/cobertura inicial y editor/capacidad, campos/historia/retención aprobados; no ciudad o especialidad elegida |
| Búsqueda | Modelo de filtros/paginación/orden propuesto C06 | API/UI y proyección seguras; orden y semántica de filtros aprobados, límites concretos, estado vacío y retiro vigente; no matching por relato |
| Destinatario C04 | Modelo LegalRequest→contexto/profesional y versiones de intake propuesto | Campos y divulgación exactos, fuente de elegibilidad vigente, ciclo/respuesta/retirada y retención por familia aprobados; no bandeja universal |
| Operación limitada | Arturo ya responsable retiro/fallos30/90; C17 delimita facultades | Procedimiento de revisión/quejas/no respuesta; autoridad mínima por acción sin contenido jurídico universal |

«Disponible» se deriva de lectura estática y evidencia existente; esta auditoría
no ejecuta red, SQL, fixtures ni pruebas de producción.

## Evidencia concreta de código

- [Dominio C03](../../apps/api/src/abogalia_api/professional_contexts/domain.py):
  `DraftFields` acepta solo display_name/declared_area; agregado valida pareja
  draft/preparing o withdrawn/closed. Lectura/no-op no reinician30d; eventos90d.
  No hay cédula, resultado de revisión o permiso profesional en este agregado.
- [Servicio](../../apps/api/src/abogalia_api/professional_contexts/service.py):
  `view` no publica ni habilita; `execute` usa
  `identity.authenticated(touch=True, business=True)` y exige aal2.
- [Router](../../apps/api/src/abogalia_api/professional_contexts/router.py):
  read/create/edit/withdraw y listado propio; body estricto hasta8KiB, CSRF/origen,
  rechazo Authorization, no-store. Catchall gated no representa una función hecha.
- [Storage](../../apps/api/src/abogalia_api/professional_contexts/storage.py):
  usa conexión de Identity, sujeto transaccional verificado, rol runtime exacto,
  locks y versiones; no DSN/conexión/commit independientes. La consulta amplia de
  la fila privada no es una proyección pública reutilizable.
- [Frontera Identity](../../apps/api/src/abogalia_api/identity/service.py):
  `authenticated` valida sesión al inicio y frontera; negocio en savepoint, rollback
  ante revocación/fallo sin perder custodia renovada. No reemplazar con claims JWT.
- [Cliente C03](../../apps/web/app/lib/professional-contexts.ts): parser acepta solo
  publication private/review null/capabilities vacías. [Rutas](../../apps/web/app/routes.ts)
  solo incluyen home/Auth/cuenta y profesional privado; no catálogo/búsqueda/solicitud.
- [Tests API C03](../../apps/api/tests/test_professional_contexts_api.py):
  `test_future_families_not_fake_enabled`, actor ajeno, MFA y rollback de frontera
  son restricciones deliberadas; no borrarlas para conseguir una pantalla positiva.
- [Tests storage](../../apps/api/tests/test_professional_contexts_storage.py): rol,
  sujeto, conexión reutilizada, CAS, concurrencia, retención y cuenta cerrada.
  Leídos, no ejecutados de nuevo en esta revisión.

## Orden mínimo que conserva el recorrido elegido

1. **Resolver el paquete concreto marketplace C06/C04.** Mantener prioridad y
   excluir reservas/pagos. A0 registra modelo por dato, alcance de catálogo,
   filtros/orden, destinatario, divulgación y plazos jurídicos aún pendientes.
   Seleccionar secuencia no equivale a aprobar cada campo o valor propuesto.
2. **Completar confianza/publicación mínima C03 en paralelo a C02.** Para una
   primera oferta no hace falta completar sedes o todo el despacho si el corte
   aprobado se limita a práctica propia; esa limitación es una opción a ratificar,
   no exclusión automática de despachos. Separar declarado, revisado, habilitado,
   contexto activo y publicación voluntaria. Ningún dato privado se publica por
   tener perfil o ser administrador.
3. **Catálogo de oferta elegible.** Implementar solo después del contrato aprobado
   una proyección pública de campos explícitos; lista/ficha/estado vacío. El
   complemento propone empezar con nombre/ámbito declarado; no exigir taxonomías
   nuevas como dependencia artificial de esa variante mínima. No hay
   proveedores ficticios ni profesionales reales de prueba publicados. El registro
   revisado tiene alcance preciso; no sello de especialidad/identidad no comprobada.
4. **Búsqueda sobre esa proyección.** Variante mínima recomendada: nombre/ámbito
   declarado, texto público acotado y validado según contrato por aprobar, paginación
   limitada y orden explicado. Códigos de área/jurisdicción/modalidad son una
   variante posterior si requiere atributos nuevos; no puertas universales del
   primer directorio. Sin relato jurídico libre en query, ranking pagado, reseñas
   o datos privados. Conjunto vacío no relaja criterios ni anuncia oferta inexistente.
5. **Solicitud dirigida.** Usuario confirmado elige profesional/contexto vigentes,
   revisa qué versión comparte y confirma. Una referencia pública debe identificar
   destinatario/contexto sin publicar IDs privados; la etiqueta visible de práctica/
   despacho requiere proyección aprobada. Revalidación de elegibilidad al envío
   y en commit; crear solicitud no crea reserva, relación de servicio o cargo.
   Respuesta/aclaración/retirada tienen estado y siguiente paso, sin contratar.
6. **Aceptar el corte real.** Cuenta controlada, profesionales habilitados mediante
   proceso aprobado, pruebas integradas de permisos/retiro/concurrencia y operación
   de datos. Sin dominio, Resend sigue restringido al destinatario de su remitente
   de prueba; un marketplace abierto requiere resolver onboarding/correo real.
   No renovar automáticamente el presupuesto de ensayo ni hacer envíos a terceros.

No exigir C05 completo para enviar una solicitud de evaluación, ni construir C07
como dependencia falsa del directorio. Si el texto comercial promete contratar o
consultar en este corte, entonces C05/C07 sí necesitan su propio alcance aprobado;
la solución es ajustar la promesa al recorrido elegido, sin simular capacidades.

## Trabajo local C03 ya aprobado que puede continuar

**Sí**, bajo nueva orden de archivos del coordinador, puede avanzarse en la
implementación local de invariantes de PC-01..05/D-041 sin volver a decidir sus
opciones. Esta orden A3 es de lectura/documentación y no modifica código.

| Paquete local propuesto | Archivos candidatos para asignación A0 | Criterio y límite |
|---|---|---|
| Revisar contratos/modelo para el siguiente incremento | `docs/contracts/professional-contexts-api.md`, `docs/data/professional-context-schema.md`, `docs/security/professional-context-access.md` | Reconciliar campos, versión, actores, referencias, clasificación y30/90 aprobados; procedimiento/titularidad pendientes visibles; no SQL por transformar propuestas en tablas |
| Máquina de estados profesional y proyección mínima pura | `apps/api/src/abogalia_api/professional_contexts/domain.py`, `apps/api/tests/test_professional_contexts_domain.py` | Implementar/incrementar reglas ya aprobadas con fixtures, sin un «enabled» libre que el cliente pueda imponer. Revisado ≠ publicado; cambio relevante invalida revisión; self-review prohibida. Esquema exacto de evidencia y procedimiento no se inventan |
| Pruebas de gates y frontera antes de abrir funciones | `apps/api/tests/test_professional_contexts_api.py`, `apps/api/tests/test_professional_contexts_storage.py` | Conservar FEATURE_UNAVAILABLE hasta dependencias satisfechas; demostrar que el agregado actual no aparece público ni concede capacidades; rollback/CAS/aal2 y aislamiento se mantienen |
| Preparar contrato privado de UI según estados ya aprobados | `apps/web/app/lib/professional-contexts.ts`, `apps/web/app/components/professional-draft.tsx` | Solo después de contrato revisado; no mostrar acciones operables que servidor no tenga. Mantener parser cerrado del incremento actual o versionar claramente el nuevo; no aceptar cualquier state/capability para evitar errores |

Cambiar router/service/storage para una familia nueva requiere modelo específico
reconciliado, matriz revisada y criterios de entrada satisfechos. No habilitar submit
si nadie puede revisar conforme al procedimiento; no otorgar a Arturo permisos
reales por una fixture. Migraciones tienen responsable único y revisión independiente;
esta auditoría no autoriza aplicarlas o ampliar runtime/owner. Puede prepararse
implementación sintética aprobada con gates reales cerrados mientras se resuelven
aceptación humana C02 y procedimiento jurídico, sin declarar producción lista.

## Negativos obligatorios antes del primer corte

| Caso | Resultado exigido |
|---|---|
| Borrador, no revisado, suspendido o publicación desmarcada | Ausente en lista/ficha/búsqueda y no elegible para nueva solicitud; no revelar motivo interno al público |
| Revisor intenta autoaprobarse o actor aporta enabled/capability/owner | Denegación sin transición, evento de éxito falso ni eco de datos |
| Cambia nombre/cédula relevante después de revisión | Revisión anterior insuficiente; no mantener publicación/habilitación como si nada cambió |
| Admin/revisor sin participación solicita relato o audit jurídico | Denegación uniforme; autoridad administrativa no lee solicitudes |
| Perfil retirado entre resultado de búsqueda y envío | Revalidación rechaza envío; no queda contenido entregado a destinatario inelegible |
| Suspendido/salida/revocación durante operación privada | Rechazo en frontera y rollback de negocio; no acceso residual por pestaña/JWT/selector |
| Solicitante cambia profesional/contexto en body/URL, usa ID ajeno | No cruce de ámbito ni enumeración; destinatario debe coincidir con objeto y permiso vigente |
| Doble envío o respuesta perdida | Reconciliación/idempotencia según contrato; no dos solicitudes ni reintento automático a otro destinatario |
| Aclaración cambia intake después de revisión | Revisión queda ligada a versión anterior; no usarla como evaluación vigente |
| Retirada vs evaluación concurrentes | Resultado transaccional consistente; retirada terminal no reabre ni entrega contenido nuevo |
| Relato jurídico libre, parámetros desconocidos/no permitidos, cursor alterado o XSS en nombre/área | Rechazo/escape y límites; permitir búsqueda acotada de nombre/ámbito si se aprueba, sin relato en URL/logs ni payload público inesperado |
| Resultado incluye email/cédula completa/dato interno | Test de allowlist falla; serialización servidor nunca depende de ocultar en React |
| Caché/build/restore conserva perfil retirado | No resurrección pública; política de retiro aplicada a cada proyección y datos restaurados |
| Cuenta cerrada o faltan tablasC03 al mantenimiento | No login/reactivación ni purga fingida; estado fijo de bloqueo, sin owner/bypass/cascade improvisados |
| Error/timeout/429 de Auth o almacenamiento | Fallo cerrado, no fallback JWT ni excepción cruda; ninguna afirmación de entrega/revocación por timeout |

## Límites operativos de apertura

Cloudflare sigue Free; una VM/un proceso Fly continúa. Logs/traces OFF, checker
público a demanda sin alertas o histórico. Reusar estos componentes no habilita
monitorización de búsquedas ni relatos.30/90 Identity/C03 no aprueban retención
C04 o nuevos eventosC06. Runtime mínimo y RLS/FORCE se mantienen; no service_role
universal ni SQL Auth para evitar resolver el contrato D-039.

Pendientes reales C02: correo/OTP, MFA y revocación proveedor e integrada, evidencia
fiable de retiro, mantenimiento/alertas y restore. Pueden diseñarse/probarse piezas
locales C03/C06/C04 autorizadas sin afirmar resueltos esos controles de apertura.
No volver a solicitar publishable ni reinstalar hosting; son base ya configurada.

## Evidencia y comprobación de esta entrega

Leídos README, plan vigente, decisiones, C03/C04/C06 y contratos/datos C03; revisión
estática de dominio/router/service/storage, frontera Identity, cliente/rutas y tests
no sensibles. Skills Supabase/Workers previamente leídas se conservan como contexto;
no se implementó proveedor, API o SQL nuevo y no se emitieron claims de límites
cambiantes más allá del estado aprobado/documentado del proyecto.

Se creó exclusivamente este documento; enlaces locales comprobados. Sin .env,
secretos, datos reales, SQL ejecutado, acceso remoto, permisos, commits, dependencias,
pruebas funcionales nuevas ni agentes hijos. A0 revisa decisiones y asigna cualquier
implementación posterior con archivos propios y revisor independiente.
