# hogar-bot — Recomendaciones de Diseño

Archivo acumulativo. Cada recomendación incluye el contexto, la decisión tomada y por qué importa.

---

## DB / Schema

### 1. Horarios de recordatorio en `settings`, no en `tasks`
**Contexto:** Se necesitan recordatorios a hora fija en v1, pero en v2 el sistema elegirá el horario óptimo por persona.
**Decisión:** Tabla `settings` con claves `morning_reminder_time` y `night_reminder_time`.
**Por qué:** Si los horarios vivieran en `tasks`, migrarlos en v2 requeriría alterar esa tabla. En `settings` el cambio de v1→v2 es solo "el scheduler deja de leer las claves fijas y calcula dinámicamente" — sin tocar el schema de tareas.

### 2. `sleep_start` / `sleep_end` en `persons` desde v1
**Contexto:** v2 necesitará no enviar recordatorios durante horas de sueño, y cada persona puede tener horarios distintos.
**Decisión:** Agregar ambos campos como `nullable` en `persons` desde ahora.
**Por qué:** Son baratos de agregar ahora y evitan una migración de schema en v2. En v1 simplemente se ignoran.

### 3. `next_due_at` materializado en `tasks`
**Contexto:** APScheduler necesita saber qué tareas están vencidas sin hacer joins complejos.
**Decisión:** Columna `next_due_at` en `tasks`, actualizada en cada completación como `completed_at + frequency_days`.
**Por qué:** Permite filtrar `Task.next_due_at <= now()` en una sola query, sin recalcular sobre el historial. Valor inicial: `created_at + frequency_days`.

### 4. Soft delete con `is_active` en `tasks`
**Contexto:** El usuario puede "eliminar" tareas por WhatsApp, pero el historial de completaciones debe preservarse para v2.
**Decisión:** `is_active = False` en lugar de `DELETE`.
**Por qué:** `task_completions` es append-only y referencia `task_id`. Borrar físicamente la tarea rompería esas FK y perdería datos de historial valiosos.

### 5. Dos FK a `persons` en `tasks` requieren `foreign_keys` explícito
**Contexto:** `Task` tiene `current_assignee_id` y `created_by_id`, ambas apuntando a `persons`.
**Decisión:** Declarar `foreign_keys=[current_assignee_id]` y `foreign_keys=[created_by_id]` en cada `relationship`.
**Por qué:** SQLAlchemy no puede inferir cuál FK usar cuando hay ambigüedad entre dos relaciones hacia la misma tabla. Sin esto lanza `AmbiguousForeignKeysError` al arrancar.

### 6. WAL mode + `foreign_keys=ON` via PRAGMA en cada conexión
**Contexto:** SQLite no activa foreign keys por defecto, y el modo de journal por defecto puede tener contención en lecturas.
**Decisión:** Listener `@event.listens_for(engine, "connect")` que ejecuta ambos PRAGMAs.
**Por qué:** El PRAGMA `foreign_keys=ON` no persiste entre conexiones en SQLite — debe setearse en cada una. WAL mejora lecturas concurrentes aunque en v1 no sean críticas.

---

## Arquitectura / API

### 7. Validación de firma Twilio en cada request
**Contexto:** El webhook de Twilio es un endpoint público.
**Decisión:** Validar el header `X-Twilio-Signature` con `twilio.request_validator.RequestValidator` antes de procesar cualquier mensaje.
**Por qué:** Sin validación, cualquiera podría enviar POST al endpoint y ejecutar lógica del bot. Twilio firma cada request con el auth token; si la firma no coincide, rechazar con 403.

### 8. Router delgado, lógica en `dispatcher`
**Contexto:** El router de Twilio recibe el mensaje y necesita decidir qué hacer.
**Decisión:** El router solo identifica al sender y delega a `bot.core.dispatcher.handle()`.
**Por qué:** Mantiene el router como capa HTTP pura (parsear form, validar firma, armar TwiML) y concentra las decisiones de negocio en `core`. Facilita testear el dispatcher sin simular requests HTTP.

### 9. Número de WhatsApp como identidad, sin login
**Contexto:** Solo 2 usuarios conocidos, sin necesidad de auth compleja.
**Decisión:** Lookup por `phone_number` en cada request. Si no existe en `persons`, rechazar con mensaje amigable.
**Por qué:** Elimina toda la capa de sesiones/tokens. El número de WhatsApp ya fue validado por Twilio; usarlo como identidad es suficiente para este scope.

---

## Dispatcher / Lógica de negocio

