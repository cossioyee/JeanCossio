# hogar-bot — CLAUDE.md

## Propósito
Bot de WhatsApp para distribución equitativa de tareas del hogar entre
Jean y Ana. Asignación por round-robin simple. Configuración de tareas
por WhatsApp. El aprendizaje de patrones de horario queda para v2.

## Stack
- Python 3.12 / FastAPI / SQLAlchemy / SQLite
- Twilio WhatsApp Sandbox (dev) / Meta Cloud API (prod, futuro)
- APScheduler para recordatorios a hora fija
- Docker Compose (servicios: bot, ngrok, adminer)
- Claude API solo para parsear texto libre (configurar tareas, detectar "listo")

## Alcance del MVP v1
SÍ incluye:
- Configurar/editar/eliminar tareas por WhatsApp
- Asignación round-robin estricta (alternancia matemática, sin IA)
- Recordatorios a hora fija (mañana y noche)
- Marcar tarea completada respondiendo "listo"
- Historial guardado en DB (para alimentar aprendizaje en v2)

NO incluye (diferido a v2):
- Aprendizaje de patrones de horario por persona
- Reenvío de recordatorios si la tarea queda vencida
- Mensajes generados dinámicamente con contexto histórico
- Dashboard web

## Convenciones
- snake_case para funciones y variables, PascalCase para clases
- Todos los mensajes al usuario en español, tono casual
- Logs con loguru: INFO en prod, DEBUG en dev
- Tests con pytest, nombrados test_{modulo}_{caso}

## Comandos clave
make dev        # docker-compose up con hot-reload
make test       # pytest
make shell      # shell dentro del contenedor bot
make db-reset   # limpia y recrea la DB (solo dev)

## Qué NO tocar sin revisión
- db/models.py: cambios de schema requieren migración manual
- whatsapp/sender.py: tiene rate limiting, no agregar sleeps arbitrarios
- task_completions es append-only, nunca se borra

## Personas (reemplazar con números reales)
- Jean: admin, puede configurar tareas
- Anelys: usuario estándar

## Decisiones de diseño tomadas
- SQLite, no Postgres: solo 2 usuarios, sin necesidad de concurrencia
- Sin login/auth: el número de WhatsApp es la identidad
- Round-robin matemático en v1, sin LLM en la decisión de "a quién le toca"
- Claude API se usa solo para parsear texto libre, no para decidir asignaciones