# Legalia — C03 y directorio: incremento local2026-10-17

Rama `feature/marketplace-c03`, base `main` `a6f172c` (PR1 integrada). Arturo
aprobó directorio/flujo y pidió continuar con agentes. No nueva autorización de
retención jurídica, roles reales o servicios. Regla permanente de comprobar
cuenta/proyecto/entorno Legalia antes de mutaciones externas incorporada a AGENTS.md.

## Implementado y revisado

- `professional_contexts/publication.py`: dominio puro C03 de declaración, envío
  a revisión, decisión explícita por revisor ajeno/asignado, activación de práctica,
  publicación voluntaria y recepción separadas. Versiones/CAS, revisión ligada a
  datos y retirada/suspensión; cambios invalidan revisión y publicación. Proyección
  pública exacta sin cédula, nombre legal ni identificadores privados.
- `marketplace/directory.py` y `router.py`: rutas GET de lista/ficha, filtros
  nombre/ámbito NFC/casefold literales,80 caracteres combinados, query2048bytes,
  paginación20/máximo50 y cursor cifrado autenticado efímero ligado a criterios.
  Anchor retirado/cambiado fuerza reinicio409; reinicio del proceso invalida cursor.
- Fuente inyectada debe mantener/revalidar elegibilidad hasta serialización. Sin
  fuente real devuelve503; no fixtures, catálogo vacío ficticio ni lectura del draft
  privado. Límite técnico1000 filas falla503 sin truncar si el adapter lo supera;
  antes de escala real, consulta acotada/indexada y keyset de base requieren revisión.
- `main.py`: integra el router y fuente opcional, deshabilitada en runtime por
  defecto. Errores desconocidos de esa familia saneados y sin caché.
- Filtro de acceso excluye criterios/rutas de catálogo y solicitudes de logs;
  respuesta pública sin cookies, Authorization, caché ni eco de input.

## Equipo y revisión

| Agente | Archivos exclusivos | Evidencia |
|---|---|---|
| planning_services | publication.py y test_professional_publication.py |57 nuevos tests de reglas C03; dominio previo intacto |
| planning_attention | marketplace y test_marketplace_directory.py |63 tests de API/proyección/filtros/cursor/retirada/errores |
| planning_operations | marketplace-retention-decision.md y revisión estática independiente |127 tests focales incluidos filtros de logs pasan; sin bloqueantes en alcance cerrado |
| A0 | Integración main/logging,7 tests de logs, aprobaciones/reglas/documentación | Suite completa714 tests contra PostgreSQL aislado pasa |

`make check-api` pasó: Ruff, formato, dependencias e importación. Suite completa
con PostgreSQL temporal aislado:714passed (587 anteriores +127 nuevas). Auth es
transporte sintético; fuente del directorio es sintética bajo guard controlado.
No equivalen a aceptación de Auth/SMTP, consulta oficial, permisos reales,
publicación de profesionales o aislamiento de un futuro adapter no escrito.

## Qué todavía impide declarar C03 o marketplace terminados

1. Adaptar modelo/persistencia C03 ampliado y autorización transaccional de revisión/
   publicación. El agregado privado actual conserva su esquema/contrato sin cambios.
2. Implementar invitaciones, membresía, capacidades, salida y relevo C03 aprobados,
   con almacenamiento/HTTP/UX y pruebas de aislamiento; no se sustituyen por este
   dominio de práctica propia ni se excluyen del producto.
3. Procedimiento real de cotejo/titularidad/suplantación y revisión jurídica; cuenta
   APP confirmada/MFA y concesión manual limitada de revisor. Ninguna fixture
   concede capacidad a Arturo ni valida su propia identidad profesional.
4. Aceptación C02 real de correo/MFA/revocación y mantenimiento/restore. C03 remoto
   todavía no instalado; este incremento no ejecuta SQL ni concede privilegios.
5. Adapter real del catálogo: sólo proyecciones elegibles, revalidadas frente a
   retirada, nunca SELECT amplio de usuarios o draft convertido en público.
6. [Retención C04](marketplace-retention-decision.md): aprobar plazos, lectores,
   intención idempotente caducable, bloqueo legal y backups; después concretar
   modelo/matriz antes de tablas de solicitudes. Flujo aprobado no fija esos plazos.
7. UI del directorio/solicitud y recorrido navegador→API→datos, una vez conectadas
   las piezas reales. No se publica un formulario que aparente entrega inexistente.

**LEGAL REVIEW REQUIRED** para revisión profesional y tratamiento jurídico reales.
No se cambió proveedor, gasto, cuenta ni recurso Kova; no se leyó .env o datos
reales ni se ejecutaron migraciones, correos, concesiones o despliegues.

Antes de commit/push: enlaces/estructura/diff y escaneo redactado de fuentes e
historia. El registro de integración no convierte los gates pendientes en Done.
