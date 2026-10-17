# Primer flujo marketplace — Catálogo → búsqueda → solicitud dirigida

Fecha: 2026-10-16. Referencia común `7b88b4e`; rama `codex/identity-design`.
Orden A1: este archivo exclusivamente, revisión A0/A2. **Propuesta UX verificable**;
no modifica checkpoints ni convierte nuevos datos/permisos en decisiones aprobadas.

## Alcance y autoridad

Arturo priorizó este orden exacto: catálogo, búsqueda y solicitud dirigida a un
profesional. Reservas y pagos no son dependencias de ese recorrido; tampoco exige
contratación C05, consulta ficticia, suscripción o IA para poder solicitar atención.
La recomendación anterior de empezar por atención directa C04/C05 no controla esta
nueva tanda. El coordinador registra la instrucción y actualiza los índices.

Se reutilizan D-016 (búsqueda gratuita), D-031 (contexto propietario y autorización
por objeto), D-040 (revisión profesional, publicación separada y voluntaria) y
D-041 (capacidades de revisión/cierre acotadas). No se pregunta otra vez si un
profesional desea publicar ni se habilita publicación por guardar un borrador.

Fuentes: [plan](../27_development_plan_agents.md), [decisiones](../decisions/decision-log.md),
[C03](../checkpoints/professional-contexts.md), [UX C03](professional-contexts-flows.md),
[C04](../checkpoints/c04-requests-conflicts.md), [C06](../checkpoints/c06-discovery-catalog.md).
Aprobación de prioridad no aprueba automáticamente taxonomía, orden, nuevos campos,
formulario, retención o matriz de destinatarios. No se usa marca piloto.

## Recorrido propuesto por pantalla

Los nombres de ruta son candidatos para el contrato, no rutas ya existentes.

| Paso | Qué ve/hace la persona | Respuesta verificable y límite |
|---|---|---|
| 1. Catálogo público (`/profesionales`) | Explicación breve: buscar es gratuito; elegir profesional permite solicitar evaluación, no contratar. Proyecciones públicas con nombre y ámbito declarado; ayudas para buscar solo por esos campos. Botón «Ver profesionales» | Sin login para explorar. Catálogo orienta; no clasifica jurídicamente ni promete oferta en todo México. Sin términos de búsqueda muestra la lista alfabética elegible, sin adjudicar área |
| 2. Resultados | Busca por nombre de presentación y/o ámbito declarado; lista paginada y orden explicado. Cada tarjeta muestra nombre de presentación, área declarada y contexto destinatario publicable | Solo proyecciones voluntariamente publicadas, perfil habilitado y contexto elegible. Resultado no declara compatibilidad individual ni ausencia de conflicto |
| 3. Ficha profesional (`/profesionales/:publicId`) | Alcance del cotejo real con fecha, campos declarados distinguidos y contexto exacto que recibiría una solicitud. Acción «Solicitar evaluación de atención» | No «Reservar», «Pagar» o «Contratar». Si no existe servicio/precio aprobado, no simular consulta, tarifa, disponibilidad ni presupuesto |
| 4. Identificarse | Si falta sesión, acceso/registro C02 existente. Al volver, confirmar mismo destinatario/contexto antes de mostrar formulario | Solo destino interno público permitido; sin relato, token, email o contraseña en URL. No redirigir por un fallo503 como si fuera logout |
| 5. Solicitud privada | Encabezado permanente con profesional y contexto; campos mínimos y explicación de audiencia. Botón «Revisar solicitud» | Sin archivos, contraparte, identificaciones o datos fiscales en este primer formulario. No enviar al cambiar filtros, identificar cuenta o escribir |
| 6. Revisar y enviar | Vista previa de datos, destinatario y propósito; enlace para corregir. Acción inequívoca «Enviar solicitud a este profesional» | Confirmación explícita, sin casilla premarcada ni aceptación de contratación. El texto informativo/recibo versionados necesitan revisión, no un consentimiento universal |
| 7. Resultado y estado | Acuse con fecha y estado «Enviada; pendiente de revisión», profesional/contexto y acción «Ver solicitud» / «Retirar solicitud» según estado | Acuse de recepción no cuenta como respuesta útil. No prometer plazo numérico, lectura, aceptación, reserva o entrega de correo; no pago previo |
| 8. Respuesta dirigida | Solicitante consulta respuesta estandarizada o retirada; profesional autorizado responde con MFA | Solo destinatario concreto del contexto, sin bandeja jurídica general del despacho, correo de negocio automático ni reenvío a otros profesionales |

