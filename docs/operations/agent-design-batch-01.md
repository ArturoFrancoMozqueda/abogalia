# Tanda 01 — Identity y contextos

Fecha: 2026-10-12. Coordinación: A0. Autorización: Arturo pidió revisar el plan
y levantar agentes para desarrollarlo. Alcance ejecutable inmediato: T01–T03
en diseño; T04 preparado por coordinación. No aprueba las decisiones de Identity.

## Referencia y propiedad

Rama asignada: `codex/identity-design`. HEAD de partida:
`c71fea298742a43994cf6026494ded080b3ef50d`.
La fundación y documentos locales sin commit forman parte del contexto; este SHA
por sí solo no los contiene. Se preservan los cambios existentes. No se ha creado
todavía un baseline publicable ni se ha completado un scan del historial.

Los agentes de esta tanda comparten checkout con archivos exclusivos para diseño.
Antes de distribuir implementación en worktrees se requiere una referencia común
con la fundación incorporada y revisión de secretos terminada, como exige el plan.
Ningún agente modifica Git, configuración global, lockfiles o código de aplicación.

| Orden | Autor | Archivo exclusivo | Revisor | Dependencia |
|---|---|---|---|---|
| T01 | A1 / identity_checkpoint | [Checkpoint](../checkpoints/identity-and-contexts.md) | A0 | D-003, D-028, fundación |
| T02 | A2 / identity_security | [Amenazas](../security/identity-threat-model.md), [matriz](../security/access-matrix-proposed.md) | A0 | Contrato de preguntas T01 |
| T03 | A3 / identity_data | [Modelo conceptual](../data/identity-model-proposed.md) | A0 y revisión A2 | Contrato de preguntas T01 |
| T04 | A0 | [Desarrollo seguro propuesto](secure-development-proposed.md) | A2 | Workflow local existente |

Entradas: README, AGENTS, plan, registro de decisiones, checkpoint de fundación y
documentación pública oficial. Prohibido leer secretos, clientes reales o recursos
de Kova; no usar el navegador administrativo ni conectores de proyectos.
No hay instalación, migración, publicación, provisioning ni contratación.

## Contrato de diseño compartido

Seis IDs estables, todos pendientes de decisión de Arturo:

1. IC-01: registro y recuperación.
2. IC-02: usuario con varias funciones.
3. IC-03: propiedad de relaciones y acceso del cliente.
4. IC-04: membresía y salida del despacho.
5. IC-05: sesiones, MFA y revocación.
6. IC-06: camino de datos y autorización.

Las recomendaciones se marcan como propuestas. D-003 conserva práctica propia más
un despacho y D-028 conserva Supabase Auth. Ninguna recomendación agrega Approved
al registro. El checkpoint debe contener las ocho secciones y criterios verificables.
Retención, clasificación e historial se documentan sin inventar plazos aprobados.

## Aceptación y siguiente paso

A0 verifica coherencia entre documentos, enlaces, estados y alcance; A2 revisa el
modelo y la propuesta T04 como autor independiente. Una revisión documental no
prueba controles implementados. Los casos de prueba descritos siguen por ejecutar.

Tras integrar T01–T03, presentar a Arturo una sesión de hasta seis decisiones.
T05–T07 podrán derivar contratos, UX y aceptación del diseño; implementación C02
requiere aprobación del checkpoint y dependencias listas. T08 sigue en cola.
Ningún recurso externo ni código de negocio se habilita por esta tanda.

## Resultado de la tanda

T01, T02 y T03 entregados por los tres agentes y revisados documentalmente por A0.
T03 y T04 tuvieron revisión independiente de A2; T04 y este registro también fueron
revisados por A1. Sin bloqueantes para entrega de diseño; no es aprobación de
implementación ni validación de controles en ejecución. Estado: **Awaiting decision**.

Corrección de integración: salida del despacho retira facultades profesionales
derivadas de membresía; una participación independiente como cliente se evalúa
por relación y acción. No conserva facultades profesionales ni se elimina
automáticamente por la salida. T01/T02/T03 reflejan esa distinción propuesta.

Verificación local de los seis documentos nuevos: sin enlaces locales rotos,
sin espacios finales; ocho secciones y seis IDs presentes en el checkpoint.
Revisión limitada de patrones de clave privada, JWT y URL con contraseña,
con salida solo de conteos: cero coincidencias. No equivale a scanner formal,
revisión del historial o certificación de ausencia de secretos. No se leyeron
archivos sensibles para estas comprobaciones.

No se ejecutaron pruebas de aplicación, SQL, CI remoto, restauración, commit, push
o despliegue. No hay mocks funcionales; escenarios y negativos son especificaciones.
Los cambios previos permanecen locales. Antes de implementar: aprobación de los
paquetes aplicables IC-01–IC-06, matriz y modelo completo (incluida retención),
contratos, definición técnica de custodia/revocación y referencia común segura.
