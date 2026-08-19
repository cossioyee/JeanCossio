---
name: Smart Commit
description: This skill should be used when the user wants to commit their current changes with a well-formatted conventional commit message.
allowed-tools: Read, Write, Bash
---

# Smart Commit

## Propósito
Stagear todos los cambios actuales y crear un commit git con un mensaje de commit convencional.

## Entradas
- El directorio de trabajo actual (debe ser un repositorio git)
- Una descripción opcional del usuario sobre lo que cambió

## Salidas
- Un nuevo commit git con un mensaje de commit convencional

## Pasos
1. Ejecutar `git status --short` para ver qué archivos cambiaron.
2. Ejecutar `git diff` y `git diff --cached` para entender los cambios.
3. Stagear todos los cambios con `git add -A`.
4. Analizar los cambios y generar un mensaje de commit convencional:
   - Formato: `type(scope): description`
   - Tipos: feat, fix, docs, style, refactor, test, chore
   - Mantener la primera línea en menos de 72 caracteres
5. Crear el commit con `git commit -m "<generated message>"`.
6. Imprimir el hash y mensaje del commit para confirmar el éxito.