## Proyección pública y búsqueda mínima propuestas

La opción recomendada usa solamente nombre de presentación, ámbito declarado y
alcance/fecha reales de cotejo, ya contemplados por C03, más etiqueta pública del
contexto receptor como extensión propuesta. No introduce taxonomía nacional,
jurisdicción, modalidad, servicio, precio o disponibilidad. Esas extensiones no
bloquean el recorrido elegido y necesitan aprobación propia antes de capturarse.
No hacer públicos cédula completa, email, nombre legal privado, User ID, revisor,
membresías completas, historia, domicilio o documentos. No «identidad verificada»
ni «especialista certificado» a partir de una declaración. Sin procedimiento y
actor reales no se inventa sello/fecha.

Se propone resultado/ficha por proyección **profesional + contexto receptor**,
identificada por public_id opaco ligado inmutablemente a esa combinación. Cambiar
contexto exige nueva proyección, no redirigir solicitudes de un public_id existente.
La etiqueta pública del contexto (public_context_label,1..120 caracteres propuestos) es un dato nuevo propuesto: el
controlador autorizado debe aprobar expresamente el texto y publicación; no usar
el nombre privado del despacho por inferencia. Solicitud/confirmación muestran
nombre profesional y esa etiqueta, sin exponer IDs internos de contexto o membresías.
Cada combinación conserva retirada independiente; public_id no porta autorización.

| Campo/control | Parámetro recomendado por aprobar | Ausencia/ambigüedad |
|---|---|---|
| Nombre de presentación | Búsqueda textual sobre display_name público,1..80 caracteres normalizados | Campo vacío elimina ese criterio; no búsqueda sobre nombre legal, email o usuarios privados |
| Ámbito declarado | Búsqueda textual sobre declared_area público,1..80 caracteres; máximo80 entre ambos campos | Texto libre declarado, no categoría oficial ni especialidad certificada; no exigirlo si el visitante no sabe qué buscar |
| Ayuda de búsqueda | «Escribe solo el nombre de un profesional o un ámbito declarado; no describas tu situación aquí» | No garantiza ausencia de datos sensibles en input; no persistir consultas/historial en aplicación, ni enviarlos a telemetría |
| Orden | Nombre de presentación normalizado y public_id estable como desempate; rótulo «Orden alfabético» | Sin ranking de calidad, pago, popularidad o aleatoriedad encubierta |
| Paginación |20 resultados por defecto, máximo50; cursor opaco revisado por API | Lista vacía honesta; no traer resultados de otro filtro para rellenar |

Semántica propuesta: coincidencia textual acotada sobre cada campo público, insensible
a mayúsculas; si se usan ambos, intersección de ambos criterios. No búsquedas sobre
relatos, sinónimos jurídicos inferidos, ubicación ni áreas privadas. A4 fija Unicode/
colación y escape con ejemplos sintéticos antes de implementar. Texto desconocido
produce lista vacía, no diagnóstico ni reclasificación jurídica. No identificar
profesionales por domicilio o inferir jurisdicción de declared_area.

Búsqueda con texto puede recibir información sensible aunque se instruya lo contrario:
no reflejar input en errores, logs o analytics ni persistir en aplicación. Recomendar
mantener estos términos solo en memoria del formulario y transporte API público
revisado; si GET usa query, navegador/red/proveedor pueden tener rastros y el contrato
debe reconocerlo. No declarar anonimato o ausencia total de huella. Si se requiere
eliminar ese riesgo de URLs, evaluar transporte de búsqueda separado antes de código.
No matching sobre relato, favoritos, fingerprint o historial personalizado en este corte.

## Formulario dirigido: campos mínimos propuestos

Las cifras de longitud siguientes son límites de UX **propuestos**, no retención,
regla jurídica ni contrato aprobado. A0 coordina su compatibilidad con A2/A3/A4.

