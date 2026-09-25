# Perdi e Achei: guia para agentes de IA

Sistema web de achados e perdidos do campus, desenvolvido como TP1 de Engenharia de Software (UFMG).
Objetivo, histórias de usuário e instruções de execução estão no [README](README.md).

## Stack e estrutura
- Python 3.12, Django 5.2 (LTS), SQLite, Pillow (upload de fotos)
- Frontend: templates do Django + Bootstrap 5.3 via CDN (sem build de JS)
- `config/`: settings e URLs do projeto
- `accounts/`: cadastro, login e logout (usa o `User` padrão do `django.contrib.auth`)
- `itens/`: itens, comentários e reivindicações
- `templates/base.html`: layout comum; toda página faz `{% extends 'base.html' %}` e preenche `{% block content %}`
- `static/css/style.css`: só ajustes pontuais sobre o Bootstrap

## Convenções de código
- Textos da interface em português do Brasil
- Nomes de models e campos do domínio em português (`Item`, `Comentario`, `Reivindicacao`)
- Preferir recursos prontos do Django (class-based views, `ModelForm`, `django.contrib.auth`, `messages`) a código próprio
- Views que exigem usuário logado usam `LoginRequiredMixin`/`@login_required`
- Testes automatizados estão fora do escopo do TP1: não criar

## Regras do trabalho (obrigatórias)
- **Um branch e um PR por issue.** Branch `tipo/N-descricao` (ex.: `feat/1-auth`) criado a partir da `main` atualizada
- **Conventional Commits** em inglês (`feat:`, `fix:`, `docs:`, `refactor:`, `style:`, `build:`, `chore:`), com `Refs #N` no corpo
- **Máximo de 100 linhas alteradas por commit.** Exceções (ex.: código gerado pelo Django) precisam de justificativa na mensagem do commit
- A descrição do PR tem `Closes #N`, um resumo do que foi feito e um roteiro de como testar
- Todo PR precisa de **Approve** de outro membro antes do merge. Nunca fazer merge sem aprovação
- Nunca fazer commit direto na `main`
- Todo código gerado precisa ser revisado e entendido por quem faz o commit, que vai explicá-lo na apresentação

## Fluxo de uma issue
1. Mover o cartão para *In progress* no quadro do GitHub Projects (usuário `mttcabral`, projeto "tp1-es")
2. `git checkout main && git pull`, depois criar o branch da issue
3. Planejar a partir dos critérios de aceitação e das tarefas técnicas da issue (e das dependências marcadas nela)
4. Implementar em commits pequenos e testar manualmente com `python manage.py runserver`
5. Rodar `python manage.py check` e, se houver models novos, `makemigrations`/`migrate` (as migrações também vão para o commit)
6. Abrir o PR, mover o cartão para *In review* e pedir revisão
