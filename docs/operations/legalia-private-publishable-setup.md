# Configuración privada de la publishable — Legalia

Destino vigente: proyecto `spohytnxscljtitvmdab`. D-039/D-040 aprobados.
Este procedimiento no habilita Identity ni acredita correo/revocación reales.

1. En el panel del proyecto correcto, el operador abre Settings → API Keys y
   copia únicamente la clave identificada como **Publishable**, con prefijo
   `sb_publishable_`. El agente no abre esta pantalla ni inspecciona su contenido.
2. En su editor privado, abre `/Users/arturo/Documents/repos/abogalia/.env`.
   Localiza `ABOGALIA_SUPABASE_PUBLISHABLE_KEY=` y pega el valor después del `=`.
   Una línea, sin comillas, comentarios inline o expansión de shell. No sustituir
   el archivo completo ni duplicar la variable. Nunca editar `.env.example` con valores.
3. Conserva `ABOGALIA_IDENTITY_ENABLED=0` y `ABOGALIA_AUTH_EMAIL_READY=0`.
   El destino público es `ABOGALIA_SUPABASE_URL=https://spohytnxscljtitvmdab.supabase.co`.
   Los demás campos privados requieren su preparación separada; no copiar credenciales
   administrativas o la clave Resend a este archivo.
4. Guarda el archivo y ejecuta únicamente:

   ```sh
   chmod 600 /Users/arturo/Documents/repos/abogalia/.env
   ```

5. Comunica solo «publishable guardada». No compartir capturas, valores, contraseñas,
   tokens o códigos. El coordinador comprueba permisos/exclusión de Git por metadata;
   no lee el contenido del archivo real.

La publishable es pública según el proveedor, pero su configuración permanece
local. No se requiere `service_role`, clave secret ni DSN SQL de Auth para el modo
HTTP explícito. `ABOGALIA_AUTH_SESSION_CHECK_DSN` es legado opcional no inyectado.
La API aún necesita su DSN de rol runtime mínimo/TLS, firma CSRF y cifrado Fernet.
Esos valores se preparan privadamente y no se pasan como argumentos visibles.

Antes de activar Identity faltan pruebas reales de sesión/revocación y preparación
privada de runtime. EMAIL_READY solo pasa a 1 después de comprobar entrega OTP.
No ejecutar `source .env`, publicar el archivo o reiniciar servicios existentes
por inferencia. No cargar claves privadas en variables `VITE_*`.

## Correspondencia exacta de cada valor

| Origen | Variable privada exacta |
|---|---|
| Publishable del proyecto Legalia | ABOGALIA_SUPABASE_PUBLISHABLE_KEY |
| URL pública del proyecto | ABOGALIA_SUPABASE_URL |
| PostgreSQL Session pooler + rol runtime y contraseña propios + TLS validado | ABOGALIA_DATABASE_DSN |
| Generación criptográfica local de firma | ABOGALIA_CSRF_KEY |
| Generación criptográfica local Fernet | ABOGALIA_SESSION_CIPHER_KEY |

Valores públicos locales: ENVIRONMENT=development, WEB_ORIGIN=http://127.0.0.1:5190.
IDENTITY_ENABLED=0 y AUTH_EMAIL_READY=0 hasta la aceptación real; siempre con prefijo
ABOGALIA_. AUTH_SESSION_CHECK_DSN queda vacía en modo HTTP.

El operador puede preparar las dos claves locales nuevas, **solo si todavía no
configuró esas variables**, ejecutando desde la raíz:

```sh
apps/api/.venv/bin/python scripts/prepare_identity_private_keys.py
```

Escribe únicamente `.env.identity-generated`, excluido de Git y permiso0600.
No lee ni cambia `.env`, no imprime valores y se niega a sobreescribir el archivo.
El operador abre el archivo en su editor privado y copia cada valor a la variable
**del mismo nombre** en `.env`. No sustituir claves existentes: una clave de cifrado
nueva no descifra sesiones creadas con la anterior. El coordinador ejecutó el generador localmente al confirmar por metadata que
el destino no existía. Solo se informaron estado y nombres; no se leyó el archivo
generado ni el .env real, y no se modificó configuración existente.

El navegador confirmó en2026-10-14 Session pooler de Legalia:
host `aws-0-us-east-1.pooler.supabase.com`, puerto5432, basepostgres. El usuario de
runtime es `abogalia_identity_runtime.spohytnxscljtitvmdab`. Connect muestra por
defecto al administrador postgres: no copiar esa cadena tal cual. Contraseña del
rol runtime y confianza TLS requieren preparación privada por el operador.
