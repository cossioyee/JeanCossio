# hogar-bot — v2: Saneamiento + scheduler correcto (sin LLM)

Roadmap aprobado por Jean el 2026-07-03. Nota global: el LLM de v3/v5
será Gemini (Google, free tier), no Claude API.

## Alcance de v2

SÍ entra:
- [x] Scheduler: recordar solo tareas vencidas (`next_due_at <= now`)
- [x] Scheduler: respetar ventana de sueño `sleep_start`/`sleep_end` por persona
- [x] Scheduler: registrar `last_reminder_sent_at` y no reenviar si el último
      recordatorio fue hace menos de 4 horas (evita duplicados por reinicio)
- [x] Parser: `next_due_at` inicial al crear tarea (`ahora + frequency_days`)
- [x] Parser: desambiguación en editar/eliminar (match exacto primero; si hay
      varios parciales, listar opciones en vez de tocar la primera)
- [x] Router: `keep_blank_values=True` en `parse_qs` (fix 403 con params vacíos)
- [x] Timestamps: reemplazar `datetime.utcnow()` deprecado por helpers
      timezone-aware en `bot/core/tiempo.py`; mostrar fechas en hora local
- [x] Seed: no evaluar los números de teléfono en tiempo de import
- [x] DB: índices + migración idempotente (`bot/db/migrations.py`) con
      columna nueva, backfill de `next_due_at` y `CREATE INDEX IF NOT EXISTS`
- [x] Makefile: `db-reset` borra también los archivos WAL; `test` mide cobertura
- [x] Tests nuevos: scheduler, router, tiempo, migraciones, seed, sender, main
- [x] Commit único `feat(hogar-bot): v2 ...`

NO entra (queda para versiones siguientes):
- Gemini / cualquier LLM (v3)
- Rate limiting y audit log (v4)
- Aprendizaje de patrones y mensajes dinámicos (v5)
- Historial simulado, README, tag (v6)

## Revisión (2026-07-03)

- 54/54 tests pasan; cobertura 94.78% (piso de 80% activo en `make test`
  vía `--cov-fail-under=80`).
- Migración verificada contra la DB real `data/hogar.db`: columna
  `last_reminder_sent_at` agregada e índices `ix_*` creados; segunda
  corrida idempotente (la ejercitan los tests).
- Arranque real con `docker compose up`: limpio, `/health` 200.
- Cero warnings de `datetime.utcnow()` (antes 50).
- Ajuste a test existente: `test_listar_con_tareas` ahora usa mediodía UTC
  porque las fechas se muestran en hora de Panamá (comportamiento correcto
  nuevo; medianoche UTC del 01/08 es 31/07 local).
