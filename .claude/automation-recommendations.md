# Claude Code Automation Recommendations

_Generado: 2026-05-25_

## Perfil del repositorio
- **Proyectos**: Python (FinanzasPersonales, scripts), Terraform (OCI, AWS), CloudFormation, Docker, Ollama/AI
- **Stack principal**: Python + SQLite + Docker + IaC (Terraform/CF)

---

## 🔌 MCP Servers

### 1. Docker MCP
**Por qué**: Tienes múltiples proyectos con Docker y docker-compose. Permite inspeccionar contenedores, ver logs y ejecutar comandos sin salir de Claude Code.
**Instalar**: `claude mcp add docker`

### 2. context7
**Por qué**: Usas librerías como SQLAlchemy, Plotly, Pandas y providers de Terraform — context7 trae la documentación actualizada directo al contexto sin que tengas que buscarla.
**Instalar**: `claude mcp add context7`

---

## ⚡ Hooks

### Auto-format Python al editar
**Por qué**: Varios scripts Python sin formateo automático (`finanzas.py`, `analisis.py`, etc.).
**Qué hace**: Corre `black` sobre el archivo cada vez que Claude lo edita.

```json
"PostToolUse": [{
  "matcher": "Edit|Write",
  "command": "black \"$CLAUDE_TOOL_INPUT_FILE_PATH\" 2>/dev/null || true"
}]
```

### Bloquear edición de terraform.tfvars
**Por qué**: El archivo contiene credenciales OCI y ya se coló en un commit accidentalmente.
**Qué hace**: Impide que Claude edite ese archivo.

```json
"PreToolUse": [{
  "matcher": "Edit|Write",
  "command": "if echo \"$CLAUDE_TOOL_INPUT_FILE_PATH\" | grep -q 'terraform.tfvars$'; then echo 'Bloqueado: archivo de credenciales' && exit 2; fi"
}]
```

---

## 🎯 Skills

### `tf-workflow`
**Por qué**: El flujo `init → plan → apply → output` se repite en cada proyecto de Terraform, con debugging incluido.
**Qué hace**: Empaqueta el workflow completo con manejo de errores.
**Invocación**: `/tf-workflow`

### `retry-capacity`
**Por qué**: El error `Out of host capacity` de OCI free tier se repite cada vez que creas infra ARM.
**Qué hace**: Documenta el patrón e invoca `retry-apply.sh` directamente.
**Invocación**: `/retry-capacity`

---

## 🤖 Subagentes

### `security-reviewer`
**Por qué**: Manejas credenciales OCI, tfvars y archivos de estado — ya ocurrió un commit con datos sensibles.
**Qué hace**: Revisa PRs y detecta credenciales expuestas o permisos inseguros en archivos `.tf` antes de hacer push.
**Dónde crear**: `.claude/agents/security-reviewer.md`

---

## Implementación

Para implementar cualquiera de estas, pídele a Claude:
- _"configura el hook de bloqueo de terraform.tfvars"_
- _"instala el MCP de Docker"_
- _"crea el skill tf-workflow"_
- _"crea el subagente security-reviewer"_
