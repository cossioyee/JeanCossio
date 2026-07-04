# hogar-bot — Documentación de Arquitectura

## Índice
- [Stack y decisiones de diseño](#stack-y-decisiones-de-diseño)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Capa de base de datos](#capa-de-base-de-datos)
  - [Modelos](#modelos)
  - [Relaciones](#relaciones)
  - [Engine y sesión](#engine-y-sesión)
  - [Seed inicial](#seed-inicial)
- [Capa web / WhatsApp](#capa-web--whatsapp)
  - [Webhook de Twilio](#webhook-de-twilio---botwhatsapprouterpy)
  - [Dispatcher](#dispatcher---botcoredispatcherpy)
  - [Parser](#parser---botcoreparserpy)
  - [Sender](#sender---botwhatsappsenderpy)
- [Scheduler de recordatorios](#scheduler-de-recordatorios---botcoreschedulerpy)
- [Tests](#tests)
- [Convenciones](#convenciones)

---

## Stack y decisiones de diseño

| Decisión | Elección | Razón |
|---|---|---|
| Base de datos | SQLite | Solo 2 usuarios, sin concurrencia real |
| ORM | SQLAlchemy 2.x (mapped_column) | Type hints nativos, sin boilerplate |
| Identidad de usuario | Número de WhatsApp | Sin login; el número es la sesión |
| Asignación de tareas | Round-robin matemático | Sin IA en v1; alternancia estricta |
| Parser de texto libre | Claude API | Solo para interpretar comandos WhatsApp |
| Scheduler | APScheduler | Recordatorios a hora fija |
| Eliminación de tareas | Soft delete (`is_active=False`) | Preservar historial para v2 |
| Historial de completaciones | Append-only | Nunca se borra; base para aprendizaje en v2 |

---

## Estructura del proyecto

```
hogar-bot/
├── bot/
│   ├── core/
│   │   ├── dispatcher.py  # Routing de intents (listo, listar, nueva/editar/eliminar)
│   │   ├── parser.py      # Parseo regex de "nueva tarea X, cada N días"
│   │   └── scheduler.py   # APScheduler: recordatorios mañana/noche
│   ├── db/
│   │   ├── models.py      # Modelos SQLAlchemy
│   │   ├── database.py    # Engine, sesión, dependencia FastAPI
│   │   └── seed.py        # Seed idempotente (lee JEAN_PHONE_NUMBER / ANELYS_PHONE_NUMBER)
│   └── whatsapp/
│       ├── router.py      # Endpoint POST /webhook/twilio + validación de firma
│       └── sender.py      # Envío de mensajes salientes via Twilio REST
├── tests/                 # pytest — dispatcher y parser con DB SQLite en memoria
├── data/
│   └── hogar.db           # SQLite (generado en runtime, no commitear)
├── .env                   # Credenciales — nunca se commitea (ver .gitignore)
├── main.py                # FastAPI app, lifespan (create_tables + seed + scheduler)
├── docker-compose.yml     # bot + ngrok + adminer
└── docs/
    ├── architecture.md    # Este archivo
    └── recommendations.md # Decisiones de diseño con contexto y motivo
```

---

## Capa de base de datos

### Modelos

#### `Person` — `bot/db/models.py`

Representa a un usuario del bot. El `phone_number` en formato Twilio
(`whatsapp:+521...`) es la identidad: cada mensaje entrante se resuelve
contra este campo.

| Campo | Tipo | Notas |
|---|---|---|
| `id` | Integer PK | |
| `name` | String(100) | Nombre para mostrar en mensajes |
| `phone_number` | String(20) UNIQUE | Identidad del usuario |
| `is_admin` | Boolean | Puede crear/editar/eliminar tareas |
| `sleep_start` | Time nullable | Inicio de horas de sueño (para v2) |
| `sleep_end` | Time nullable | Fin de horas de sueño (para v2) |
| `created_at` | DateTime | |

**v2:** `sleep_start` y `sleep_end` ya están en schema. El scheduler de v2
los leerá para evitar enviar recordatorios en esa ventana por persona.

---

#### `Task` — `bot/db/models.py`

Una tarea del hogar configurable por WhatsApp. El campo `current_assignee_id`
es el estado del round-robin: al completarse la tarea se actualiza al otro
miembro. `is_active=False` equivale a eliminar sin perder historial.

| Campo | Tipo | Notas |
|---|---|---|
| `id` | Integer PK | |
| `name` | String(200) | Nombre de la tarea |
| `frequency_days` | Integer | Cada cuántos días se repite |
| `current_assignee_id` | FK → persons | Estado actual del round-robin |
| `created_by_id` | FK → persons | Quién configuró la tarea |
| `next_due_at` | DateTime nullable | Próximo vencimiento materializado |
| `is_active` | Boolean | False = tarea eliminada (soft delete) |
| `created_at` | DateTime | |
| `updated_at` | DateTime | Se actualiza automáticamente |

**`next_due_at`:** se calcula como `completed_at + frequency_days` al
registrar cada completación. El scheduler filtra `Task.next_due_at <= now()`
para saber qué tareas están vencidas. Valor inicial: `created_at + frequency_days`.

**Dos FK a `persons`:** SQLAlchemy requiere `foreign_keys=[...]` explícito
cuando hay más de una FK a la misma tabla.

---

#### `TaskCompletion` — `bot/db/models.py`

Registro inmutable de cada vez que alguien marcó "listo". **Nunca se borra.**
Su propósito doble: confirmar la completación en v1 y alimentar el modelo
de aprendizaje de patrones en v2.

| Campo | Tipo | Notas |
|---|---|---|
| `id` | Integer PK | |
| `task_id` | FK → tasks | |
| `person_id` | FK → persons | Quién completó |
| `completed_at` | DateTime | Timestamp de la completación |

---

#### `Setting` — `bot/db/models.py`

Key-value para configuración global del sistema.

| Campo | Tipo | Notas |
|---|---|---|
| `key` | String(100) PK | Nombre del setting |
| `value` | String(255) | Valor como string |

**Claves iniciales (seed):**

| key | Ejemplo de value |
|---|---|
| `morning_reminder_time` | `07:30` |
| `night_reminder_time` | `21:00` |

---

### Relaciones

```
Person ──< Task (current_assignee_id)
Person ──< Task (created_by_id)
Person ──< TaskCompletion
Task   ──< TaskCompletion
```

---

### Engine y sesión — `bot/db/database.py`

- **Archivo DB:** `data/hogar.db` (relativo a la raíz del proyecto)
- **WAL mode:** activado via PRAGMA en cada conexión nueva — mejora
  lecturas concurrentes aunque SQLite en v1 no las necesite estrictamente.
- **Foreign keys:** `PRAGMA foreign_keys=ON` en cada conexión — SQLite
  las ignora por defecto; sin esto las FK no se validan.
- **`check_same_thread=False`:** requerido por FastAPI que maneja requests
  en distintos threads con el mismo engine.
- **`get_db()`:** dependencia de FastAPI con `yield`; garantiza que la
  sesión se cierra aunque el handler lance excepción.

**Uso en un router FastAPI:**
```python
from fastapi import Depends
from sqlalchemy.orm import Session
from bot.db.database import get_db

@router.post("/webhook")
def webhook(db: Session = Depends(get_db)):
    ...
```

**Crear tablas al arrancar:**
```python
from bot.db.database import create_tables
create_tables()  # llamar en el startup event de FastAPI
```

---

### Seed inicial — `bot/db/seed.py`

Pobla la DB con los datos mínimos para arrancar. Es idempotente: si un
registro ya existe lo omite sin error. Se ejecuta automáticamente en el
`lifespan` de FastAPI (`main.py`) cada vez que arranca el contenedor.

**Ejecutar manualmente:**
```bash
python -m bot.db.seed
```

**Datos que inserta:**

| Tabla | Registro | Notas |
|---|---|---|
| `persons` | Jean | `is_admin=True`; número desde `JEAN_PHONE_NUMBER` |
| `persons` | Anelys | `is_admin=False`; número desde `ANELYS_PHONE_NUMBER` |
| `settings` | `morning_reminder_time` | `07:30` por defecto |
| `settings` | `night_reminder_time` | `21:00` por defecto |

**Números de teléfono vía variables de entorno:** `seed.py` lee
`JEAN_PHONE_NUMBER` y `ANELYS_PHONE_NUMBER` de `.env` (nunca hardcodeados
en el código). Si faltan, `seed.py` lanza `RuntimeError` explícito en vez
de insertar un placeholder. Formato esperado: `whatsapp:+<código país><número>`.

---

## Capa web / WhatsApp

### Webhook de Twilio — `bot/whatsapp/router.py`

`POST /webhook/twilio` es el único punto de entrada de mensajes. Flujo:

1. Lee el body raw una sola vez (`await request.body()`) y lo parsea a
   dict con `urllib.parse.parse_qs` — **no** se declaran `From`/`Body`
   como `Form(...)` en la firma del endpoint, porque FastAPI consumiría
   el stream antes de poder leerlo de nuevo para validar la firma
   (ver [decisión #14](recommendations.md) sobre el bug `RuntimeError: Stream consumed`).
2. Valida `X-Twilio-Signature` con `twilio.request_validator.RequestValidator`
   contra la URL completa del request. Si no coincide → `403`.
3. Busca al remitente por `From` en `persons`. Si no existe → mensaje
   amigable de "no estás registrado", sin tocar el dispatcher.
4. Delega el texto (`Body`) a `bot.core.dispatcher.handle()`.
5. Devuelve la respuesta como TwiML (`MessagingResponse`).

**Detrás de un reverse proxy (ngrok):** uvicorn necesita `--proxy-headers
--forwarded-allow-ips='*'` para confiar en el `X-Forwarded-Proto: https`
que reenvía ngrok; sin esto reconstruye la URL como `http://` y la firma
de Twilio (calculada sobre `https://`) nunca valida (ver
[decisión #15](recommendations.md)).

---

### Dispatcher — `bot/core/dispatcher.py`

Recibe el mensaje ya limpio y decide qué handler ejecutar, por orden de
prioridad con regex:

| Patrón | Handler | Notas |
|---|---|---|
| `listo` / `hecho` / `ya` / `terminé` / `done` | `_completar()` | Marca la tarea más urgente del sender como completada, avanza el round-robin |
| `mis tareas` / `qué me toca` / `pendientes` | `_listar()` | Lista tareas activas asignadas al sender |
| `nueva/editar/eliminar tarea` | delega a `parser.parse_config()` | Requiere `sender.is_admin` |
| cualquier otro texto | `_ayuda()` | Lista de comandos disponibles |

**Round-robin (`_next_assignee`):** ordena `Person` por `id` y avanza con
módulo. Con 2 personas fijas no se justifica un campo `rr_position`
dedicado (ver decisión #11 en `recommendations.md`).

---

### Parser — `bot/core/parser.py`

Solo se invoca para los comandos de configuración de tareas (`nueva`,
`editar`, `eliminar`), y solo si el sender es admin. Usa regex, sin
llamar a Claude API — el formato esperado es fijo:
`nueva tarea [nombre], cada [N] días`.

- `_crear()`: rechaza si ya existe una tarea activa con ese nombre.
- `_editar()`: busca por coincidencia parcial (`ilike`) y actualiza `frequency_days`.
- `_eliminar()`: soft delete (`is_active=False`), nunca borra la fila.

---

### Sender — `bot/whatsapp/sender.py`

Envío de mensajes salientes (usado por el scheduler para recordatorios).
Cliente Twilio singleton (`_get_client()`). **No agregar `sleep()` entre
envíos** — con 2 usuarios el rate limit del sandbox (~1 msg/seg) nunca se
alcanza; ver la advertencia en el docstring del archivo.

---

## Scheduler de recordatorios — `bot/core/scheduler.py`

`BackgroundScheduler` de APScheduler, timezone fija `America/Panama`.
En `setup()` (llamado desde el `lifespan` de `main.py`):

1. Lee `morning_reminder_time` y `night_reminder_time` de `settings`
   (fallback `07:30`/`21:00` si no existen).
2. Registra dos `CronTrigger`, uno por horario, con `id` fijo y
   `replace_existing=True` (evita duplicar jobs si se reinicia el proceso).
3. `_send_reminders()` filtra solo tareas **vencidas**
   (`next_due_at <= now`), las agrupa por `current_assignee_id` y envía un
   mensaje por persona con la lista de tareas pendientes.

**Reglas agregadas en v2:**
- **Ventana de sueño:** si la hora local (America/Panama) cae dentro de
  `sleep_start`/`sleep_end` de la persona, el recordatorio se omite. El
  rango puede cruzar medianoche (ej. 22:00 → 06:00).
- **Anti-duplicado:** cada envío marca `Task.last_reminder_sent_at`; si el
  último recordatorio fue hace menos de 4 horas no se reenvía (protege
  contra reinicios del contenedor cerca de la hora cron). La cadencia de
  reenvío de tareas vencidas la dan los dos crons diarios.
- **Fechas:** la DB guarda UTC naive; toda conversión a hora local vive en
  `bot/core/tiempo.py` (reemplaza al deprecado `datetime.utcnow()`).

**Migraciones — `bot/db/migrations.py`:** `create_all()` no altera tablas
existentes, así que los cambios de schema de v2 (columna
`last_reminder_sent_at`, índices, backfill de `next_due_at`) viven como
pasos idempotentes que corren en cada arranque desde el `lifespan`.

---

## Tests

`tests/` cubre `dispatcher` y `parser` — la lógica de negocio pura, sin
levantar el servidor HTTP ni mockear Twilio.

- **`tests/conftest.py`:** fixture `db_session` crea un engine SQLite
  **en memoria** propio (`sqlite:///:memory:`), independiente del engine
  persistente de `bot/db/database.py` (que siempre apunta a
  `data/hogar.db`). Fixtures `jean` y `anelys` insertan las dos personas
  base — el orden de creación importa porque el round-robin depende del
  `id` ascendente.
- **`tests/test_dispatcher.py`:** intents (`listo`, `mis tareas`,
  configuración), control de admin, alternancia del round-robin.
- **`tests/test_parser.py`:** crear/editar/eliminar tarea, duplicados,
  formato no reconocido.

**Ejecutar:**
```bash
make test   # docker compose run --rm bot pytest
```

---

## Convenciones

- snake_case para funciones y variables, PascalCase para clases
- Mensajes al usuario en español, tono casual
- Logs con loguru: INFO en prod, DEBUG en dev
- Tests con pytest, nombrados `test_{modulo}_{caso}`
- No commitear `data/hogar.db` (agregar a `.gitignore`)
