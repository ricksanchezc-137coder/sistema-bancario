# Sistema Bancário
Sistema bancário em Python com SQLite e POO


#Curriculo 11 (Git avancado): revisao aplicada ao sistema-bancario" \
 "Curriculo 11 (Git avancado, 15 modulos) concluido no repo git-avancado: internals, rebase interativo, cherry-pick, reflog, bisect, stash avancado, merge strategies e rerere, hooks, worktrees, submodules/subtrees, log/blame avancado, workflows (Gitflow/GitHub Flow), config avancado, colaboracao avancada (PRs/protected branches) e encerramento." \
 "Modulo 15 (encerramento) aplicado direto neste projeto: git log --graph + shortlog confirmaram historico linear (9 commits, sem merges); achado que o fechamento do Curriculo 10 (TDD) teve 3 commits, nao 1 (dois refactors de extracao - tentar_login e submenu_extratos, motivados pela complexidade medida pelo radon - antes do commit final)." \
 "git log -L :funcname:file mostrou que essa forma de -L nao detecta move, so rastreia a partir da criacao da funcao. git blame -C -C -C10 mostrou que a extracao teve mudanca de comportamento junto (break virou return, novo except Exception), entao a maioria das linhas ficou atribuida ao proprio commit de extracao - so as linhas que permaneceram identicas foram rastreadas corretamente ate o commit original." \
 "Nenhuma mudanca de codigo - so revisao e analise."

#05/08/2026

#_________



#17/08/2026
"Currículo 12 (Ambiente Python) concluído: 16 módulos - venv, pip, requirements.txt, pip avançado, índices/PyPI, pyproject.toml (PEP 518/517/621), build backends, ferramentas modernas (Poetry/PDM/Hatch/uv), lockfiles, entry points, pipx/.env, empacotamento/distribuição (build/twine/TestPyPI), uv na prática (via Ubuntu proot-distro) e encerramento."
"Módulo 16 (encerramento) aplicado direto neste projeto: diagnóstico revelou zero isolamento (dependências soltas no Python global do Termux, que inclusive sumiram parcialmente após o upgrade 3.13→3.14 do módulo anterior); criado .venv dedicado, pyproject.toml (com py-modules explícito, já que o projeto é módulos soltos, não pasta-pacote) e requirements.txt/requirements-dev.txt separando produção de dev; suíte reinstalada do zero via pip install -e \".[dev]\" e revalidada (171 passed, mesmo estado conhecido do XPASS strict do Currículo 9)."

#30/08/2026
## Manutenção

O script `manutencao.sh` automatiza três tarefas de rotina do projeto:

- **Backup**: gera um `.tar.gz` com data/hora em `~/backup/`, excluindo `.venv`, `__pycache__`, `.pytest_cache`, `htmlcov` e `.git`
- **Limpeza de cache**: remove pastas `__pycache__` do projeto (fora do `.venv`)
- **Testes**: ativa o venv, roda a suíte via `pytest` e grava um resumo em `manutencao.log`

### Uso

\`\`\`bash
cd sistema-bancario
./manutencao.sh
\`\`\`

O log completo de cada execução fica em `manutencao.log` (fora do controle de versão).

### Agendamento (opcional)

Pra rodar automaticamente, adicione ao crontab:

\`\`\`
0 3 * * 0 cd ~/sistema-bancario && ./manutencao.sh
\`\`\`

Se o backup demorar, é recomendável rodar dentro de uma sessão `tmux` pra não depender do terminal ficar aberto.

