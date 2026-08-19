---
name: Dev Pipeline
description: This skill should be used when the user wants to commit their changes and update the project changelog in one step.
allowed-tools: Read, Write, Bash
---

# Dev Pipeline

## Propósito
Commitear los cambios actuales con un mensaje bien formateado y luego regenerar el changelog del proyecto.

## Pasos
1. Ejecutar el skill `/smart-commit` para stagear y commitear todos los cambios actuales.
2. Ejecutar el skill `/changelog` para regenerar el CHANGELOG.md con el historial de commits actualizado.
3. Imprimir un resumen mostrando el nuevo commit y la ruta al changelog actualizado.
