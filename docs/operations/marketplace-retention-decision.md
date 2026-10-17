# Marketplace C04 — decisión de conservación y acceso

2026-10-17. Estado: **Proposed / Requires Arturo**; **LEGAL REVIEW REQUIRED**.
Orden A0, rama `feature/marketplace-c03`, base `main` `a6f172c`.
Directorio/flujo aprobados según orden actual del coordinador; la retención jurídica
**no está aprobada**. Esta propuesta no reabre catálogo, búsqueda o respuesta mínima.
No modifica los plazos ya aprobados de Identity/C03 ni los extiende a C04.

## Qué hay que decidir antes de persistir solicitudes

El primer corte solo recibe descripción dirigida a un profesional/contexto;
respuesta inicial cerrada `can_continue_evaluation` / `cannot_assist` y retirada.
No intake de partes estructuradas, documentos, chat, reserva, pago o acuerdo.
No respuesta profesional todavía no implica una fecha de vencimiento, rechazo,
recordatorio o SLA. Eso no autoriza conservar su relato indefinidamente.

Propuesta: separar **acceso operativo**, **conservación restringida/bloqueo**, y
**copias de respaldo**, con finalidad y plazo propios por familia. Borrar datos
no promete deshacer una lectura o copia previa del destinatario. Mantener la
identidad del contexto no transforma a su administrador en lector del relato.

Las cifras siguientes son **alternativas de producto Proposed**, no plazos legales
obligatorios ni aprobación de conservación/supresión real. Se propone A por menor
exposición de relatos; B permite más tiempo de consulta, con mayor conservación.
No se ha emitido dictamen jurídico. La política concreta debe aprobarse y superar
la revisión de bloqueo/prescripción antes de persistir C04.

## Fuentes oficiales y límite de la recomendación

