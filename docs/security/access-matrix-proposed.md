# Identity y contextos — Matriz de acceso propuesta

Fecha: 2026-10-12. Estado: **Proposed; no aprobada ni implementada**.
Orden T02, A2; revisión por A0. D-003 y D-028 preservados. Roles, propiedad,
permisos, retención y sesiones requieren aprobación antes de código o tablas.
Referencias: [T01](../checkpoints/identity-and-contexts.md),
[amenazas](identity-threat-model.md), [decisiones](../decisions/decision-log.md).
Contrato compartido: IC-01 registro; IC-02 multifunción; IC-03 propiedad;
IC-04 membresía/salida; IC-05 sesión/MFA/revocación; IC-06 camino de datos.

## Actualización de aprobación

D-031 registra la aprobación de Arturo de las recomendaciones A de T01 y del
modelo/matriz recomendados para Identity. D-032 fija 30 días para cuenta cerrada
/evidencia mínima de membresía terminada y 90 días para auditoría, con eliminación
/anonimización posterior. Esta actualización supera el estado pendiente de esas
partes en el borrador; no aprueba superficies F/C03–C19 ni plazos ausentes para
datos jurídicos o evidencia profesional. Implementación y pruebas reales pendientes.

## Lectura de la propuesta

Las columnas representan **situaciones del actor**, no roles ya elegidos para
PostgreSQL, Auth o aplicación. Una misma persona puede ocupar varias situaciones;
cada petición evalúa solo la facultad aplicable a su objeto/contexto. Ser abogado,
cliente, miembro o administrador no otorga acceso general al contenido jurídico.
La administración de proveedores con posprojectsupport es distinta de los permisos
del producto. El despacho nunca obtiene acceso implícito a la práctica propia.

- **D**: negar en el diseño recomendado.
- **L**: lectura de campos publicados; publicación/visibilidad requiere checkpoint.
- **P(...)**: facultad propuesta condicionada al contrato entre paréntesis. No se
  habilita mientras siga pendiente. Leer, crear, editar y eliminar se aprueban por
  separado; P no equivale a CRUD completo.
- **F**: superficie futura fuera de implementación C02/C03. La condición orienta el
  diseño, sin autorizar esa capacidad.

Se recomienda denegar todo lo no concedido expresamente y verificar acción, objeto,
contexto, relación y estado actuales. La UI muestra capacidades, pero no las crea.
[OWASP Authorization](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html).

## Matriz por objeto y acción

| Objeto/acción | Visitante | Persona sobre sí misma | Cliente de relación | Profesional práctica propia | Miembro despacho | Gestor despacho propuesto | Operación producto propuesta |
|---|---|---|---|---|---|---|---|
| Iniciar registro/recuperación | P(IC-01/05) | P(IC-01/05) | Sin facultad adicional | Sin facultad adicional | Sin facultad adicional | Sin facultad adicional | D: sin crear sesión de otro por este rol |
| Leer/editar atributos personales editables | D | P(IC-01): solo atributos permitidos propios | D sobre terceros | D sobre terceros | D sobre terceros | D sobre terceros | P(checkpoint operativo): intervención acotada, sin impersonación implícita |
| Leer/cerrar sesiones propias | D | P(IC-05): alcance local/global por decidir | Sin facultad adicional | Sin facultad adicional | Sin facultad adicional | Sin facultad adicional | D sobre tokens; facultad de revocación ajena requiere checkpoint |
| Modificar roles, estado verificado o permisos por formulario personal | D | D | D | D | D | D | P(C17/IC-04): transición explícita y auditada |
| Leer perfil público publicado | L | L | L | L | L | L | L |
| Editar perfil profesional propio | D | P(IC-01/02, C03): atributos editables; no estado verificado | D por ser cliente | P(IC-02, C03): propio | P(IC-02, C03): propio | D sobre perfiles personales ajenos | P(C17): moderación acotada, pendiente |
| Leer evidencia privada de credenciales | D | P(C03): propia y alcance acordado | D | P(C03): propia | D sobre otros miembros | D por gestionar despacho | P(C03/C17): revisor asignado, no lectura universal |
| Leer/cambiar contexto y capacidades disponibles | D | P(IC-02/04): solo contextos vigentes propios | P(IC-02): funciones de cliente | P(IC-02): práctica propia | P(IC-04): membresía vigente | P(IC-04): facultad acordada | D sobre selección de contexto de otro |
| Leer membresía propia | D | P(IC-04): campos propios acordados | D por ser cliente | P(IC-04): propia | P(IC-04): propia | P(IC-04): información mínima de gestión | P(C17): caso operativo acotado |
| Invitar/aceptar/cambiar facultad o dar baja de miembro | D | P(IC-04): aceptar invitación propia/salida, reglas pendientes | D | D por práctica propia | D salvo facultad expresa | P(IC-04): acciones separadas; no autoelevarse | P(C17): solo operación aprobada |
| Leer/crear relación de cliente del contexto | D | F(IC-03/C04/C05): no cliente global | F: solo vínculo explícito y campos acordados | F: relación de práctica y facultad | F: vínculo asignado y facultad vigente | F: gestión no implica leer relato | F: acceso excepcional definido en C17 |
| Leer/escribir relato, solicitud, consulta o asunto | D | F: propiedad/relación no se infiere por cuenta | F: recurso vinculado y campos acordados | F: relación/contexto y facultad | F: relación asignada y facultad | F: no acceso jurídico por jerarquía | F: no lectura universal por soporte |
| Leer notas internas profesionales | D | D por solo ser dueño de cuenta | D | F(C05): relación/contexto autorizado | F(C05): facultad específica | F(C05): gestión no concede lectura | F(C17): excepción específica pendiente |
| Transferir relación/propiedad entre práctica y despacho | D | D por solo ser dueño de cuenta | F: derechos/consentimiento por decidir | F(IC-03/04/C05): transición específica | F: transición específica | F: transición específica, no copia automática | F: operación excepcional aprobada |
| Consultar auditoría funcional mínima | D | P(IC-05/C16): eventos propios si se aprueba | D por solo ser cliente | D por solo ser profesional | D por solo ser miembro | P(IC-04/C16): alcance de gestión por definir | P(C16/C17): necesidad, campos y retención acordados |
| Leer secretos, tokens/cookies o credenciales de terceros | D | D | D | D | D | D | D: no acceso a valores por rol de producto |