| Campo | Obligatoriedad propuesta | Regla y finalidad |
|---|---|---|
| Destinatario/contexto | Obligatorio, seleccionado desde ficha; no editable como UUID libre | public_id+expected_listing_version; API resuelve profesional/contexto elegible. Mostrar nombre y etiqueta pública en formulario y confirmación |
| Descripción breve | Obligatoria;1..2000 caracteres tras normalización Unicode y recorte exterior; cuerpo JSON máximo8192 bytes, propuestas por aprobar | Explicar qué necesita sin identificaciones, archivos, contraseñas o nombres de terceros. Texto plano, rechazar vacío; no repetir input en errores/logs ni sustituir original con IA |
| Información de divulgación | Texto versionado y acción explícita de envío | disclosure_version+disclosure_acknowledged:true. Explica audiencia/finalidad revisadas; no contrato profesional ni consentimiento universal |
| Identificador del comando | Generado por cliente al confirmar una intención de envío; no campo de usuario | command_id UUID en JSON, no token de acceso ni nuevo header del proxy; reutilizar para reconciliar un mismo envío |

Área orientativa, jurisdicción y modalidad **no forman parte del primer cuerpo de
envío recomendado**: no copiar texto del buscador como relato o asumir que un filtro
expresa jurisdicción del asunto. Extensiones posteriores requieren datos/contrato
aprobados. El destinatario podrá determinar si puede continuar la evaluación sin
que Legalia recabe partes o documente una consulta en este corte.

No solicitar de nuevo nombre/email/teléfono que no son necesarios para este corte;
la identidad confirmada se usa por el contrato C02, no se publica ni se entrega como
contacto libre por inferencia. No fecha procesal/urgencia clínica, CURP/RFC, cédula,
partes/contrapartes, documentos, cantidad a pagar o cuenta bancaria. Si el usuario
incluye información sensible en texto libre, la ayuda no garantiza su ausencia;
clasificar el texto como confidencial, sin analítica, y tratarlo según política C04.
Una fase posterior de partes/conflicto requiere campos/finalidad revisados propios;
no añadirla como formulario obligatorio oculto en esta entrega.

## Estado privado y acciones del profesional

Estados privados del contrato propuesto: submitted (enviada), responded (respuesta
registrada) y withdrawn (retirada). El borrador anterior existe solo en memoria;
no fila persistida ni estado jurídico servidor. No under_review inferido al abrir
un GET, aclaración, aceptación contractual o acuerdo automático.

Bandeja del profesional: solo solicitudes dirigidas a su identidad habilitada en
el contexto vigente y con MFA; abrir y responder exigen autorización actual. Comando
explícito de respuesta sobre expected_version y command_id, con uno de dos outcomes:

- can_continue_evaluation: «Puede continuar la evaluación contigo». No contrato, confirmación
  definitiva de conflicto, reserva, precio o garantía de atención.
- cannot_assist: «No puede atender esta solicitud». No expone razón privada, conflicto
  con otro cliente o evaluación del mérito jurídico; no penalización automática.

Respuesta sin texto libre profesional ni intake ampliado; la interfaz muestra el
resultado y su alcance, sin prometer seguimiento que el corte no permita. Cliente
puede retirar según estado/lectura aprobados. Retirada impide respuesta posterior;
la carrera respuesta/retirada se resuelve por versión y autorización transaccional.
No elegir tiempo de respuesta, vencimiento, sanción, recordatorio o escalado sin decisión.

## Vacíos, retirada y cambios de contexto

