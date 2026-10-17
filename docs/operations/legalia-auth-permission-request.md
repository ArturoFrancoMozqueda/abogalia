# Consulta técnica preparada para Supabase

Este texto está preparado para que Arturo lo envíe mediante su soporte autorizado.
No se envió una consulta ni se contactó a terceros. No adjuntar secretos, filas de
usuarios o sesión, contraseñas, DSN privados, OTP, cookies o capturas de claves.

> Proyecto Legalia: spohytnxscljtitvmdab, PostgreSQL 17.11, Free.
> Nuestro backend debe comprobar la existencia de la sesión Auth antes de autorizar
> operaciones, mediante un rol PostgreSQL independiente y mínimo.
> El operador postgres tiene SELECT WITH GRANT OPTION sobre auth.sessions(id, user_id),
> pero carece de USAGE WITH GRANT OPTION sobre auth. El esquema pertenece a
> supabase_admin y postgres no puede SET ese rol.
> ¿Cuál es el mecanismo soportado para que un grantor legítimo conceda únicamente
> USAGE del esquema auth y SELECT de esas dos columnas al rol dedicado, sin
> service_role, membresías en roles administrados, BYPASSRLS ni acceso general?
> El rol dedicado todavía no está creado porque la receta falla antes de hacerlo
> al detectar que el grantor no tiene capacidad. No queremos sortear ese control.
> Si la plataforma no soporta este patrón, agradeceremos indicar una alternativa
> oficial que permita verificar revocación de una sesión concreta, sin elevar los
> permisos generales del backend.

Revisar respuesta con coordinación antes de aplicar cambios. Un diagnóstico de
permisos no autoriza copiar secretos ni crear funciones SECURITY DEFINER para
eludirlos. [Estado y evidencia](legalia-supabase-setup.md).
