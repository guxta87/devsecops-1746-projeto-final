# Relatório de Evidências Técnicas — Clube Aurora (Trilha 3 — Técnica)

**Nome do Aluno:** Gustavo Duarte Lepesteur da Costa

**Turma:** DevSecOps 1746

**Link do Repositório / Fork no GitHub:** <https://github.com/guxta87/devsecops-1746-projeto-final>

**Link do Pull Request Principal:** a preencher após a abertura do PR

---

## 1. Evidência do Pipeline Inicial (Antes das Correções)

**Execução inicial:** <https://github.com/guxta87/devsecops-1746-projeto-final/actions/runs/40803047106>

![Pipeline inicial com os Quality Gates reprovados](evidencias/pipeline-inicial-falha.png)

O pipeline inicial terminou com os dois jobs reprovados:

- **Quality Gate Estático:** falhas no Hadolint, Gitleaks, Trivy Filesystem, Semgrep SAST e análise de IaC do Docker Compose.
- **Quality Gate Dinâmico:** falhas no Trivy Image e OWASP ZAP Baseline.

## 2. Resumo das Correções Implementadas

| Achado | Arquivo modificado | Resumo da alteração realizada |
|---|---|---|
| **F1: Segredos** | `.gitignore`, `.env`, `.env.example` | A preencher |
| **F2: SCA** | `requirements.txt` | A preencher |
| **F3: SAST** | `app/db.py` | A preencher |
| **F4: Hardening** | `Dockerfile` | A preencher |
| **F5: DAST** | `app/main.py` ou `app/__init__.py` | A preencher |
| **F6: Menor Privilégio** | `app/db.py`, `app/main.py` | A preencher |
| **F7: IaC** | `docker-compose.yml` | A preencher |

## 3. Evidência do Pipeline Final (Após as Correções)

A preencher após a aprovação de todos os Quality Gates.

## 4. Aceitação de Risco

Não prevista. Qualquer exceção necessária será documentada com o respectivo identificador, justificativa e prazo de correção.
