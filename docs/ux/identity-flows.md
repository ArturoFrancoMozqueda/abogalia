# Recorridos de identidad — contrato UX

Fecha: 2026-10-12. Orden T06 / A5. Estado: diseño para revisión A0; sin pantallas
implementadas. A0 comunicó aprobación de las opciones A de IC-01–IC-06 y
continuación proactiva por Arturo; su registro corresponde a A0. Este documento
aplica esos recorridos sin convertir parámetros técnicos todavía incompletos en
implementación. Referencias: [checkpoint](../checkpoints/identity-and-contexts.md),
[modelo conceptual](../data/identity-model-proposed.md) y
[contrato API T05](../contracts/identity-api.md), en preparación.

## Alcance inicial y navegación

La identidad usa correo y contraseña con confirmación, una cuenta con función
cliente y habilitación profesional separada. La API custodia la sesión; el
navegador recibe una cookie opaca HttpOnly. Los datos privados pasan por FastAPI.
La práctica propia y un despacho activo conservan permisos por acción/relación.
Retención y tablas de negocio siguen pendientes; acceso y sesión avanzan con su
contrato independiente. No hay captación, expediente, pagos o IA en estas rutas.

| Ruta | Objetivo | Acción principal | Enlaces disponibles |
|---|---|---|---|
| `/acceso` | Entrar con una cuenta existente | «Entrar» | «Crear cuenta», «Recuperar acceso», «Volver al inicio» |
| `/registro` | Solicitar una cuenta inicial | «Crear cuenta» | «Ya tengo cuenta», «Volver al inicio» |
| `/recuperar` | Solicitar y completar recuperación según contrato | «Solicitar recuperación» | «Volver a acceso» |
| `/cuenta` | Consultar estado de cuenta y cerrar sesión | «Cerrar sesión en este dispositivo» | «Cerrar sesión en todos los dispositivos», «Volver al inicio» |

Rutas privadas comprueban sesión con la API antes de mostrar identidad. Mientras
se comprueba, usar «Comprobando tu sesión…» sin contenido privado previo. Fallo de
red no equivale a sesión ausente. `/cuenta` redirige a `/acceso` únicamente ante
respuesta de sesión no autenticada. Retornos posteriores al login usan destinos
internos permitidos; no consumir un destino arbitrario recibido en la URL.

## Contrato consumido por el navegador

| Operación T05 | Uso UX | Regla |
|---|---|---|
| GET `/api/auth/session` | Resolver inicio y `/cuenta` | `{authenticated:false}` o `{authenticated:true,user:{id,email,assurance}}`; no deducir roles de `assurance` |
| GET `/api/auth/csrf` | Preparar acciones con efecto | `{csrf_token}` mantenido en memoria; cabecera y vigencia exactas dependen de T05 |
| POST login | Enviar `{email,password}` | Solo mediante API; limpiar contraseña tras respuesta o salida del formulario |
| POST register | Alta inicial | Campos y respuesta final por T05; propuesta UX: correo, contraseña y repetición local |
| POST recover | Solicitar recuperación | Correo y respuesta genérica conforme a T05; envío externo condicionado a operación de correo |
| POST logout | Enviar `{scope:local}` o `{scope:global}` | Actualizar estado solo con respuesta; no declarar revocación cuando falle |

Errores tienen forma `{error:{code,message}}`. El frontend mapea códigos conocidos
a copy en español; no muestra respuestas crudas, trazas o detalles del proveedor.
Endpoints completos, estados HTTP, políticas de contraseña, confirmación,
recuperación por código, MFA y reenvío deben fijarse en T05 antes de programar
acciones dependientes. No crear endpoints desde UX.

La sesión, cookie, contraseña y código temporal no van a URL, localStorage,
sessionStorage, analítica, logs, capturas, fixtures o reportes. El frontend no
recibe tokens Supabase. El CSRF se usa solo para su finalidad y tampoco se registra.
No ofrecer «recordarme» ni otro plazo no aprobado. No enviar contenido de campos
a telemetría. Navegar fuera limpia contraseñas/códigos de memoria y formularios.

## `/acceso`

