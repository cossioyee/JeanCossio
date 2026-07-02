# hogar-bot — Guía rápida para Anelys

Así funciona el bot de tareas del hogar. Es un chat de WhatsApp, no una app —
todo se hace escribiéndole mensajes.

## Antes de empezar (una sola vez)

WhatsApp de Twilio (el servicio que usa el bot) requiere que actives el
chat manualmente:

1. Guarda el número **+1 415 523 8886** en tus contactos.
2. Envíale por WhatsApp el mensaje que te pase Jean, algo como:
   `join <una-palabra>`
3. Te va a responder confirmando que quedaste conectada.

**Importante:** si pasan 3 días sin que le escribas nada al bot, esa
conexión se desactiva sola y hay que repetir el paso 2. Si un día el bot
deja de responderte, prueba primero con esto antes de avisarle a Jean.

## Comandos que puedes usar

| Escribes | Qué pasa |
|---|---|
| `listo` (también sirve `hecho`, `ya`, `terminé`) | Marca tu tarea pendiente como completada y le pasa el turno a Jean |
| `mis tareas` (también `qué me toca` o `pendientes`) | Te muestra qué tareas tienes asignadas ahora mismo |
| cualquier otra cosa | El bot te muestra la lista de comandos disponibles |

No hace falta escribir con mayúsculas ni con acentos perfectos, el bot
entiende igual.

## Cómo funciona la asignación

Las tareas van rotando entre tú y Jean por turnos, uno a la vez —no hay
favoritismos ni criterio raro, es matemático. Cuando alguien escribe
`listo`, la tarea pasa automáticamente a la otra persona.

## Recordatorios

El bot te va a escribir solo, dos veces al día (mañana y noche), si
tienes alguna tarea pendiente. No necesitas pedirle nada para eso.

## Configurar o cambiar tareas

Eso solo lo puede hacer Jean por ahora (crear tareas nuevas, cambiar la
frecuencia, o eliminarlas). Si quieres que se agregue o cambie algo,
pídeselo directamente a él.

## Si algo no funciona

1. Revisa que no haya expirado la conexión (ver el aviso de los 3 días arriba).
2. Si sigue sin responder, avísale a Jean — puede ser algo del servidor.
