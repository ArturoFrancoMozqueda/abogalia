# Checkpoint C06 — Catálogo, descubrimiento y compatibilidad

Fecha: 2026-10-16. Estado: **Proposed / Requires Arturo**. Orden A1, baseline
`4eb597c`, rama `codex/identity-design`; revisor A0/A2. Planificación solamente.

## Lo que entiendo

Búsqueda gratuita está aprobada; cobertura nacional efectiva, especialidades,
ranking, patrocinios, precios y garantía de disponibilidad no lo están. El catálogo
organiza opciones declaradas y publicadas; no diagnostica problemas ni concluye que
un abogado puede asumir una solicitud. C03 habilita/publica profesionales; C04
revisa una solicitud particular; C07 confirma horarios, no C06.
Fuentes: [plan](../27_development_plan_agents.md), [decisiones](../decisions/decision-log.md),
[producto refinado](../23_refined_product.md), [C03](professional-contexts.md),
[C04](c04-requests-conflicts.md), [alcance](../05_product_scope.md).

## Decisiones tomadas

D-011/014/016: claridad, segmento profesional prioritario, búsqueda gratuita,
servicios con precio o cotización y referencias institucionales pertinentes.
No se aprueba tarifa, moneda de oferta, impuestos ni captación garantizada.
D-040 separa revisión profesional y publicación voluntaria; no publicar número
completo de cédula ni presentar especialidad declarada como verificada.
D-010 sobre patrocinio sigue Proposed; D-003/031 mantienen aislamiento de prácticas.

## Decisiones pendientes

AT-05 del [handoff](../operations/planning-attention-handoff.md) propone directorio
orgánico limitado a oferta realmente habilitada y voluntariamente publicada,
filtros explícitos y orden determinista explicado. Alternativa: postergar buscador
público y usar únicamente selección directa consentida C04/C05.

En ambos casos faltan lista inicial de áreas/situaciones/jurisdicciones y su editor,
servicios y condiciones, cobertura efectiva, validación de referencias institucionales,
reglas de exclusión/publicación y tratamiento de búsquedas. Ninguna ciudad/área
queda elegida por este documento. Matching por relato, patrocinio, reseñas, precio
personalizado y aprendizaje automático se mantienen fuera del primer corte.
**LEGAL REVIEW REQUIRED** para taxonomía/afirmaciones profesionales, condiciones
de oferta, tratamiento de datos y referencias; no se realizó investigación jurídica.

## Diseño propuesto

| Entidad | Relaciones/propiedad propuestas | Estados e historia |
|---|---|---|
| PracticeArea | Catálogo editorial versionado de plataforma, no credencial | borrador → publicada → retirada; sustitución mantiene referencias sin reinterpretar historias |
| LegalIssue | Situación orientativa vinculada a áreas, no diagnóstico ni relato de cliente | borrador/revisada/publicada/retirada; autor/revisor/versión mínimos |
| Jurisdiction | Catálogo territorial/competencial revisado; ámbito declarado no prueba competencia | activa/retirada; no inferir competencia por proximidad física |
| ServiceOffering | Contexto propietario/profesional oferente; área, jurisdicción, modalidad, alcance y condiciones | borrador → lista para revisión → publicada / pausada / retirada. Publicar exige controles C03 y condiciones completas |
| PublicProfessionalProjection | Proyección de campos publicables C03, no copia de tablas privadas | publicada → suspendida/retirada; retirar elimina proyección/índice/caché según contrato |
| InstitutionalReference | Recurso institucional público, fuente/alcance/revisión editorial | propuesta → revisada/publicada → requiere revisión/retirada; frecuencia/actor pendientes |
| LawyerMatch | Resultado derivado de criterios públicos, no relación jurídica ni autorización | sin persistencia por defecto propuesta; guardar resultados exige política aparte |

Primera búsqueda propuesta: filtros de área/situación orientativa, jurisdicción
y modalidad, con etiquetas de declarado/revisado según C03. Solo resultados que
cumplen filtros; no relajar jurisdicción silenciosamente por falta de oferta.
Orden inicial recomendado: nombre de presentación normalizado e identificador
estable como desempate, explicado sin afirmar mejor calidad. No usar pago,
conversión, datos privados, velocidad de aceptación o ubicación precisa como ranking.
Rotación justa u otra ordenación requerirá diseño porque cambia exposición.

Una oferta publicada necesita alcance, duración si aplica, modalidad, condiciones,
precio claro o indicación explícita de cotización. Una cotización no aparece como
cero; búsqueda gratuita no significa servicio gratuito. Fijación profesional de
precios, impuestos, moneda y revisiones requieren acuerdo C05/C08 antes de publicar
ofertas transaccionables. Directorio inicial puede mostrar perfiles y contacto
interno sin simular compra o disponibilidad de servicio todavía no habilitado.

