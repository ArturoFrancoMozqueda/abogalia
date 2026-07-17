# Arquitectura de Datos

## Objetivo

Diseñar un modelo de datos que soporte operación, analítica, auditoría, cumplimiento, inteligencia de matching e inteligencia artificial.

## Dominios

- Identidad.
- Organizaciones.
- Profesionales.
- Clientes.
- Catálogo legal.
- Intake.
- Matching.
- Agenda.
- Reservas.
- Consultas.
- Pagos.
- Suscripciones.
- Reputación.
- Documentos.
- Consentimientos.
- Notificaciones.
- Auditoría.
- Analítica.

## Entidades principales

- User.
- ClientProfile.
- LawyerProfile.
- LawFirm.
- Office.
- Membership.
- Role.
- Credential.
- PracticeArea.
- LegalIssue.
- Jurisdiction.
- Service.
- AvailabilityRule.
- AvailabilityException.
- LegalRequest.
- IntakeSubmission.
- LawyerMatch.
- Booking.
- Consultation.
- Payment.
- Refund.
- Review.
- Subscription.
- Document.
- Consent.
- Notification.
- AuditEvent.
- ProductEvent.

## Separaciones conceptuales

### LegalRequest

Necesidad expresada por el usuario.

### IntakeSubmission

Respuestas a un formulario específico.

### LawyerMatch

Relación evaluada entre solicitud y abogado.

### Booking

Reserva.

### Consultation

Servicio realizado.

### LegalMatter

Asunto formal posterior a la consulta.

No debe utilizarse una sola entidad genérica `case`.

## Data ownership

Cada dominio debe tener ownership claro.

Ejemplo:

| Dominio | Owner funcional |
|---|---|
| Identity | Plataforma |
| Lawyer profile | Profesional / operaciones |
| Legal catalog | Producto legal |
| Booking | Scheduling |
| Payment | Payments |
| Review | Trust |
| Analytics | Data |

## Datos sensibles

Clasificación:

- Públicos.
- Internos.
- Confidenciales.
- Sensibles.
- Altamente sensibles.
- Regulatorios.

## Retención

Definir políticas para:

- Prospectos no convertidos.
- Consultas.
- Documentos.
- Pagos.
- Auditoría.
- Sesiones.
- Eventos.
- Datos de IA.
- Datos eliminados.

## Calidad de datos

Dimensiones:

- Completitud.
- Validez.
- Unicidad.
- Integridad.
- Consistencia.
- Actualidad.
- Trazabilidad.
- Conformidad.

## Gobierno

- Diccionario.
- Catálogo.
- Linaje.
- Ownership.
- Clasificación.
- Accesos.
- Retención.
- Consentimiento.
- Auditoría.
