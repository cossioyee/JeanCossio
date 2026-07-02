# hogar-bot — Guía: levantar el bot en otra PC

Qué hacer cuando apagas el bot en tu laptop de desarrollo y lo quieres
levantar en una máquina distinta.

## Lo que SÍ viaja en git

Clonar el repo trae todo el código, `docker-compose.yml`, `Makefile` y
`docs/`. No falta nada de eso.

## Lo que NO viaja en git (hay que llevarlo aparte)

| Archivo | Contiene | Cómo llevarlo |
|---|---|---|
| `.env` | Credenciales Twilio, ngrok, números de teléfono | Copiar manualmente por un canal seguro (AirDrop, gestor de secretos, USB). **Nunca por Slack/email/chat en texto plano.** |
| `data/hogar.db` | Tareas, historial de completaciones, personas ya seedeadas | Copiar el archivo si quieres conservar el historial; si no, se puede regenerar con `make db-reset` (pierdes las tareas configuradas y el historial). |

## Pasos en la máquina nueva

1. **Clonar el repo:**
   ```bash
   git clone <url-del-repo>
   cd hogar-bot
   ```

2. **Copiar `.env`** desde la laptop de desarrollo a la raíz del proyecto
   en la máquina nueva. Debe tener estas claves (ver `docs/architecture.md`
   para el detalle de cada una):
   ```
   TWILIO_ACCOUNT_SID=...
   TWILIO_AUTH_TOKEN=...
   TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
   NGROK_AUTHTOKEN=...
   JEAN_PHONE_NUMBER=whatsapp:+...
   ANELYS_PHONE_NUMBER=whatsapp:+...
   ```

3. **(Opcional) Copiar `data/hogar.db`** si quieres conservar las tareas
   y el historial ya configurados. Va dentro de la carpeta `data/` en la
   raíz del proyecto (créala si no existe: `mkdir -p data`).

4. **Instalar Docker Desktop** en la máquina nueva si no lo tiene, y
   asegurarse de que el daemon esté corriendo antes del siguiente paso.

5. **Levantar el stack:**
   ```bash
   make dev
   ```
   Si no copiaste `data/hogar.db`, este paso crea la DB vacía y corre el
   seed automáticamente (via el `lifespan` de `main.py`), usando los
   números de `JEAN_PHONE_NUMBER`/`ANELYS_PHONE_NUMBER` del `.env`.

6. **Obtener la nueva URL de ngrok** (cambia en cada máquina/reinicio,
   plan free):
   ```bash
   curl -s http://localhost:4040/api/tunnels | python3 -c "import sys,json; print(json.load(sys.stdin)['tunnels'][0]['public_url'])"
   ```
   O abre `http://localhost:4040` en el navegador.

7. **Actualizar el webhook en Twilio:** consola de Twilio → *Messaging →
   Try it out → Send a WhatsApp message* → pegar la nueva URL
   (`https://<nueva-url-ngrok>/webhook/twilio`) en **"When a message
   comes in"**, método `POST`. Este paso es obligatorio cada vez que
   cambia la URL de ngrok, sin importar en qué máquina corras el bot.

8. **Verificar que el sandbox siga activo:** el sandbox de Twilio expira
   la conexión de un número si pasan 72h sin actividad. Si `listo` o
   `mis tareas` no responden, primero revisa si hace falta reenviar
   `join <código-sandbox>` desde WhatsApp — no asumas que es un bug del
   bot.

## Apagar el bot en la laptop original

`docker compose down` detiene los contenedores sin borrar `data/hogar.db`
(el volumen está montado desde el filesystem local, no es un volumen
Docker). Si vas a mover el trabajo a la otra máquina y no quieres tener
dos `.env` con las mismas credenciales activas en paralelo, no hay
riesgo real: solo una instancia a la vez puede tener el webhook de
Twilio apuntando a ella, así que la otra simplemente no recibirá
mensajes aunque esté corriendo.

## Checklist rápido

- [ ] `.env` copiado a la máquina nueva
- [ ] `data/hogar.db` copiado (si quieres conservar historial)
- [ ] Docker Desktop corriendo
- [ ] `make dev` levantado sin errores
- [ ] URL de ngrok actualizada en la consola de Twilio
- [ ] Sandbox de WhatsApp sigue activo (`join <código>` si expiró)