Consultada2026-10-17 la [LFPDPPP vigente de la Cámara de Diputados](https://www.diputados.gob.mx/LeyesBiblio/pdf/LFPDPPP.pdf),
última reforma DOF14-11-2025. Arts10/12: conservación relacionada con finalidad y
minimización; supresión con bloqueo cuando corresponda. Art24 vincula bloqueo con
prescripción de acciones de la relación jurídica; art25 contempla excepciones a
cancelación. Esto **no establece30/90 para las solicitudes de Legalia**. El
[decreto DOF20-03-2025](https://sidof.segob.gob.mx/notas/docFuente/5752569)
es la fuente oficial de expedición; no se usa la ley2010 abrogada como texto vigente.

Inferencia de diseño: separar fin del acceso operativo de supresión física; una
ventana comercial no determina prescripción. Revisión jurídica debe concretar
relación/finalidad, norma/plazo aplicable y datos que necesiten bloqueo, sin guardar
todo por defecto ni suprimir evidencia debida por cumplir un número de producto.
No se investigó ni certificó una prescripción universal de controversias jurídicas.

## Alternativas numéricas de producto — ninguna aprobada

Todos los días propuestos son periodos transcurridos de24h, con cálculo UTC, no
los días hábiles de un procedimiento legal. Límites para conservación ordinaria;
si procede bloqueo legal, se separa y no mantiene lectura del relato en el portal.

| Familia | A recomendada: minimización | B alternativa: revisión más prolongada |
|---|---|---|
| Descripción | Corte ordinario en el menor de30d tras respuesta inicial final/retirada y90d desde envío; sin respuesta rige90d desde envío | Menor de90d tras respuesta/retirada y180d desde envío |
| Respuesta cerrada mínima |90d desde responded_at; sin copiar relato |180d desde responded_at |
| Recibo de divulgación |90d desde submitted_at, solo versión/fecha/destinatario lógico mínimo |180d desde submitted_at |
| Idempotencia |24h de intención autenticada desde emisión servidor; recibo hasta ese mismo corte, sin reinicios | Mantener24h; ampliar conservación de contenido no justifica ampliar deduplicación |
| Auditoría sin contenido |90d desde occurred_at **como decisión nueva C04**, no herencia de Identity |180d desde occurred_at, también decisión nueva |
| Copias operativas |Edad máxima30d por copia y purga efectiva; no servicio/capacidad actual supuestos |Edad máxima90d por copia, sujeto a capacidad/costo y revisión |

Respuesta «puede continuar evaluación» cierra solo esta respuesta inicial; no
renueva el plazo del relato ni crea una relaciónC05. No se guarda otra versión de
relato en este primer corte. Si una solicitud pasa a C05, debe aprobarse tratamiento
y referencia allí; no mover contenido para eludir su corte original.

## Matriz propuesta por familia

| Familia / finalidad | Evento inicial fijo propuesto | Acceso operativo propuesto y efecto de retiro/cierre | Conservación por aprobar |
|---|---|---|---|
| Descripción enviada / evaluación dirigida | `submitted_at`; reloj máximo desde envío. Respuesta o retirada pueden iniciar ventana terminal adicional, sin reiniciar el máximo | Antes del terminal: solicitante y profesional destinatario vigente con MFA. Retirada: cesa lectura operativa profesional; solicitante ve recibo/estado. Cuenta cerrada o facultad retirada no conserva login ni acceso por pendientes | A30d terminal/máximo90d desde envío o B90d/máximo180d; decidir bloqueo/supresión según finalidad concreta, separado del plazo operativo. No duplicarlo en audit, recibos o errores |
| Respuesta mínima / comunicar siguiente paso | `responded_at`; exactamente el evento confirmado, no última lectura | Solicitante y destinatario vigente en recorrido normal. Tras retirada/cierre: recibo mínimo según política, sin relato ni facultades profesionales residuales | A90d o B180d desde respuesta y lectores autorizados posteriores; continuar evaluación no crea relación C05 ni conservación ilimitada |
| Recibo de divulgación / probar qué se presentó y a quién se compartió | Confirmación del envío con versión del texto informativo y destinatario; no timestamp del GET del aviso | Propuesta: recibo mínimo al solicitante; acceso profesional solo cuando tenga finalidad/permiso vigente. Conservación restringida no da lectura a soporte general | A90d o B180d desde envío, campos mínimos y eventual bloqueo; conservar texto informativo versionado por separado, sin una copia adicional del relato |
| Idempotencia / evitar duplicados de una intención | Commit del primer comando de esa intención; creación/respuesta/retirada tienen recibos separados | Solo servidor comprueba sujeto+operación+command_id después de autorizar. No endpoint público de recibos ni descarga de body original | Propuesta24h desde intención autenticada por servidor, regla de replay antiguo y tratamiento de resultados purgados; no deduplicación infinita |
| Auditoría mínima / trazabilidad de acción y decisión | `occurred_at` del evento confirmado; no última consulta del registro | Lector de auditoría expresamente autorizado, finalidad concreta y ámbito; admin/revisor no obtiene lectura jurídica por su cargo. Actor ya retirado no conserva lectura | Propuesta propia C04 de90d o180d, derechos/excepciones y minimización tras supresión; no heredar90d C02 ni guardar descripción, respuesta libre, email, cédula o tokens |

Los identificadores lógicos y un hash ligado a persona/contenido siguen siendo
referencias restringidas; no se llaman anónimos por quitar el nombre. Un recibo
no debe reconstruir el relato. Para huella de idempotencia, elegir representación
mínima/custodia y eliminación antes de persistir; no usar el body como log.

**Lectura del solicitante tras retirada/cierre:** la recomendación es conservar
solo estado y recibo mínimo de su propia solicitud en el periodo aprobado; no una
segunda ruta permanente al relato. Si se necesita acceso posterior al contenido,
debe aprobarse por finalidad/actor/plazo. Cerrar cuenta impide acceso autenticado;
un derecho posterior se tramita por procedimiento separado, sin reabrir sesión
ni atribuir al agente/soporte autoridad para entregar datos de terceros.

## Relojes, ausencia de respuesta y repetición

- Propuesta de cálculo: cada familia tiene inicio fijo y duración que Arturo
  elija entre alternativas o ajuste. Si hay máximo desde envío y ventana terminal,
  se aplica el vencimiento más temprano; ningún valor está activo por esta propuesta. Una nueva solicitud es otra intención
  explícita, no reapertura o extensión escondida de la anterior.
- GET, paginación, abrir una respuesta, refresh de sesión, cambio de nombre del
  profesional, retry/replay o recalcular una proyección no cambian fechas de corte.
  Una acción no-op no crea evento terminal nuevo ni mueve el plazo.
- Sin respuesta no hay TTL profesional/SLA aprobado: mantener estado submitted
  sin fingir rechazo. El máximo de conservación, cuando se apruebe, debe suprimir
  contenido aunque nadie haya respondido. Su efecto visible es «contenido ya no
  disponible» según contrato, nunca «el abogado rechazó» ni envío a otro abogado.
  Definir ese recibo/estado con UX antes de activar el vencimiento de contenido.
- Retirada impide respuesta nueva y acceso operativo dependiente; respuesta previa
  no revive tras replay. La preservación restringida de evidencia no suspende la
  retirada de facultades.
- Anti-replay propuesto para las24h: intención emitida/autenticada por servidor,
  ligada al sujeto y operación, con instante inicial y expiración inalterables;
  aceptar hasta24h desde emisión, nunca24h desde último replay. Tras el corte,
  rechazar la intención incluso si ya no existe su recibo; reconciliar listado/GET
  antes de permitir nueva intención explícita. No usar fecha aportada libremente
  por el cliente o un UUID aleatorio como prueba de antigüedad.
- El contrato actual command_id UUID por sí solo no prueba emisión/expiración.
  Hace falta aprobar su complemento autenticado y transporte privado en body,
  sin URLs/logs/cookies de analítica, antes de implementar este mecanismo. Este
  documento no instala token, endpoint o secreto nuevo. Si esa solución no se
  aprueba, mantener C04 bloqueado hasta acordar otra regla que no permita duplicar
  intención expirada; no prometer anti-replay con solo borrar recibos a24h.

## Respaldos, restauración y excepciones

Propuesta: copias aisladas con ciclo finito y acceso exclusivo para recuperación,
no búsqueda/soporte. A propone edad máxima30d de cada copia; B90d. La expiración
debe borrar efectivamente esa copia, y ninguna copia antigua debe quedar retenida
por rotación fallida. Aprobar ciclo/destino/custodio y comprobar capacidad real del
proveedor para ejecutarlo; una eliminación activa puede permanecer en copias hasta
ese máximo adicional, que debe quedar visible en la política. No afirmar borrado de backups por un DELETE,
ni que el plazo activo se cumple físicamente en todas las copias por ese comando.
No crear una réplica o servicio pagado por esta propuesta.

Tras restore, acceso y envíos permanecen cerrados mientras se reconcilian cortes,
retiros y revocaciones con evidencia privada fiable. Aplicar los cortes originales
antes de reabrir; restaurar una copia no inicia un periodo de conservación nuevo.
No volver a publicar perfiles retirados ni reactivar asignaciones o cuentas.

Excepción propuesta: conservación restringida solo por finalidad documentada,
alcance por familia/objeto, autoridad designada, motivo y fecha de revisión/fin.
No bloqueo genérico «por si hubiera disputa» ni excepción perpetua. Si se necesita
prórroga, registrar decisión justificada y próximo corte; nunca conservar acceso
operativo del profesional o retrasar cierre de cuenta. Motivos y evidencia no se
publican en repo, logs o métricas. El procedimiento y su actor no están aprobados;
requieren revisión jurídica antes de tratar contenido real.

## Tres paquetes concretos de decisión para Arturo

A0 presenta A recomendada, B alternativa o ajuste explícito; **no son respuestas
asumidas**. No se repite Identity30/90, PC-01..05 ni quién es revisorC03.

1. **Contenido y evidencia.** ¿Aprueba A: descripción30d después de respuesta o
   retirada con máximo90d desde envío; respuesta/disclosure/auditoría mínimos90d
   desde sus propios eventos; idempotencia24h con intención servidor caducable y
   rechazo posterior sin duplicados? Alternativa B:90d terminal/máximo180d y
   recibos/auditoría180d, manteniendo idempotencia24h. Son decisiones nuevas C04.
   El paquete incluye cortes/no reinicios y aviso de vencimiento sin fingir rechazo
   si no hubo respuesta; el complemento anti-replay debe revisarse en API antes
   de código. No activa supresión física legal sin resolver bloqueo aplicable.
2. **Lectores y bloqueo.** ¿Aprueba retirar inmediatamente lectura profesional al
   retirar la solicitud o facultad, dejar al solicitante solo recibo mínimo tras
   retirada durante el plazo aprobado y reservar evidencia bloqueada a responsable
   expresamente designado por finalidad? Alternativa: acceso posterior al relato
   limitado al solicitante por el plazo operativo elegido, sujeto a revisión de
   derechos de terceros. En ambas: cierre de cuenta impide login; definir actor,
   fundamento, inicio/revisión/fin del bloqueo por norma/prescripción aplicable,
   sin soporte universal ni prórroga por GET/replay. No fijar bloqueo legal30d
   automático ni conservar todo indefinidamente «por si acaso».
3. **Backups y operación.** ¿Aprueba como objetivo A máximo30d por copia con purga
   efectiva, aislamiento y filtro de retiros/cortes antes de reabrir tras restore,
   y asignar un responsable de operación/fallos? B sería máximo90d por copia con
   el mismo control, si lo justifican recuperación y costo. Verificar factibilidad
   del proveedor antes de apertura; no afirma backups contratados ni añade gasto.
   La frecuencia/ejecutor y alertas deberán concretarse sin dar días de demora
   implícitos; si no puede cumplirse, posponer tratamiento real en vez de simularlo.

## Condición de implementación y aceptación

Directorio público y dominio puro C03 autorizado pueden avanzar sin almacenar
solicitudes. La aceptación del flujo de C04 no autoriza elegir sus plazos; antes
de tablas/endpoints operativos deben quedar llenas y aprobadas las casillas de
inicio, duración, lector, supresión, excepción y respaldo de cada familia afectada.
Código sintético local ya aprobado no necesita una certificación jurídica global;
tratamiento real y afirmaciones profesionales conservan sus puertas específicas.

Negativos verificables posteriores: GET/replay no reinicia corte; ausencia de
respuesta no conserva relato perpetuo; retiro concurrente niega respuesta; antiguo
profesional/admin no lee relato retirado; idempotencia expirada no duplica envío;
ninguna cascada elimina evidencia aún legítimamente vigente; evidencia caducada
no sobrevive por FK; error parcial no se informa como cumplimiento; restore no
resucita acceso/contenido; bloqueo sin autoridad/motivo/fin se rechaza; logs no
contienen relato/identificadores privados. Pruebas solo con fixtures sintéticos.

Fuentes de alcance: [C04](../checkpoints/c04-requests-conflicts.md),
[corte marketplace](../checkpoints/marketplace-first-slice.md),
[API propuesta](../contracts/marketplace-first-api.md),
[retención C02/C03](legalia-coordinated-retention.md).
Investigación oficial y revisión documental; no implementación, SQL, pruebas funcionales, acceso remoto,
secretos, permisos o dictamen jurídico. A0 conserva integración y publicación.