| Escenario | Texto/comportamiento propuesto | Qué verificar |
|---|---|---|
| Catálogo aún sin oferta publicada | «Todavía no hay profesionales publicados para consultar». No tarjetas inventadas, falsa carga o enlace de reserva | Consulta pública vacía sin exponer perfiles en revisión; no exigir registro para descubrir que no hay oferta |
| Búsqueda sin coincidencias | «No hay opciones publicadas con estos criterios». Mostrar criterios activos y «Cambiar búsqueda»/«Ver todas» expresos | No relajar los criterios silenciosamente ni prometer captación; referencias institucionales solo si revisadas |
| Oferta temporalmente inaccesible | Mensaje de indisponibilidad y reintento manual | Fallo503 no se transforma en cero profesionales ni en logout |
| Publicación retirada/suspendida tras cargar tarjeta | Ficha/acción consulta estado actual; «Este perfil ya no está disponible para nuevas solicitudes» | No mostrar datos retirados desde caché, historial, índice o build; error público no revela causa privada |
| Contexto receptor deja de estar activo antes de enviar | Bloquear envío, conservar texto solo en memoria de la misma sesión mientras el usuario decide descartarlo | API no entrega ni crea solicitud; no cambiar a práctica propia del mismo abogado para rescatar envío |
| Solicitante cambia profesional antes de enviar | Informar que contenido pertenece al borrador anterior; recomendar descartar y abrir formulario vacío | No copiar ni reenviar relato sin nueva acción explícita; el primer corte no incluye transferencia de borrador |
| Profesional cambia contexto en su selector | Cerrar vista privada anterior y pedir lista actual del nuevo; si hay selección de respuesta aún sin confirmar, confirmar descarte local | Respuesta tardía del contexto anterior no se dibuja en nuevo; no cambia propiedad/asignación de solicitudes |
| Profesional pierde vínculo/capacidad | Ocultar contenido del ámbito retirado y detener comandos; cliente ve estado genérico de destinatario no disponible | No acceso residual por pestaña/MFA anterior ni traslado automático de solicitud al administrador/suplente |
| Solicitante confirma retirada | Explicar «No se enviarán nuevas acciones de revisión; la información ya compartida sigue su política de conservación». Mostrar estado real | No prometer borrado inmediato, desaparición de copias conocidas o retirada de memoria profesional |
| Timeout tras enviar/retirar | «No pudimos confirmar el resultado; comprueba el estado antes de repetir» | Reconciliar comando propio con clave idempotente; no reenvío automático ni duplicación por doble click |
| Sesión confirmadamente revocada/otra cuenta entra | Vaciar contenido privado y borradores en memoria; autenticar de nuevo | No persistencia localStorage/sessionStorage, URL, cache API ni restauración de texto a otro usuario |

## Accesibilidad y manejo de datos

Labels visibles, instrucciones enlazadas, teclado completo, foco al resumen de error,
éxitos anunciados con role=status y errores con role=alert sin eco del contenido.
Contador de longitud local no envía pulsaciones. Profesional/contexto siguen visibles
al revisar, no dependientes solo de color o un selector oculto. No búsqueda por mapa,
domicilio exacto, calendario, CAPTCHA o nuevo proveedor introducidos por esta UX.

Términos de búsqueda pública solo usan el transporte revisado y su riesgo documentado;
nunca incluir texto jurídico, borrador, IDs de cliente o credenciales en navegación.
La acción de acceso conserva solo un destino interno público permitido. Borrador
inicial en memoria de la pestaña y sin autosave persistente recomendado: si se cierra
la página puede perderse, y la UI debe decirlo. Logout/revocación elimina memoria.
Persistir borrador en servidor necesita modelo/retención aprobados; escribirlo en
browser storage no es una alternativa de privacidad automática.

Envío requiere API FastAPI con CSRF/sesión vigente, versión de destinatario/proyección
y comando idempotente; la UI no elige roles ni confía en parámetros públicos para
acceso. La serialización compartida no incluye notas internas/administración.
No destinatarios, relato, IDs de solicitud, filtros personales o partes en telemetría,
logs, errores crudos, notificaciones externas o eventos Cloudflare. Retención C04
se resuelve en su modelo por familia; no inventar30/90d desde UX.

## Decisiones nuevas sugeridas para Arturo

A0 consolida **tres paquetes globales: directorio, solicitud y retención**. Este
archivo concreta los dos primeros y remite la retención al modelo/checkpoint;
no agrega una cuarta sesión ni pide otra vez la prioridad o publicación voluntaria.
Ninguno de estos parámetros nuevos queda aprobado por esta propuesta.

