# hogar-bot — Lecciones aprendidas

## 2026-07-03 — El LLM del proyecto es Gemini, no Claude API
**Corrección de Jean:** al aprobar el roadmap v2→v6 aclaró que la decisión
previa fue usar Gemini (Google, free tier) para todo lo de lenguaje natural,
no Claude API, por costo.
**Regla:** antes de proponer integraciones de LLM en este proyecto, asumir
Gemini (`google-genai`). Los docs viejos (CLAUDE.md, architecture.md,
recommendations.md) todavía dicen "Claude API" — corregirlos cuando se
implemente v3, no confiar en ellos para esta decisión.

## 2026-07-03 — Los docs pueden estar por delante del código
**Detección en Fase 0:** `architecture.md` afirmaba que el scheduler filtra
`next_due_at <= now()` y que `next_due_at` se inicializa al crear la tarea;
ninguna de las dos cosas estaba en el código.
**Regla:** al leer la documentación de este proyecto, verificar contra el
código antes de asumir que un comportamiento descrito existe.
