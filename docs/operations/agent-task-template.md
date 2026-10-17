# Plantilla de orden de trabajo para un agente

Copiar y completar una orden por capacidad y asignación. No incluir credenciales,
datos de clientes ni salidas de herramientas que puedan contenerlos. Un rol no es
una autorización global para todos los recursos de ese proveedor.

```text
Proyecto: Abogalia. Leer AGENTS.md y docs/27_development_plan_agents.md.
Orden: [ID de tarea]
Rol: [A1–A8]
Modo: [Diseño / Implementación local / Revisión / Operación autorizada]
Objetivo y valor para el usuario: [...]
Capacidad: [Cxx]
Estado del checkpoint: [ruta + estado + decisiones de Arturo que lo respaldan]
Decisiones aprobadas aplicables: [IDs]
Decisiones pendientes: [...; no resolverlas por inferencia]
Base Git: [rama y SHA comunes revisados; nunca inventarlos]
Rama/worktree: [destino asignado]
Archivos que puedes editar: [lista acotada]
Archivos compartidos que requieren coordinación: [...]
Dependencias: [contrato/versiones/entregas previas]
Entradas permitidas: [documentos públicos y datos sintéticos]
Acceso externo: [ninguno por defecto; proveedor/recurso/entorno/operación exactos]
Secretos: no leer, mostrar, copiar, solicitar ni transmitir sus valores.
Implementación incluida: [...]
Fuera de alcance: [...]
Contrato: [API, eventos, estados y permisos acordados]
Pruebas y criterios de aceptación: [casos positivos, negativos y excepciones]
Entregables: [archivos, evidencia sanitizada y reporte]
Revisor: [otra persona/agente; autor no aprueba su propia entrega]
Condiciones para detener la operación afectada:
  exposición de secreto, destino equivocado, acceso no autorizado,
  decisión bloqueante sin aprobar o intento de debilitar controles.
Al detectar una condición, reportar sin valores y avanzar solo en tareas seguras
independientes. No publicar, provisionar o migrar recursos por inferencia.
```

## Formato del reporte

1. Resultado y alcance realmente completados.
2. Archivos cambiados y contrato utilizado.
3. Pruebas ejecutadas, resultado y qué permanece sin verificar.
4. Decisiones pendientes o cambios que requieren coordinación.
5. Revisión de seguridad y secretos: controles comprobados, sin valores ni
   fragmentos de credenciales; nunca certificar ausencia absoluta de riesgo.
6. Próxima dependencia y quién puede continuar.

Estados de tareas: Ready for design → Awaiting decision → Ready for implementation
→ In progress → Review → Integrated → Verified. Una tarea puede estar Blocked por
una dependencia concreta. Estos estados de backlog no reemplazan los estados de ADR.

