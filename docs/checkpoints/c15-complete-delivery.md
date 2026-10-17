# C15 — Entrega completa y aceptación

Fecha: 2026-10-16. Estado: **Proposed**. No aprobación de alcance de lanzamiento.

## Lo que entiendo

El plan completo es una visión, no una autorización para implementar todas sus
capacidades. La entrega necesita un recorrido útil y verificable, con límites
visibles y dependencias cerradas. La web publicada permite preparar aceptación de
Identity; todavía no permite contratar servicios jurídicos ni acredita C02 Done.

## Decisiones tomadas

D-014 prioriza independientes/despachos pequeños; D-015 centra la relación de
servicio; D-016 conserva búsqueda gratuita/precio o cotización. Hosting aprobado
se mantiene. D-040/D-041 y D-032 ya resuelven los paquetes profesionales y30/90;
no se preguntan otra vez. Resumen/borrador IA D-019/D-020 tienen flujos aprobados,
pero proveedor, tratamiento y gasto siguen pendientes.

## Decisiones pendientes

Elegir primera entrega: se recomienda recorrido con cliente propio, contexto
profesional habilitado, solicitud/decisión, acuerdo y seguimiento mínimo; es una
propuesta que depende de C04/C05 y no aprueba mensajería, cobro o IA. Alternativa:
catálogo/derivación sin contratación, con promesa menor. Precisar público/geografía,
servicios, criterios de éxito, soporte y exclusiones. Acordar condiciones jurídicas,
accesibilidad y responsables antes de usuarios reales. No imponer una fecha sin
estimar capacidades aprobadas.

## Diseño propuesto

DeliveryScope enumera capacidades y sus versiones aprobadas; AcceptanceScenario
pertenece a un scope y tiene actor/precondición/acción/resultado; ReleaseDecision
refiere evidencias y pendientes. No son tablas de negocio ni entidad `case`.

Estados de entrega: propuesta → alcance aprobado → implementada parcialmente →
aceptación pendiente → lista para apertura; fallo crítico → bloqueada. Toda
excepción debe tener responsable, consecuencia y autorización concreta; nunca
ocultar un negativo roto como excepción cosmética. A0 integra; A7 verifica y A2
revisa autorización/privacidad de forma independiente.

Recorrido propuesto depende de C02/C03 reales, C04 solicitudes/conflicto, C05
relación y C14 operación. Agenda, documentos, notificaciones y pagos se incluyen
solo si la entrega aprobada los exige y sus propios checkpoints están cerrados.
C18/C19 y procesamiento documental IA siguen diferidos. Una pantalla o mock es
una evidencia de interfaz, no aceptación funcional.

## Datos afectados

Ensayo con identidades y contenido sintéticos aislados. Las evidencias públicas
solo llevan nombre de escenario y resultado fijo; pruebas privadas no deben
convertirse en relatos de usuarios. Finalidad, titularidad y retención de cada
capacidad se heredan de su contrato aprobado; retención de nueva evidencia de
aceptación queda pendiente, sin copiar PII en screenshots, issues o repositorio.

## Seguridad

Matriz completa cliente/profesional/despacho/operador; negar ID/contexto ajeno,
capacidad suspendida y sesión revocada tanto al inicio como en commit. Rechazar
transiciones concurrentes incompatibles. Verificar no reaparición tras restore,
caché o salida del despacho. No usar datos de clientes para prueba ni atribuir
servicios profesionales, éxito jurídico o cumplimiento a una demo.
**LEGAL REVIEW REQUIRED** antes de apertura jurídica.

## Impacto futuro

Una entrega acotada puede estar terminada aunque C18/C19 sigan aplazados; se debe
decir su alcance. El fin del planning produce una cola implementable y decisiones
explícitas, no el cierre ficticio del producto ni autorización de gasto adicional.

## Implementación propuesta

1. A0 obtiene selección de alcance/criterios y registra sus decisiones, con
   dependencias y bloqueos humanos/jurídicos separados de trabajo de código.
2. A7 prepara escenarios positivos/negativos por actor y evidencia esperada sin
   secretos; A2 revisa aislamiento y efectos de revocación.
3. Cerrar correo/MFA/revocación/retención/restore de C02 y completar C03 aprobado;
   implementar C04/C05 después de sus checkpoints, no por este texto.
4. Ejecutar extremo a extremo navegador→API→DB→respuesta con fallos reales
   controlados: correo no entregado, revocación, concurrencia, salida, cuota y
   recuperación. Contabilizar pruebas locales, mocks, CI y producción por separado.
5. Criterio de salida: todos los escenarios críticos del scope pasan, responsables
   y recuperación están operativos y no quedan preguntas que alteren permisos,
   datos o promesas de la entrega. Esta revisión documental no ejecuta esos pasos.
