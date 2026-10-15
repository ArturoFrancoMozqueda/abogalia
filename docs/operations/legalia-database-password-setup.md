# Legalia — preparación privada de contraseña runtime

2026-10-15. C02 operativo ya aprobado; Arturo pidió establecer la contraseña del
rol y consumir la contraseña administrativa desde un archivo privado. No nuevos
roles, grants, proveedores, habilitación de Identity o cambios a otros proyectos.

## Certificado TLS

El error del operador fue `certificate verify failed` usando sslrootcert=system;
no demuestra contraseña incorrecta. Se descargó la CA pública de Supabase desde
su distribución HTTPS oficial, identificada en el código oficial del dashboard:

- [Configuración SSL](https://github.com/supabase/supabase/blob/master/apps/studio/components/interfaces/Settings/Database/SSLConfiguration.tsx).
- [URL de distribución](https://github.com/supabase/supabase/blob/master/apps/studio/hooks/custom-content/custom-content.json), ssl:certificate_url con entorno prod.
- [Guía PSQL](https://supabase.com/docs/guides/database/psql).

Archivo público: apps/api/certificates/supabase-prod-ca-2021.crt. SHA256:
700723581420dd1ac98fd7e9ac529f0ef210eadcaf87fc868a3ad7d114c2f3b7.
Se comprobó identidad CA, BasicConstraints CA:TRUE y TLS1.3 con validación de cadena
+hostname contra aws-0-us-east-1.pooler.supabase.com:5432. Solo SSLRequest/TLS:
sin startup PostgreSQL, usuario, contraseña, consultas SQL o datos reales.
No se modifica confianza global del equipo ni se degrada verify-full.

## Uso por el operador

1. Abrir el archivo privado `.env.database-setup`, creado vacío con permiso0600
   y exclusión Git. Pegar la contraseña **original administrativa de la base**
   únicamente después del signo igual de `ABOGALIA_SETUP_DATABASE_ADMIN_PASSWORD=`.
   Sin comillas añadidas; caracteres especiales se conservan literalmente, sin shell.
   No poner esa variable en el `.env` usado por la aplicación ni compartir su valor.
2. Tras revisión, ejecutar `apps/api/.venv/bin/python scripts/configure_identity_database_password.py`.
   También puede ejecutarlo el coordinador por autorización expresa de Arturo,
   consumiendo el archivo solo dentro del proceso y recibiendo estados redactados.
3. Solo el estado `runtime_password_set_and_verified` acredita que el cambio se
   confirmó y se pudo autenticar el rol runtime. Entonces abrir privadamente
   `.env.database-runtime` y copiar su línea **ABOGALIA_DATABASE_DSN completa** a
   la variable del mismo nombre en `.env`. No copiar la contraseña administrativa.
4. Mantener ABOGALIA_IDENTITY_ENABLED=0 y ABOGALIA_AUTH_EMAIL_READY=0 hasta los gates
   reales de Identity. El operador retira el archivo temporal administrativo de
   su equipo al terminar. No se borra automáticamente evidencia o configuración.

## Límites del ejecutor

Destino fijo Legalia spohytnxscljtitvmdab, host pooler confirmado, basepostgres,
puerto5432. Solo contraseña de abogalia_identity_runtime ya existente, previa
comprobación de identidad postgres y rol sin privilegios elevados ni membresías ascendentes de ningún tipo.
No grants, creación de roles, migraciones, lectura de usuarios o datos jurídicos.
CA pública fijada por hash; verify-full, clientcertdisable y passfiledevnull.
Retira nombres PG* heredados sin leer sus valores y no carga configuración.env API.

Genera contraseña runtime aleatoria URL-safe, conserva candidato en archivo nuevo
0600/excluido ANTES del cambio remoto y envía solo verificador SCRAM-SHA-256 al SQL,
como mecanismo equivalente a \password. No contraseña en claro en SQL/argumentos/
logs/salidas. La autenticación usa únicamente el flujo del driver hacia ese destino.
Conserva contraseña candidata ante resultado incierto; no sobreescribe ni vuelve a
rotar automáticamente al reejecutar. Si falla, no copiar la salida como configuración
confirmada: revisar estado sin mostrar valores ni resetear otras credenciales.
No modifica ni lee el `.env` real, ni habilita la API. El archivo administrativo
queda separado y nunca lo carga el launcher de aplicación.

Evidencia: dieciséis pruebas con conexiones simuladas/archivos sintéticos y una
prueba de membresías PostgreSQL aislado pasan; integración A0:484 pruebas pasan.
Revisión independiente A2 sin bloqueantes. Lint/formato/dependencias/importación
de API pasan. Los negativos
cubren input seguro/literal, permisos, links/tamaño, rol/TLS/destino, verificador,
salida privada/nunca lectura.env y negativa de repetición/CA alterada/rol elevado.
No acredita cambio de contraseña remoto: pendiente de input privado del operador.
