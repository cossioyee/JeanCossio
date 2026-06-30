# hogar-bot — Documentación de Arquitectura

## Índice
- [Stack y decisiones de diseño](#stack-y-decisiones-de-diseño)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Capa de base de datos](#capa-de-base-de-datos)
  - [Modelos](#modelos)
  - [Relaciones](#relaciones)
  - [Engine y sesión](#engine-y-sesión)
  - [Seed inicial](#seed-inicial)
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
│   ├── core/          # Lógica de negocio (round-robin, scheduler, parser)
│   ├── db/
│   │   ├── models.py  # Modelos SQLAlchemy
│   │   └── database.py# Engine, sesión, dependencia FastAPI
│   ├── whatsapp/      # Integración Twilio / sender
│   └── tests/
├── data/
│   └── hogar.db       # SQLite (generado en runtime, no commitear)
└── docs/
    └── architecture.md# Este archivo
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
registro ya existe lo omite sin error.

**Ejecutar:**
```bash
python -m bot.db.seed
```

**Datos que inserta:**

| Tabla | Registro | Notas |
|---|---|---|
| `persons` | Jean | `is_admin=True`; número en placeholder |
| `persons` | Anelys | `is_admin=False`; número en placeholder |
| `settings` | `morning_reminder_time` | `07:30` por defecto |
| `settings` | `night_reminder_time` | `21:00` por defecto |

**Antes de correr en producción:** reemplazar los `phone_number` en
`PERSONS` con los números reales en formato `whatsapp:+521XXXXXXXXXX`.

---

## Convenciones

- snake_case para funciones y variables, PascalCase para clases
- Mensajes al usuario en español, tono casual
- Logs con loguru: INFO en prod, DEBUG en dev
- Tests con pytest, nombrados `test_{modulo}_{caso}`
- No commitear `data/hogar.db` (agregar a `.gitignore`)
