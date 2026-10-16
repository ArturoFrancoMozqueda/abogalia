# C18 — Ampliación jurídica futura

Fecha: 2026-10-16. Estado: **Proposed / Deferred**. Solo límites y puertas de
reentrada; no es parte automática de la entrega actual.

## Lo que entiendo

Actuaciones, vencimientos jurídicos, firma y operación fiscal necesitan diseños y
responsabilidades especializados. La visión de gestión jurídica interna aprobada
en D-015 no aprueba cálculos, firma con efectos legales ni cumplimiento fiscal.

## Decisiones tomadas

Relación de servicio como centro D-015; ampliación posterior con checkpoint propio.
No OCR, embeddings o indexación documental IA D-022. IA actual se limita a resumen
y borrador revisables D-019/D-020; no se usa para establecer plazos u obligaciones.
No seleccionar proveedores, gasto o nuevos accesos por el planning de C18.

## Decisiones pendientes

Elegir un único subdominio al reabrir: actuaciones/plazos, firma o fiscal; cada uno
requiere alcance geográfico/jurídico, fuente, responsable profesional, límites y
mecanismo de corrección. No inventar reglas mexicanas, cómputos, vencimientos o
valor probatorio. Presupuesto, proveedor, datos, custodia y retención se deciden
después de esa selección. **LEGAL REVIEW REQUIRED** antes de diseñar operación real.

## Diseño propuesto

Conceptos orientativos, sin schema: LegalAction pertenece a una relación C05 y
contexto autorizado; DeadlineReference vincula fuente y revisión profesional;
SignatureEnvelope refiere versión exacta de documento C09 y participantes con
facultad; FiscalRecord pertenece a la obligación/actor fiscal correspondiente,
no necesariamente al pagador o al contexto operativo. No combinar estos dominios.

Estado de reentrada: diferido → necesidad documentada → análisis jurídico/técnico
→ checkpoint específico aprobado → implementación. Una referencia de plazo podría
estar borrador/revisada/corregida, pero transiciones, autoridad y efectos deben
aprobarse por subdominio. No ejecutar consecuencias automáticamente ni tomar un
recordatorioC10 por plazo jurídico validado.

## Datos afectados

Potencial contenido jurídico altamente restringido, fuentes, versiones y evidencias
probatorias/fiscales. C05/C09 deben fijar propiedad, acceso y conservación antes
de referencias nuevas. Retención completa pendiente y separada de30/90 Identity;
no guardar documentos reales ni identidades fiscales durante este análisis.
Historial puede requerir corrección preservada, sin inventar inmutabilidad o
conservación indefinida. Revisión jurídica decide requisitos concretos.

## Seguridad

Facultad profesional, firma y acceso al documento son controles distintos. No usar
credencial Auth/MFA como prueba de representación o consentimiento de firma. No
inferir normativa por jurisdicción del usuario. No importar claves de firma,
certificados privados o credenciales fiscales al repositorio/chat/modelo.
Negativos futuros: fuente ausente, versión alterada, profesional no facultado,
contexto ajeno, cancelación, zona horaria/calendario ambiguos y corrección tardía.

## Impacto futuro

Reentrada depende de C05/C09, operación recuperable C14, auditoría aprobadaC16 y
responsable humano. Cada subdominio podría exigir proveedor/costo/contrato nuevo;
su evaluación no compromete contratación ni modifica el hosting actual.

## Implementación propuesta

No escribir código/tablas/endpoints de C18 ahora. Preparar al reabrir un análisis
con fuentes oficiales actuales, casos sintéticos, revisión jurídica especializada,
matriz de riesgo y presupuesto concreto. Criterio para iniciar: capacidad previa
aceptada, necesidad validada, responsable y modelo completo aprobados. Criterio
futuro de salida: casos positivos/negativos específicos y correcciones demostradas
sin atribuir al software garantías jurídicas no revisadas.