La sesión propia se utiliza únicamente dentro del flujo de autenticación aprobado;
la última fila prohíbe extracción/visualización y acceso a valores de terceros, no
el uso protocolario de la sesión propia. Registro no equivale a verificación
profesional. Recuperación y cierre no autorizan borrado de datos jurídicos.
Retención/borrado y transferencia requieren contratos propios, **LEGAL REVIEW REQUIRED**.

## Caminos técnicos que deben demostrar la matriz

IC-06 decidirá superficies. Una conexión SQL de FastAPI no recibe identidad ni RLS
automáticamente por usar Supabase Auth. Debe existir un contrato explícito del rol
runtime, identidad/contexto verificables, grants y política de filas. Si se usa pool,
el contexto de una petición no puede persistir en la siguiente. Si se habilita Data
API, vistas o funciones, deben demostrar idénticas restricciones aplicables.
No usar `service_role`, BYPASSRLS o desactivar RLS para resolver errores.
[Supabase Data API](https://supabase.com/docs/guides/api/securing-your-api),
[PostgreSQL row security](https://www.postgresql.org/docs/17/ddl-rowsecurity.html).

## Negativos para QA y revisión de seguridad

Fixtures exclusivamente sintéticas: persona A con práctica PA y membresía en D1;
persona B con práctica PB y membresía en D2; persona C con relación R1 y también
profesional en otra relación; dos miembros distintos de D1; operador sin facultad.
Esto representa un despacho por profesional, no pertenencia simultánea a dos.
Crear registros vinculados y no vinculados con marcadores públicos, nunca copiar
sesiones, credenciales ni asuntos reales. Los contratos definirán códigos HTTP y
campos de respuesta; aquí la denegación exige ausencia de datos y efectos.

| ID | Preparación y acción | Aserción que deberá fallar si se rompe el control |
|---|---|---|
| NEG-01 | A sustituye ID de objeto de PA por PB en lectura/escritura/eliminación | Denegado, sin contenido ajeno ni mutación; verificar estado persistido |
| NEG-02 | A filtra/pagina/busca/cuenta/exporta D2; cambia IDs padre/hijo o envía lote mixto | Ningún campo, conteo privado ni elemento ajeno; atomicidad/parcialidad explícita sin efectos no autorizados |
| NEG-03 | C usa función cliente para pedir notas internas o A elige D1 para pedir PA | Función/contexto seleccionado no suma facultades ni revela notas/datos del otro contexto |
| NEG-04 | Usuario modifica metadata editable, rol, bandera de verificado o actor en payload | Ningún privilegio nuevo; identidad procede de sesión verificada, no del cuerpo |
| NEG-05 | Usuario cambia propietario/contexto/relación del objeto al editarlo | Estado y propiedad no cambian sin transición autorizada; probar condición del objeto antes y después |
| NEG-06 | Dar de baja membresía profesional de A en D1 y reutilizar sesión/claims previos | Nuevo acceso profesional derivado de membresía denegado dentro de objetivo aprobado; PA no se transfiere ni expone a D1 |
| NEG-07 | Cambiar facultad/suspender cuenta con caché caliente, JWT previo y petición en curso | Denegación según límite y semántica aprobados; medir tiempo con reloj de prueba, no asumir logout inmediato |
| NEG-08 | Tokens sintéticos: firma inválida, issuer/audience ajenos, expirado, algoritmo no permitido, sujeto ausente | Rechazo antes de datos; no registrar token ni claims crudos |
| NEG-09 | Cerrar/revocar sesión y volver a usar access token anterior | Resultado cumple garantía explícita de IC-05; probar renovación y token ya emitido por separado |
| NEG-10 | A sale de D1 mientras se intenta transferir/copiar una relación a PA | No transferencia automática; no mutación parcial o acceso residual según transición aprobada |
| NEG-11 | Repetir NEG-01/06 por cada vía habilitada: API, Data API, vista/función | Ninguna vía elude política; probar rol sujeto a controles, no administrador |
| NEG-12 | Rol runtime intenta TRUNCATE, cambio de grants, ejecutar función privilegiada o leer esquema ajeno | Facultades excluidas denegadas; fixture intacta; prueba local aislada por A3 |
| NEG-13 | Miembro/gestor/operador sin facultad llama acción administrativa o pide relato privado | Denegado; toda intervención permitida tendrá facultad, alcance, motivo y evento mínimo acordados |
| NEG-14 | Marcadores públicos sintéticos en lugares equivalentes a datos sensibles durante éxito/error/renovación | No aparecen en stdout/stderr, reportes, errores, analítica ni logs; inspección devuelve solo estado/regla |
| NEG-15 | Build/prerender con fixture pública que simula valor privado exclusivamente local | Marcador ausente de HTML, JS, sourcemaps y artefactos publicables; escaneo falla sin publicar valor |
| NEG-16 | PR sintética no confiable intenta imprimir/leer credencial de release y ampliar permisos | Job sin secretos de release, privilegios mínimos; redacción comprobada primero con marcadores públicos |
| NEG-17 | Recuperación de cuentas sintéticas presentes/ausentes, destino no permitido y abuso repetido | Respuesta sin revelar existencia; destino rechazado y límites acordados; sin envíos externos durante diseño |
| NEG-18 | Dos peticiones alternan PA/D1/PB en caché y conexión reutilizada | Ningún contexto/resultado ajeno se hereda entre peticiones |
| NEG-19 | Si IC-05 elige cookies: petición mutante sin protección CSRF/origen válido; si elige bearer: origen y almacenamiento según contrato | Camino elegido rechaza abuso aplicable; no declarar cubiertas ambas variantes con una prueba genérica |
| NEG-20 | A es también cliente de una relación de D1 y termina su membresía profesional | Retirar facultades profesionales derivadas; reevaluar participación cliente independiente según IC-02/04, sin cancelarla ni elevarla silenciosamente |
| NEG-21 | Acción profesional/administrativa con MFA incompleto, factor retirado o recuperación sin facultad | Si se aprueba IC-05 A, denegar acción privada; comprobar nivel vigente además de permisos, sin bypass de soporte |

La salida/suspensión profesional no decide por sí sola derechos de una participación
independiente como cliente del mismo despacho. IC-02/IC-04 y T03 deberán aprobar
esa combinación; reingresar no restaura asignaciones profesionales automáticamente.

Para cada negativo: incluir un control positivo autorizado sobre fixture equivalente,
verificar que denegación no proviene de servidor apagado, y observar persistencia.
Cuando haya código, retirar temporalmente el control en entorno aislado deberá hacer
fallar el negativo; un mock de autorización no prueba aislamiento real. A7 define
suite y evidencia, A2 revisa y A0 integra; esta entrega no añade tests ejecutables.

## Criterio de aprobación y estado de verificación

Arturo deberá resolver IC-01–IC-06 en T01. A0 conciliará esta matriz con T01/T03 y
registrará permisos por acción/campo, restricciones de estados y objetivo de
revocación. Toda P/F permanece pendiente; no convertirla en grant o endpoint.

Verificado: coherencia documental con D-003/D-028 y amenazas requeridas de T02;
lectura de fuentes oficiales, estructura de matriz y especificaciones negativas.
Pendiente: revisión independiente A0, acuerdo de T01/T03, ejecución local con
controles reales, scanner redactado, CI remoto y revisión jurídica aplicable.
No se accedió al proyecto remoto, browser de secretos o recursos Kova; no se crearon
tablas, roles, sesiones, artefactos de pruebas, commits o despliegues.