### 10. Detección de intents por regex antes de llamar a Claude API
**Contexto:** El dispatcher recibe mensajes de texto libre y debe decidir qué hacer.
**Decisión:** Primero se evalúan patrones regex (`_LISTO`, `_LISTAR`, `_NUEVA`, etc.). Solo si ninguno hace match se delega a Claude API.
**Por qué:** La llamada a Claude API tiene latencia y costo. Los comandos frecuentes ("listo", "mis tareas") son deterministas — no necesitan IA. Claude API queda reservada para parsear configuración de tareas donde el texto es verdaderamente libre.

### 11. Round-robin por orden de ID, no por campo dedicado
**Contexto:** Con 2 personas, el round-robin necesita saber quién sigue después del actual assignee.
**Decisión:** `_next_assignee()` consulta `Person` ordenado por `id` y avanza con módulo (`(idx + 1) % len(persons)`).
**Por qué:** Con 2 usuarios fijos no se justifica un campo `rr_position`. El orden por ID es estable y predecible. Si en v2 se agregan personas, solo hay que asegurarse de que su `id` refleje el orden deseado, o agregar `rr_position` entonces.

### 12. Verificación de admin en dispatcher, no en router
**Contexto:** Los comandos de configuración de tareas son solo para Jean (is_admin=True).
**Decisión:** El chequeo `if not sender.is_admin` vive en `dispatcher.py`, después de detectar el intent pero antes de llamar al parser.
**Por qué:** El router no sabe de lógica de negocio. Centralizarlo en el dispatcher permite testearlo sin simular requests HTTP.

### 13. `nullsfirst()` al ordenar tareas por `next_due_at`
**Contexto:** Tareas recién creadas sin completaciones tienen `next_due_at = NULL`.
**Decisión:** `.order_by(Task.next_due_at.asc().nullsfirst())` para que aparezcan primero.
**Por qué:** Sin `nullsfirst()`, SQLite coloca los NULL al final, lo que haría que una tarea nueva nunca se marque como "la más urgente". El comportamiento deseado es que una tarea sin fecha asignada se considere pendiente inmediatamente.

---

### 14. No mezclar `Form(...)` con `request.body()` en el mismo endpoint
**Contexto:** El webhook validaba la firma de Twilio leyendo el body raw con `await request.body()`, pero el endpoint también declaraba `From: str = Form(...)` y `Body: str = Form(...)` en la firma de la función.
**Decisión:** Eliminar los parámetros `Form(...)`; leer el body una sola vez y parsearlo manualmente con `urllib.parse.parse_qs`, reutilizando el mismo dict tanto para validar la firma como para extraer `From`/`Body`.
**Por qué:** FastAPI resuelve los parámetros `Form(...)` consumiendo el stream del request antes de ejecutar el cuerpo del handler. El `await request.body()` posterior encontraba el stream ya consumido y lanzaba `RuntimeError: Stream consumed`, devolviendo `500` en cada mensaje entrante — el bot nunca respondía.

### 15. `--proxy-headers --forwarded-allow-ips='*'` en uvicorn detrás de ngrok
**Contexto:** Con el fix de la decisión #14, el webhook pasó de `500` a `403 Forbidden` en todos los requests reales de Twilio.
**Decisión:** Agregar `--proxy-headers --forwarded-allow-ips='*'` al comando de uvicorn en `docker-compose.yml`.
**Por qué:** ngrok reenvía el tráfico al contenedor `bot` por HTTP plano dentro de la red de Docker, agregando el header `X-Forwarded-Proto: https`. Uvicorn por defecto solo confía en ese header si el request viene de `127.0.0.1`; como ngrok corre en otro contenedor con otra IP, lo ignoraba y reconstruía `request.url` con esquema `http://`. Twilio firma sobre la URL pública real (`https://...`), así que la validación de firma nunca coincidía. `forwarded_allow_ips='*'` es aceptable aquí porque solo hay un reverse proxy interno (ngrok) en la red de Docker, no tráfico público directo al puerto de uvicorn.

### 16. Números de teléfono de `seed.py` movidos a variables de entorno
**Contexto:** `seed.py` tenía los números reales de WhatsApp de Jean y Anelys hardcodeados en el código.
**Decisión:** Leerlos de `JEAN_PHONE_NUMBER` y `ANELYS_PHONE_NUMBER` en `.env`, con `RuntimeError` explícito si faltan.
**Por qué:** `.env` está en `.gitignore` y nunca se commitea; hardcodear PII (números de teléfono reales) en código versionado los deja en el historial de git permanentemente, incluso si luego se eliminan.

---

## Para v2 (pendientes de implementar)

- Leer `sleep_start`/`sleep_end` de `persons` en el scheduler para evitar recordatorios nocturnos
- Calcular horario óptimo de recordatorio basado en historial de `task_completions`
- Reenvío de recordatorio si la tarea queda vencida (campo `due_date` en completaciones)
- Mensajes generados dinámicamente con contexto histórico vía Claude API
