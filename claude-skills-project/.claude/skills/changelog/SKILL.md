---
name: Changelog Generator
description: This skill should be used when the user asks to generate a changelog, review commit history, or summarize what has changed in the project.
allowed-tools: Read, Write, Bash
---

# Generador de Changelog

## Propósito
Generar un CHANGELOG.md a partir del historial de commits git del proyecto.

## Entradas
- El directorio de trabajo actual (debe ser un repositorio git)

## Salidas
- Un archivo `CHANGELOG.md` escrito en la raíz del proyecto

## Pasos
1. Ejecutar `git log --pretty=format:"%h %s (%cr)" --reverse` para obtener el historial completo de commits.
2. Ejecutar `git status --short` para verificar cambios sin commitear.
3. Leer el listado del directorio raíz del proyecto para identificar archivos clave.
4. Escribir un `CHANGELOG.md` en la raíz del proyecto con estas secciones: nombre del proyecto (desde el nombre de la carpeta), historial de commits (formateado como lista legible), estado actual del árbol de trabajo, y una lista de archivos rastreados con descripciones de una línea.
5. Imprimir la ruta del archivo generado para confirmar que fue escrito exitosamente.
