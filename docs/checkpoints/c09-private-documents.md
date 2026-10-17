# C09 — Documentos privados y versiones

Fecha: 2026-10-16. Estado: **Proposed; no aprobado para implementar**.
D-015 conserva documentos básicos; D-022 aplaza procesamiento documental con IA.

## Lo que entiendo

Cliente y profesional deben compartir el archivo correcto dentro de una relación
autorizada C05, con versiones distinguibles, retiro de acceso y eliminación trazable.
No es un repositorio público ni un archivo compartido por todo el despacho. Cargar
un archivo no concede permiso a otro miembro ni habilita enviar su contenido a IA.

## Decisiones tomadas

- Almacenamiento básico forma parte de la visión D-015 y se conserva en D-022.
- OCR, embeddings, RAG, extracción y clasificación documental con IA están aplazados.
- Las aprobaciones de Supabase Auth/PostgreSQL no aprueban un proveedor Storage,
  región de objetos, antivirus, cuotas, precio ni retención de contenido jurídico.

## Decisiones pendientes

| ID | Alternativas y recomendación propuesta | Bloquea |
|---|---|---|
| DOC-01 | Comparar almacenamiento privado mediado por API y otros mecanismos privados compatibles; recomendar API como autoridad de autorización, proveedor por decidir | Proveedor, región, tratamiento y costo |
| DOC-02 | Autor del archivo conserva control individual o comparte conforme a relación C05; recomendar alcance explícito por relación/visibilidad, sin heredar todo el despacho | Matriz y acceso tras salida/cierre |
| DOC-03 | Definir tipos, tamaño, cantidad, versiones y cuota; recomendar allowlist pequeña y bloquear archivo antes de servir si validación/escaneo falla | Carga y cuarentena |
| DOC-04 | Fijar plazos separados para cuarentena, rechazados, versiones, relación cerrada, borrado y backups; excepción de conservación con autoridad/motivo | Modelo y operación de eliminación |

Acceso, propiedad jurídica, transferencias y conservación: **LEGAL REVIEW REQUIRED**.

## Diseño propuesto

Flujo: seleccionar relación → elegir visibilidad permitida → validar cuota/permiso en
API → reservar carga → objeto privado en cuarentena → verificar bytes/tipo/tamaño →
escaneo aislado aprobado → liberar versión limpia → descargar previa autorización.
No aparece botón de descarga mientras estado sea pendiente, bloqueado o desconocido.
Si no hay escaneo aprobado/operativo, no habilitar liberación de archivos para usuarios.
Un timeout no equivale a clean. No se aprueba antivirus o nuevo servicio en este diseño.

| Entidad | Propiedad y relaciones | Estados propuestos |
|---|---|---|
| Document | Un contexto y una relación C05; creador atribuido, no dueño universal | active, restricted, deletion_requested, deleted |
| DocumentVersion | N inmutables por documento; objeto privado único y metadatos mínimos | upload_reserved, quarantined, scanning, available, rejected, deletion_pending, deleted |
| DocumentAccessRule | Alcance explícito de relación/actor/acción, referenciado a C05 | active, revoked |
| ScanResult | Resultado por versión, motor/configuración y hora; sin contenido | clean, blocked, error, expired |
| DeletionReceipt | Evidencia mínima sin contenido; cubre objeto, versiones y derivados | pending, retry_required, verified |

Invariantes propuestos de DOC-02: compartir nunca amplía la audiencia más allá de la
participación y permisos vigentes definidos por C05, aunque lo soliciten el uploader o
un administrador del despacho. La autoría de carga no permite incorporar terceros a
la relación. Descargar después del cierre requiere una política expresa aprobada en
C05/C09; no heredar acceso por haber participado antes ni mantenerlo indefinidamente.

No se sobreescribe una versión disponible. Cambiar archivo crea versión nueva; restaurar
una anterior crea referencia explícita y conserva historial. El nombre visible no se
usa como clave del objeto ni ruta de disco. Claves opacas; ubicación/bucket no aparecen
en listados públicos. Firma de URL, si se aprueba, tendrá alcance exacto/TTL por fijar:
no garantiza revocación inmediata durante su vigencia. Recomendar descarga mediada por
API para datos que requieran reevaluación por petición; decidir costo/latencia después.

API candidata: crear reserva de carga desde relación, completar carga de versión,
consultar estado/listado autorizado, descargar versión y solicitar eliminación. No
aceptar `bucket`, `object_key`, propietario o scanner-status como autoridad del cliente.
UX: versión/autor/hora visibles según permiso, progreso sin publicación prematura,
cuarentena legible, cuota/error y reintento consciente. Cliente no ve notas internas
ni nombres de otros archivos por consultar un ID no autorizado.

## Datos afectados

Contenido jurídico altamente restringido; metadatos (nombre/tamaño/tipo/autor/relación)
también restringidos y potencialmente identificables. Guardar checksum interno para
integridad de versión, no para deduplicar archivos entre clientes/contextos. Historial
de cargas, compartición, revocación y borrado conserva solo mínimo acordado.

Retención nueva **pendiente DOC-04**: 30/90 de identidad no cubre documentos. Diseñar
eliminación de todas las versiones, cuarentena y copias/derivados; marcar borrado solo
tras confirmación del almacenamiento. Documentar expiración/recuperación en backups
conforme al checkpoint operativo; no prometer destrucción instantánea de backups.

## Seguridad

Autorización vigente por objeto en cada petición y aislamiento en base y almacenamiento.
No buckets públicos, permisos administrativos como solución universal ni descargas
cacheables en CDN. Subidas directas, si se eligen, solo a destino de cuarentena acotado;
ningún secreto ni llave administrativa Storage llega al cliente. Una URL firmada futura
es una capacidad portadora sensible: no se registra, no se comparte fuera de su flujo
y su alcance/vigencia siguen pendientes de aprobación. RLS/grants y política de objetos requieren
pruebas independientes, sin asumir que uno sustituye al otro.

Validar extensión/MIME y contenido real, tamaños acumulados y cuota concurrente; rechazar
path traversal, ejecutables y tipos no admitidos. Archivos comprimidos y contenido activo
se mantienen fuera hasta aprobar análisis/límites específicos. Descarga como adjunto,
`nosniff` y caché privada/no-store; no previsualización HTML/SVG ejecutable. Escáner aislado
sin acceso a otros objetos, secretos o red no necesaria. Logs no incluyen nombres,
contenido, URLs firmadas ni claves de objetos. Un moderador general no obtiene contenido.

## Impacto futuro

C18 firma/expediente requiere nuevos contratos de evidencia y custodia. IA documental
permanece aplazada aunque existan archivos limpios. Exportación C19 y migración de
Storage necesitan reevaluar permisos, cifrado y retención; no heredan consentimiento.

## Implementación propuesta

1. Aprobar DOC-01..04 después de C05; modelar propietario, matriz y retención con A2/A3.
2. Adaptador local sintético de objetos/escáner, transacciones de cuota, cuarentena,
   versiones y borrado; UI con todos los estados. No credenciales remotas para diseño.
3. Aprobar proveedor/costo y verificar aislamiento remoto antes de habilitar cargas.

Negativos obligatorios: ID ajeno/nombre adivinable no revela nada; pérdida de membresía
impide nueva descarga; versión anterior no evita revocación; scanner caído no libera;
archivo poliglota/sobretamaño/ruta maliciosa no se sirve; dos cargas no exceden cuota;
fallo parcial al borrar mantiene pendiente; URL temporal no se registra; contenido
interno no aparece al cliente. No se probaron cargas ni borrados en esta planificación.
