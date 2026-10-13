# Estrategia de Inteligencia Artificial

## Alcance aprobado para la etapa actual

Arturo decidió limitar la implementación actual de IA a estas dos funciones:

1. **Resumir una solicitud cuando el usuario lo pide.**
2. **Preparar un mensaje con información seleccionada por el abogado.**

Estado del alcance: Approved, decisión D-019. Flujos funcionales: Approved, decisión D-020. React + FastAPI están aprobados en D-025; el repositorio sigue sin aplicación. La implementación, proveedor de IA, modelo de permisos, retención, presupuesto y tratamiento por terceros siguen pendientes.

El [checkpoint de estas dos funciones](checkpoints/ai-assistance.md) contiene los flujos aprobados, criterios de aceptación y decisiones restantes. Las otras funciones de IA de este documento se conservan como posibilidades futuras y quedan fuera de la implementación actual. La decisión limita IA; no reduce el alcance de la plataforma completa ni redefine su primera entrega.

Arturo aplazó explícitamente el procesamiento documental con IA en D-022: OCR, extracción e indexación. Las dos funciones de texto continúan aprobadas. La gestión básica de documentos del producto no se elimina por esta decisión.

## Objetivo

Usar IA para reducir fricción y mejorar decisiones, sin reemplazar el criterio jurídico.

## Posibilidades futuras fuera de la implementación actual

- Clasificación de situaciones.
- Resumen de intake.
- Extracción de entidades.
- Identificación de fechas.
- Detección de información faltante.
- Detección de urgencia.
- Recomendación de categorías.
- Matching asistido.
- Moderación.
- Seguimiento.
- Comunicaciones.
- Análisis documental.
- Búsqueda semántica.

Resumen y comunicaciones de esta lista solo se incorporan ahora con el alcance específico de las dos funciones aprobadas arriba. Esta lista no es autorización para automatizar clasificación, seguimiento o envío.

## Límites

La IA no debe:

- Garantizar resultados.
- Emitir conclusiones definitivas.
- Sustituir al abogado.
- Determinar culpabilidad.
- Proporcionar asesoría autónoma.
- Procesar información sin consentimiento.
- Entrenar con datos sensibles sin control.

## Human in the loop

Requerido para:

- Clasificación de alto riesgo.
- Penal.
- Violencia.
- Menores.
- Urgencias.
- Recomendaciones delicadas.
- Moderación compleja.
- Documentos sensibles.

## Evaluación

- Precisión.
- Recall.
- Falsos positivos.
- Falsos negativos.
- Sesgo.
- Explicabilidad.
- Seguridad.
- Costo.
- Latencia.
- Privacidad.

## Gobierno

- Versionado.
- Registro.
- Prompts.
- Modelos.
- Evaluaciones.
- Rollback.
- Monitoreo.
- Red teaming.
- Incidentes.
