# ATLAS ONU — Claude Code

Las reglas del repositorio, para cualquier agente, están en `AGENTS.md` (estándar https://agents.md). Claude Code las
carga desde aquí:

@AGENTS.md

## Solo para Claude Code
- Las skills (`.claude/skills/`) se invocan con `/trabajar-cola`, `/cerrar-tarea` y `/revisar-ux`, o solas cuando la
  tarea encaja con su descripción.
- `.claude/settings.json` bloquea los `git push --force` y apaga la atribución de Claude en commits y PR
  (`attribution` vacío, `includeCoAuthoredBy: false`): no la vuelvas a encender.
