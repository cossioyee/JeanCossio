# hogar-bot — Roadmap v2

Pendientes ya identificados desde v1 (ver `CLAUDE.md` y las decisiones de
diseño en `recommendations.md`). El schema ya tiene los campos necesarios
para casi todo esto sin migraciones — fue una decisión explícita en v1
dejarlos listos.

## 1. No enviar recordatorios en horario de sueño
**Qué:** el scheduler debe saltarse a una persona si el envío cae dentro
de su `sleep_start`/`sleep_end`.
**Ya existe:** los campos `sleep_start`/`sleep_end` en `Person` (nullable,
agregados en v1 sin usarse — ver decisión #2 en `recommendations.md`).
**Falta:** lógica en `bot/core/scheduler.py::_send_reminders()` que
compare la hora actual contra el rango de cada persona antes de enviar.
**Por qué primero:** es el cambio más chico y de menor riesgo — no toca
schema, no depende de los otros puntos.

## 2. Horario óptimo de recordatorio por persona (aprendizaje de patrones)
**Qué:** en vez de horarios fijos globales (`morning_reminder_time` /
`night_reminder_time` en `settings`), calcular el horario en que cada
persona suele responder `listo`, usando el historial de `task_completions`.
**Ya existe:** `task_completions` es append-only desde v1 específicamente
para esto (decisión #4 en `recommendations.md`).
**Falta:** definir el criterio de "horario óptimo" (¿promedio de
`completed_at`? ¿moda por franja horaria?) y dónde vive ese cálculo —
probablemente un job periódico que actualiza un valor por persona, no un
cálculo en cada request.
**Depende de:** tener suficiente historial acumulado en `task_completions`
para que el cálculo tenga sentido — no vale la pena antes de unas semanas
de uso real en v1.

## 3. Reenvío de recordatorio si la tarea queda vencida
**Qué:** si nadie responde `listo` después del recordatorio, reenviar
(por ejemplo, unas horas después o al día siguiente).
**Falta en schema:** un campo `due_date` en `task_completions` (o
reutilizar `Task.next_due_at`) para que el scheduler pueda distinguir
"tarea vencida sin respuesta" de "tarea recién asignada". Revisar si
conviene un campo `last_reminder_sent_at` en `Task` para no reenviar en
cada corrida del scheduler.
**Depende de:** el punto 1 (no tiene sentido reenviar en horario de
sueño) y de definir la política de reintentos (¿cuántas veces? ¿escala a
la otra persona si no responde nadie?).

## 4. Mensajes dinámicos con contexto histórico vía Claude API
**Qué:** en vez de las plantillas fijas actuales
(`f"Recordatorio: te toca {names}..."`), generar el texto del recordatorio
con Claude API usando contexto del historial (ej. "van 3 días que te toca
esto, ¿todo bien?").
**Ya existe:** Claude API ya está en el proyecto para parsear comandos de
configuración (`bot/core/parser.py` usa regex hoy, pero la decisión de
diseño reservó Claude API para texto libre — ver decisión #10).
**Falta:** decidir el alcance (¿solo el tono del mensaje, o también
decide *cuándo* recordar?) — cuidado con no reintroducir IA en la
decisión de asignación, eso quedó fuera de scope explícitamente
(decisión #11: round-robin matemático, sin IA).
**Depende de:** puntos 2 y 3 — sin datos históricos ni política de
reenvío, no hay mucho contexto que darle a Claude todavía.

## Fuera de este roadmap (no está en el scope de v2 según CLAUDE.md)
- Dashboard web — quedó explícitamente diferido, sin fecha.
- Agregar más personas al round-robin — hoy asume 2 fijos; si se agrega
  una tercera persona, revisar decisión #11 (orden por `id` vs.
  `rr_position` dedicado).

## Sugerencia de orden de implementación
1 → 3 (con recordatorio simple, sin Claude) → 2 → 4

La razón de este orden: 1 y 3 son mejoras de comportamiento del scheduler
que no requieren datos históricos ni LLM, dan valor inmediato y son fáciles
de verificar. 2 necesita semanas de uso real acumulando `task_completions`
antes de que el cálculo tenga sentido. 4 depende de tener ya la lógica de
"cuándo" recordar (puntos 1-3) para que el mensaje generado por Claude
tenga contexto real que resumir.