Campos visibles: «Correo electrónico» y «Contraseña»; etiquetas persistentes.
Usar `autocomplete=email` y `current-password`. Permitir pegar y gestores de
contraseñas. «Mostrar contraseña» es un botón con estado anunciado y no altera
el valor. Mensaje inicial: «Entra para consultar tu cuenta y tus servicios».

| Estado | Mensaje y comportamiento |
|---|---|
| Correo inválido | «Escribe un correo electrónico válido» junto al campo; no enviar |
| Contraseña ausente | «Escribe tu contraseña» junto al campo |
| Envío | «Entrando…»; evitar envíos duplicados sin bloquear navegación por teclado |
| Credenciales rechazadas | «No pudimos iniciar sesión con esos datos. Revisa tu correo y contraseña»; enlace de recuperación |
| Cuenta sin confirmar | Solo si T05 permite ese código tras autenticación: «Confirma tu correo para entrar. Revisa el mensaje de confirmación» |
| Límite temporal | «Espera un momento antes de volver a intentarlo»; respetar plazo del servidor cuando exista |
| Servicio/red no disponible | «No pudimos conectar. Inténtalo de nuevo»; no anunciar que la contraseña es incorrecta |
| Éxito | Comprobar sesión y navegar a `/cuenta` o retorno permitido |

Un formulario válido no implica login exitoso. No inspeccionar ni mostrar JWT.
MFA incompleto puede permitir la vista básica de cuenta según T05; no da acceso
profesional privado. El correo recibido es identidad de cuenta, no certificación.

## `/registro` y confirmación

Mensaje inicial: «Crea una cuenta para consultar tus servicios. El alta profesional
se revisa por separado». Campos: correo, contraseña y «Repite tu contraseña».
La repetición se compara localmente y no se envía. Usar `new-password`, permitir
pegar y mostrar la política acordada con T05 sin inventar requisitos.

Si faltan términos/aviso aprobados, no insertar enlaces ficticios ni una casilla
de consentimiento que simule su aprobación. El registro público con datos reales
depende de esos textos y de operación de correo: LEGAL REVIEW REQUIRED.

Respuesta genérica tras solicitud: «Si podemos completar el registro con ese
correo, recibirás las instrucciones para confirmar tu cuenta». Igual respuesta
para correo existente cuando lo exija T05; no revelar existencia por copy,
tiempos artificiales o campos de error. No prometer entrega inmediata.

Confirmación propuesta: instrucciones para introducir código desde el correo
fuera de la URL, con operación exacta pendiente del contrato. No procesar enlaces
que contengan tokens en fragmentos o query. Si el proveedor/formato elegido exige
ese flujo, A0/T05 deben resolverlo antes de habilitar confirmación, sin relajar
silenciosamente la regla. Código incorrecto/vencido: «Ese código no es válido o
ya venció. Solicita uno nuevo». Reenvío solo si T05 dispone endpoint y límites.
Confirmación exitosa: «Correo confirmado. Ya puedes entrar». Nunca «Abogado
verificado», «Perfil publicado» o «Despacho habilitado» por confirmar correo.

## `/recuperar`

Paso 1: correo y «Solicitar recuperación». Copy de resultado uniforme: «Si hay
una cuenta que pueda recuperarse con ese correo, recibirás las instrucciones».
Conservar resultado genérico también para correo desconocido. Si falla la red,
«No pudimos completar la solicitud. Inténtalo de nuevo» sin afirmar envío.

Pasos 2 y 3 propuestos, bloqueados hasta T05: introducir correo/código en el
formulario, validarlo por API y definir nueva contraseña con repetición local.
Código y credenciales de recuperación solo en cuerpo de petición; custodia del
proceso en API con estado acotado, nunca parámetros de URL o almacenamiento web.
`autocomplete=one-time-code` para el código y `new-password` para nueva clave.
No crear una sesión de negocio con la sola validación de un código de recuperación.

Resultado: «Contraseña actualizada. Vuelve a entrar». Invalidación de sesiones y
MFA tras recuperación necesitan efecto explícito T05; no prometer «todos los
dispositivos desconectados» salvo garantía verificada del backend. Recuperación
de contraseña no recupera permisos retirados ni omite MFA. Recuperación de factor
es un flujo separado pendiente; no botón que conceda bypass ni instrucción de
enviar credenciales a soporte.

