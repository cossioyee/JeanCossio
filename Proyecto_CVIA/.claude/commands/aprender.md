Analiza el error o corrección actual en la conversación y actualiza CLAUDE.md con una lección concreta que prevenga que se repita.

Si se pasaron argumentos (`$ARGUMENTS`), úsalos como descripción del error. Si no, dedúcelo del contexto de la conversación.

## Proceso

1. **Identificar el error**: ¿Qué fue lo que salió mal o fue corregido? Sé específico — no generalices.

2. **Filtrar**: Solo continuar si la lección cumple los tres criterios:
   - Es específica a este proyecto o stack (no buenas prácticas genéricas)
   - Es accionable: se puede expresar como una regla imperativa clara
   - No está ya cubierta en CLAUDE.md (lee el archivo antes de escribir)

3. **Leer CLAUDE.md**: Usa Read en `CLAUDE.md` para revisar lecciones existentes y evitar duplicados.

4. **Redactar la lección** con este formato:
   ```
   - **[Categoría]**: [Regla en imperativo]. *Por qué: [razón en ≤ 10 palabras].*
   ```
   Ejemplo:
   ```
   - **Terraform/OCI**: Nunca hardcodear el compartment_id; siempre usar variable. *Por qué: rompe portabilidad entre tenancies.*
   ```

5. **Editar CLAUDE.md**: Agregar la lección bajo la sección `## Lecciones Aprendidas`. Si esa sección no existe, crearla al final del archivo antes de escribir.

6. **Confirmar** en una sola línea qué lección se añadió.
