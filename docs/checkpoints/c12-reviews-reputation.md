# C12 — Reseñas, respuesta y reputación

Fecha: 2026-10-16. Estado: **Proposed; no aprobado para implementar**.
No existe política aprobada de elegibilidad, puntuación, moderación ni publicación.

## Lo que entiendo

La persona debe poder reconocer experiencia verificable sin publicar detalles de su
situación jurídica. La plataforma necesita distinguir prestación real, desacuerdo,
conflicto de interés y abuso. Pago no demuestra por sí solo atención efectiva; la
reputación no debe revelar quién fue cliente de qué asunto por defecto.

## Decisiones tomadas

- D-011 busca claridad/continuidad; D-014 y D-015 fijan público y relación de servicio.
- Perfil profesional aprobado para publicación en C03 no certifica opiniones ni
  calidad jurídica. No hay aprobación de ranking, patrocinios o compra de reputación.
- C12 pertenece al backlog; esa inclusión no aprueba publicar datos del cliente.

## Decisiones pendientes

| ID | Opciones y recomendación propuesta | Bloquea |
|---|---|---|
| REV-01 | Consulta completada C07, relación cerrada C05 o ambas; recomendar evidencia de prestación y máximo una reseña por experiencia elegible, no solo por pago | Elegibilidad y fuentes |
| REV-02 | Texto/puntuación/identidad pública, ventana y edición; recomendar publicación mínima sin identidad de cliente por defecto, sujeto a revisión | UX y datos públicos |
| REV-03 | Moderación previa o posterior, responsables, motivos, apelación y conflicto de interés; recomendar cola previa antes de habilitar reseñas públicas | Operación C17 y permisos |
| REV-04 | Método de agregación/muestra mínima, exclusiones, respuesta profesional y efecto en ranking; recomendar separar aprobación de reseñas y cualquier ranking | Métricas visibles |
| REV-05 | Retención de borradores, retiradas, apelaciones y evidencia privada; derecho a retirar/corregir conforme a revisión | Persistencia y eliminación |

Opiniones, publicidad profesional, difamación, datos sensibles y remedios:
**LEGAL REVIEW REQUIRED**. No se realiza asesoría jurídica ni se afirma legalidad.

## Diseño propuesto

| Entidad | Propiedad y relación | Estados propuestos |
|---|---|---|
| ReviewEligibility | Cuenta autora + prestación tipada C07/C05 + destinatario profesional | eligible, used, expired, revoked |
| Review | Cuenta autora; vínculo privado a experiencia; proyección pública separada | draft, submitted, under_review, published, rejected, withdrawn |
| ReviewRevision | Versiones de texto/puntuación, autor y fecha; no sobrescribir publicada | proposed, accepted, rejected |
| ProfessionalResponse | Una reseña y actor profesional autorizado, no cliente | draft, submitted, published, withdrawn |
| ModerationDecision | Actor/capacidad y motivo estructurado; evidencia privada mínima | pending, decided, appealed, superseded |
| ReputationSnapshot | Agregado derivado de reseñas actualmente elegibles/publicadas | current, invalidated, recomputing |

Elegibilidad calculada en servidor con fuente de prestación; cliente no crea su propio
recibo de atención ni reseña a sí mismo. Un reembolso/disputa no elimina automáticamente
una reseña: la política aprobada distingue atención, devolución y abuso. Relación de
servicio permanece privada incluso cuando exista reseña visible. Editar texto genera
revisión; la edición no elude moderación ni se publica automáticamente. Retirada deja
de contribuir al agregado, con historial mínimo según REV-05.

Moderación usa razones comprobables y canales separados de soporte jurídico. Operador
sin conflicto revisa una proyección mínima; no obtiene expediente completo. Apelación
registra decisión nueva, responsable y motivo; no borra evidencia anterior. Responsables
y ventanas quedan pendientes REV-03, sin SLA inventado. No IA de moderación añadida.

API candidata: consultar elegibilidad propia, guardar/enviar reseña, retirar propia,
reportar contenido, publicar respuesta y resolver/apelar por rutas específicas. Público
recibe solo proyección publicada y paginada; ningún ID de solicitud/reserva/asunto,
email, fecha de consulta exacta o identidad interna enlazable. Formulario explica qué
será público y prohíbe detalles identificables del asunto; el filtrado técnico no
sustituye revisión. No se usa una mala calificación como rechazo automático al profesional.

## Datos afectados

Texto de opinión puede contener datos sensibles aunque su finalidad sea pública;
proyección pública requiere consentimiento/política aprobados y revisión. La prueba
privada de elegibilidad, cuenta y relación es información restringida. Historial de
moderación debe evitar reproducir contenido retirado en auditoría general.

Retención **pendiente REV-05** por estado/categoría. C02 30/90 no autoriza conservar
reseñas indefinidamente ni eliminar automáticamente prueba de apelación. Definir
anonimización/retirada tras cierre de cuenta y obligaciones pendientes; backups según
operación aprobada. Contar reseñas no autoriza instrumentar identidades en analytics.

## Seguridad

Propiedad/experiencia/contexto verificados en servidor; anti-duplicados concurrente,
rate limits y autorización por objeto. Moderador no revisa reseña propia, de su práctica
o cuando tenga conflicto definido por política. El profesional no modifica reseña del
cliente ni suprime críticas a voluntad. Renderizar texto seguro sin HTML/script; límites
de longitud y rechazo de enlaces/adjuntos según política a aprobar. Reportes no exponen
la identidad del denunciante al profesional. Auditoría de intervención mínima.

## Impacto futuro

Ranking C06 no consume ReputationSnapshot hasta definir muestra, cálculo y sesgos.
Suscripción/comisión no compra reseñas o moderación favorable. Canales de disputa
financiera C08 y apelación C12 conservan finalidad y permisos diferentes.

## Implementación propuesta

1. A1/A2/C17 cerrar REV-01..05; A3 modelo y proyección pública aprobados antes de SQL.
2. A4 elegibilidad/transiciones/moderación; A5 experiencia privada y pública accesible;
   A7 verificación de privacidad, concurrencia y cálculo reproducible.
3. Ensayo sintético y revisión de carga operativa antes de publicación real.

Negativos: pago sin atención no genera automáticamente elegibilidad; una prestación
no produce dos reseñas; IDs ajenos no se enumeran; editar/recurrir no publica sin revisar;
respuesta profesional no revela asunto; retirada recalcula agregado; operador en conflicto
no decide; cierre de cuenta tiene resultado definido; reseña retirada no sigue en caché
propia/indexación según política. Ninguna reseña fue creada o publicada en esta entrega.
