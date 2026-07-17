# Brainstorming de Arquitectura Técnica

## Propósito

Este documento no define un stack final.

La arquitectura técnica se decidirá mediante sesiones de diseño, pruebas de concepto y Architecture Decision Records.

## Principios

- Evitar decisiones irreversibles.
- Diseñar por dominios.
- Preferir simplicidad operativa.
- Escalar cuando exista evidencia.
- Separar operación transaccional y analítica.
- Instrumentar desde el inicio.
- Priorizar seguridad.
- Controlar costos.
- Automatizar despliegue y pruebas.

## Preguntas de arquitectura

### Aplicaciones

- ¿Una aplicación o varias?
- ¿Web responsive?
- ¿Aplicaciones móviles?
- ¿Portal cliente?
- ¿Portal abogado?
- ¿Portal despacho?
- ¿Admin independiente?

### Backend

- ¿Monolito modular?
- ¿Servicios?
- ¿Serverless?
- ¿Contenedores?
- ¿Arquitectura híbrida?
- ¿Qué dominios requieren aislamiento?
- ¿Qué capacidades requieren colas?

### Lenguajes

- ¿TypeScript?
- ¿Python?
- ¿Java?
- ¿Go?
- ¿Combinación?
- ¿Qué experiencia tiene el equipo?
- ¿Qué costo operativo implica?

### Datos

- ¿PostgreSQL?
- ¿Base documental?
- ¿Motor de búsqueda?
- ¿Warehouse?
- ¿Lakehouse?
- ¿Event store?
- ¿Vector database?
- ¿Cache?

### Integraciones

- Pagos.
- Calendario.
- Correo.
- WhatsApp.
- Videollamada.
- Firma.
- Facturación.
- Verificación.
- Identidad.
- Almacenamiento.

### Infraestructura

- AWS.
- Azure.
- Google Cloud.
- Vercel.
- Fly.io.
- Supabase.
- Kubernetes.
- Plataformas administradas.
- Multi-cloud.

### Seguridad

- IAM.
- MFA.
- SSO.
- Secrets.
- KMS.
- WAF.
- SIEM.
- DLP.
- Backups.
- DR.

### Observabilidad

- Logs.
- Métricas.
- Trazas.
- Auditoría.
- Alertas.
- SLO.
- Error tracking.
- Product analytics.

## Pruebas de concepto sugeridas

- Auth multi-tenant.
- Reserva concurrente.
- Pago y reembolso.
- Agenda e integración.
- Enrutamiento de notificaciones.
- Almacenamiento seguro.
- Auditoría.
- Event tracking.
- Search.
- Matching.
- IA con datos anonimizados.

## ADRs necesarios

- Arquitectura de aplicación.
- Estrategia multi-tenant.
- Lenguaje backend.
- Base de datos.
- Almacenamiento.
- Integración de pagos.
- Mensajería.
- Analítica.
- Identidad.
- Despliegue.
- Observabilidad.
- IA.