Propuesta API/UX: endpoint público paginado que serializa solo la proyección,
filtros enumerados/validados y orden explicado; endpoint de ficha pública con
estado vigente. Mutaciones de oferta requieren contexto/actor/MFA y revisión de
publicación. Nada de intake por querystring, email, IDs de cliente, documentos o
contenido privado en buscador/SEO. No endpoint de "buscar todos los clientes".

Sin oferta: explicar criterio sin resultados; permitir cambiar filtros expresamente,
volver o consultar referencias revisadas pertinentes. No inventar profesionales,
recomendar un resultado incompatible, prometer atención urgente ni trasladar
relato a otros destinatarios. No mapa ni domicilio privado por inferencia.

## Datos afectados

| Familia | Clasificación/acceso | Retención/historia pendiente |
|---|---|---|
| Catálogo editorial | Público solo tras revisión; borradores restringidos al editor autorizado | Versiones y referencias retiradas: propuesta conservar identificador no personal para integridad; plazo de borradores/historia editorial por decidir |
| Oferta/perfil público | Solo campos voluntarios y permitidos; estado C03 vigente | C03 rige sus datos de origen; nuevas condiciones e historia de oferta requieren plazo propio AT-04 |
| Búsqueda | Potencial dato sensible si se liga a persona/situación | Recomendación no guardar consultas ni historial personal en primer corte; retención nueva cero en aplicación propuesta, sin atribuirlo a logs técnicos de proveedores |
| Resultado derivado | Público por criterios, sin identificación de visitante | Sin persistencia nueva propuesta; no guardar perfiles personalizados ni fingerprint |

Las rutas públicas/filtros pueden existir en navegador/red/proveedor; no pedir
narrativa libre que se convierta en URL. Revisión de cachés y retirada debe impedir
que reaparezcan proyecciones retiradas al restaurar índice o build. C16 decide
métricas agregadas sin almacenar búsqueda individual. No se crea buscador externo,
indexación documental, embedding o proveedor por este checkpoint.

## Seguridad

Construir proyección permitida explícita en servidor; no usar SELECT amplio y
ocultar campos en React. Fuente privada no se vuelve pública por ser enlazada al
catálogo. Revalidar elegibilidad al solicitar atención: una ficha cacheada no
concede permiso ni acepta servicios. Diseñar invalidación de cache/índice de
retiros y límite de obsolescencia antes de activar caché de perfiles; no cambiar
los no-store actuales de identidad/API por optimizar cuota.

Acciones editoriales/publicación con capacidades nuevas explícitas por aprobar;
Arturo no las recibe automáticamente por review_professionals o admin proveedor.
Validar paginación, filtros, tamaños y escape de contenido para impedir inyección,
XSS y extracción no acotada. Rate limits/bot protection y su política C17 antes de
activar captación; no instalar Turnstile o ampliar permisos por inferencia.

## Impacto futuro

C04 puede referenciar oferta/versión elegida sin copiar relato a C06. C07 necesita
consultar disponibilidad real y no confirmar sobre datos de búsqueda. C08 añade
precio/tributación sin convertir cotización en autorización de cobro. C12 diseña
reputación antes de incorporarla al orden. Matching de solicitud requerirá nueva
matriz de divulgación y finalidad, no acceso automático al intake. SEO solo de
páginas públicas aprobadas; no perfiles en revisión, portal privado ni borradores.
Métrica propuesta: búsquedas con opciones elegibles, sin rastreo personal; definición
y agregación C16 todavía pendientes.

## Implementación propuesta

1. A0 resuelve AT-05, catálogo inicial/editor, ofertas y retención AT-04. Puede
   preparar fixtures sintéticos mientras faltan decisiones, sin simular catálogo real.
2. A1/A2 revisan términos y matriz de publicación; A3 define proyección, integridad
   de referencias/versiones y retiro antes de tablas. No índice externo inicial.
3. A4/A5 entregan lista/filtros/ficha/sin oferta y publicación explícita, usando
   contrato tipado revisado. C02/C03 y confianza profesional real son prerrequisitos.
4. A7/A2 negativos: perfil no revisado o no publicado; retiro entre lista y solicitud;
   consulta privada reflejada en URL/log; dato interno en ficha; cotización mostrada
   como gratis; filtro inválido o jurisdicción relajada; cursor fuera de límites;
   XSS en texto; orden por pago involuntario; caché/índice/restore resucita retirada.
5. Done exige oferta real verificable, ausencia de fuga, estados sin oferta y
   retirada comprobada; pantalla de catálogo con mocks no constituye marketplace.

No esquema, código, pruebas funcionales, publicación de perfiles ni datos reales
ejecutados en esta entrega documental.
