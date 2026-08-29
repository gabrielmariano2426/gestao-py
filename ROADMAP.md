# Roteiro — fases seguintes da reescrita

Fase 1 (concluída nesta etapa) entregou: fundação (config, banco, auth real,
RBAC server-side, auditoria), e os módulos Segurados, Seguros e Dashboard.
Este documento detalha o que falta, na ordem recomendada, com a decisão
arquitetural que corrige o problema equivalente encontrado no sistema legado
(ver CODE_REVIEW_2026-08-29.md e as explorações que geraram SCHEMA_NOTES.md).

## Fase 2 — Automações

**Legado:** `js/gestao-automacoes.js` só configura/testa; o disparo real
roda em outro deploy (`cotacaoauto.masterparceria.com.br`), fora deste repo.
Já o motor de renovação/lembretes do "Trello" (ver Fase 4) roda **dentro do
navegador**, via `setInterval`, com um lock otimista para não duplicar entre
abas — "a última aba aberta vence".

**O que fazer:** mover todo disparo agendado para um job de servidor real
(APScheduler ou Celery beat), com lock atômico no banco
(`SELECT ... FOR UPDATE SKIP LOCKED` ou um advisory lock do Postgres) em vez
do padrão "última aba vence". Tabelas: `c30automacao`, `c31automacao_logs`,
`c39emails_enviados`, `c19trello_lembretes`.

## Fase 3 — Assinatura eletrônica

**Legado:** `js/gestao-assinaturas.js` (canvas de assinatura manuscrita,
assinatura digitada com fontes cursivas, editor visual de posicionamento de
campo sobre o PDF via `PDFLib`, fila de envio sequencial por signatário).

**O que fazer:**
- Canvas de assinatura e editor de campo → componente Reflex customizado
  (wrapper de um componente React/JS, Reflex suporta isso nativamente).
- Manipulação de PDF (overlay de assinatura/QR/lacre) → sai de `PDFLib`
  (client-side) para `pypdf`/`reportlab` no servidor.
- Fila de envio sequencial (`_dispararProximoDaFila`) → função de serviço
  que dispara o próximo convite só depois que o anterior é confirmado.
- Preservar o esquema de hash de verificação (`sha256(...)` truncado) para
  não quebrar links de documento antigos, se a migração for incremental.
- Tabelas: `c40assinatura_documento`, `c41assinatura_signatario`,
  `c42assinatura`, `c43assinatura_auditoria`, `c44assinatura_campo`.
- Página pública `/assinar/<token>` sem login, com validade jurídica
  (Lei 14.063/2020) — igual ao `assinar.html` legado.

## Fase 4 — Trello/Kanban interno

**Legado:** não é a API do Trello — é um Kanban próprio (`js/gestao-trello.js`),
com drag-and-drop de cards entre colunas de pipeline (novo negócio,
renovação 30/15/10/5 dias, emissão), comentários, anexos, notificações e o
motor de automação client-side citado na Fase 2.

**O que fazer:** drag-and-drop via componente Reflex customizado; um único
endpoint de reordenação (o legado faz N updates individuais por drag);
extrair a máquina de estados de renovação (limiares 30/15/10/5 dias,
sucessão por `numero_seguro_anterior`) em funções puras testáveis, como foi
feito aqui com `services/dashboard_dates.py`. Tabelas: `c19` a `c26`
prefixadas com `trello`/`comentarios` (ver SCHEMA_NOTES.md).

## Fase 5 — Relatórios

**Legado:** três estilos de geração de PDF coexistem em
`js/gestao-relatorios.js` — desenho manual com `jsPDF`, overlay com
`PDFLib`, e HTML+`window.print()`. Bastante lógica de negócio (formatação
de bônus, código de forma de pagamento) embutida na camada de apresentação.

**O que fazer:** consolidar num único pipeline server-side (ReportLab ou
WeasyPrint), extraindo a lógica de formatação para funções de serviço
independentes de layout, testáveis sem gerar PDF.

## Fase 6 — Financeiro e Checkout público

**Legado:** `financeiro/index.html` (importação de OFX, conciliação,
categorização automática por regras) roda embutido em `<iframe>` sem
autenticação própria — confia que só o app pai (já logado) o abre.
`checkout/index.html` é uma página pública por token para captura de
cartão, que **nunca persiste dado de cartão no banco** — só envia por
e-mail (padrão a preservar).

**O que fazer:** página `/financeiro` dentro do app autenticado (não mais
iframe sem checagem própria); página pública `/checkout/<token>` mantendo a
regra de nunca gravar dado de cartão. Tabelas: `c94` a `c98`, `c93checkout`.

## Fase 7 — Cartão 24h e Auditoria (UI completa)

Cartão 24h: geração de layout A4 (3 modos de impressão) — hoje é
client-side com `html2canvas`+`jsPDF`; avaliar manter renderização no
cliente ou mover para ReportLab no servidor. Auditoria: a Fase 1 já grava
em `audit_log` (ver `services/audit.py`); falta a tela de consulta/filtro
(o legado só tinha isso, sem a escrita correta por trás).

## Integrações externas a mover para trás do backend (todas as fases)

No legado, todas essas eram chamadas direto do navegador com a anon key do
Supabase exposta:

- **Resend** (e-mail) — `RESEND_API_KEY` em `config.py`, nunca no cliente.
- **WhatsApp** (`wa.me/...`) — link simples, sem chave, pode continuar
  gerado no frontend.
- **api.ipify.org** (captura de IP para auditoria de assinatura) — mover
  para o backend (o IP da requisição já está disponível no handler).
- **Hub de consulta CPF** (proprietário, citado mas não implementado nesta
  fase) — precisa da URL/chave real do provedor antes de portar.
- **API Anthropic** (leitura de proposta via IA, `api/ler-proposta.js`) —
  `ANTHROPIC_API_KEY` já reservada em `config.py`; endpoint ainda não
  portado.
- **api.cpfcnpj.com.br** (`api/consulta.js`) — `CPFCNPJ_TOKEN` já reservada
  em `config.py`; endpoint ainda não portado.