## `/cuenta`, MFA y contextos

Mostrar el correo devuelto por la sesión con etiqueta «Cuenta» y «Sesión activa».
No presentar `id` técnico ni interpretar `assurance` como rol o membresía.
No mostrar selección de práctica/despacho a partir de datos ausentes: el contrato
actual no devuelve habilitación, contextos o permisos. Su selector requiere API
específica; al cambiarlo se limpia contenido anterior y se valida acceso actual.

Para acceso profesional privado futuro, exigir MFA TOTP validado por servidor.
Copy propuesto: «Completa la verificación en dos pasos para continuar»; código
inválido: «No pudimos verificar ese código. Revisa el código actual e inténtalo
de nuevo». Sin endpoint MFA implementado, no mostrar botón que finja verificar.
Enrolamiento, código QR, recuperación y eliminación de factor requieren diseño
separado; esos secretos no entran en evidencias de prueba ni capturas de agente.

Logout local: una acción directa con etiqueta explícita. Logout global: acción
«Cerrar sesión en todos los dispositivos», con confirmación «Se cerrarán las
sesiones de esta cuenta en tus dispositivos» y botones «Cerrar todas»/«Cancelar».
No mencionar retirada de membresías o borrado de datos como efecto del logout.
Éxito: limpiar estado privado, volver a acceso y anunciar «Sesión cerrada».
Fallo: «No pudimos confirmar el cierre de sesión. Inténtalo de nuevo»; conservar
la distinción entre interfaz limpiada y revocación real, sin declarar éxito.

Sesión expirada/revocada: limpiar contenido privado y mostrar «Tu sesión terminó.
Vuelve a entrar». Acceso a objeto denegado: «No tienes acceso a este contenido»
sin nombre/destinatarios del objeto ajeno. Cambio de membresía: «Tu acceso
profesional a este despacho cambió»; reevaluar participación como cliente y
práctica propia por separado, sin restaurar privilegios antiguos.

## Accesibilidad y recuperación de fallos

HTML semántico, un título principal, etiquetas vinculadas y mensajes asociados
mediante `aria-describedby`; `aria-invalid` solo tras error. Resumen de errores
con enlaces a campos y foco en el primer error al enviar. Estados de progreso y
éxito anunciados por región `aria-live=polite`; errores importantes anunciados
una vez. No depender de color, animación o placeholder. Foco visible y orden
lógico; diálogos devuelven foco al botón de origen y permiten cancelar.

Permitir zoom, lectores de pantalla, pegado y gestores; evitar pruebas de memoria
o CAPTCHA cognitivo añadido por UX. Mantener correo ante fallos corregibles,
limpiar contraseñas/códigos y permitir reintento consciente. No reenviar login,
registro o recuperación automáticamente tras timeout incierto. No reintentar
mutaciones tras fallo CSRF sin regla específica de T05. Ningún toast es la única
fuente del estado. Referencias oficiales:
[notificaciones de formularios](https://www.w3.org/WAI/tutorials/forms/notifications/)
y [autenticación accesible](https://www.w3.org/WAI/WCAG22/Understanding/accessible-authentication-minimum.html).

## Aceptación y entrega

Pruebas futuras sintéticas: teclado/lector de pantalla, campos inválidos, login
rechazado, red caída, sesión ausente/expirada, doble envío, recuperación genérica,
logout local/global fallido y exitoso, navegación tras timeout, MFA incompleto,
acceso ajeno y desaparición de contexto. Inspeccionar contratos, historia/URL y
almacenamiento con marcadores sintéticos para detectar secretos; no usar datos
reales ni publicar capturas con entradas sensibles. La UI no sustituye pruebas
de autorización de API/base.

Único archivo editado en T06: `docs/ux/identity-flows.md`. Lectura de checkpoint y
orden A0; documentación pública W3C consultada el 2026-10-12. T05 aún estaba en
preparación al redactar: rutas no fijadas quedaron pendientes expresamente.
No se programaron pantallas, instalaron dependencias ni accedió a proyectos,
entornos, secretos o DB. Sin pruebas runtime, CI, commit, push o despliegue.
Revisión A0 y orden posterior de implementación tras baseline seguro pendientes.