| Paquete | Recomendación concreta | Alternativa y consecuencia |
|---|---|---|
| MF-DIR / directorio | Campos C03 públicos, etiqueta pública autorizada del contexto y proyección profesional+contexto; búsqueda nombre/ámbito1..80 cada uno, máximo80 combinado,20 resultados/máximo50, orden alfabético estable. Sin taxonomía, jurisdicción, modalidad, precio ni historial persistido | Solo catálogo de proyecciones y lista alfabética sin campos de búsqueda; permite explorar pero recorta la búsqueda elegida. Si se quieren filtros territoriales/modalidad, aprobar esos datos como extensión explícita |
| MF-REQ / solicitud | Cuenta confirmada con controles cliente C02, sin imponer MFA profesional al cliente; receptor exacto/publicación vigente, descripción1..2000/body8192, revisión y envío explícitos, solo memoria previa, respuesta can_continue_evaluation/cannot_assist y retirada idempotentes. Sin correo automático/plazo prometido ni traslados | Limitar por ahora catálogo/búsqueda mientras se aprueban permisos/datos de solicitud. No mostrar botón de enviar aparente ni un acuse como atención útil |
| Retención / coordinado por A0 | Aprobar modelo, política por familia, lectura tras retirada, recibos/idempotencia y restauración antes de tablas; números pertenecen al paquete C04, no se fijan desde UX | Sin ese contrato solo diseño y trabajo local que ya tenga aprobación aplicable; no persistir relato en servidor/browser storage para sortear el gate |

La etiqueta pública de contexto y recepción expresa de solicitudes son extensiones
por aprobar, no una repetición de publicación voluntaria C03. El solicitante no
necesita crear perfil profesional; nivel de assurance cliente debe quedar expreso
al aprobar MF-REQ. Jurisdicción/modalidad/áreas editoriales se aplazan en el corte
recomendado; no presentar sus campos vacíos como cobertura nacional disponible.

## Criterios de aceptación para la siguiente orden

1. Visitante anónimo completa catálogo→búsqueda→ficha sin credenciales y encuentra
   solo campos publicados; resultado vacío/503/retirada son distinguibles sin datos privados.
2. La misma persona profesional en dos contextos no mezcla destinatario, texto o
   permisos; selección visible coincide con contexto verificado en el commit de envío.
3. Acceso/registro no recibe relato en URL/storage ni lo recupera bajo otra cuenta.
   Cuenta cliente confirmada puede solicitar según política; no exigir MFA profesional
   al visitante por el hecho de buscar o actuar como cliente.
4. Vista previa confirma contenido/destinatario sin crear solicitud todavía; enviar
   una vez crea un objeto y un recibo mínimo, con reintentos reconciliados sin duplicar.
5. Retiro de publicación/capacidad/contexto entre ficha y envío bloquea nueva entrega;
   tras envío, pérdida de acceso del profesional bloquea lectura/acción, sin reenviar
   datos o destruir unilateralmente la evidencia del solicitante.
6. Administrador, revisor de profesionales y miembro no asignado no ven solicitudes;
   objeto ajeno y objeto inexistente no se distinguen; cada respuesta respeta audiencia.
7. Cliente retira y una acción profesional concurrente no ignora versión/estado;
   respuesta estandarizada no edita relato ni lo sustituye con resumen IA.
8. Teclado/lector de pantalla completan búsqueda/formulario/confirmación y estados
   de error; validación/error/log no repite relato ni identidad privada.
9. Capturas, bundle, logs y eventos de prueba no incluyen relato/credenciales; fixtures
   son sintéticos aislados; no probar con terceros ni publicar perfiles ficticios reales.
10. No reserva, pago, acuerdo, asunto, correo de negocio o IA creado implícitamente.
    C02/C03 pendientes operativos se registran como tales; flujo sintético local
    no acredita atención profesional real.

Gate de implementación: checkpoint/modelo/matriz/retención aprobados por Arturo,
contrato A4/A5 revisado y orden con archivos propios. La revisión jurídica mexicana
permanece **LEGAL REVIEW REQUIRED** para activar tratamiento real, sin afirmar
dictamen ni bloquear por certificación todo trabajo local sintético ya aprobado.
Esta entrega solo diseña UX: sin código, SQL, pruebas de aplicación, secretos,
proveedores, operaciones remotas, commits o despliegues.
