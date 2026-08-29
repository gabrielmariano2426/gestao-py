# Notas de schema — mapeamento legado → reescrita

O sistema legado usa um schema Postgres chamado `gestao` no Supabase, com
**63 tabelas/views**, todas com nomes curtos prefixados (`c02usuario`,
`c88seguro`...). Não existe nenhum arquivo `.sql` no repositório original —
esse inventário foi reconstruído lendo as chamadas `.from('...')` em todo o
código JS (`index.html`, `js/*.js`, `checkout/`, `financeiro/`, `assinar.html`).

**Antes de ligar esta aplicação a dados reais**, rode `pg_dump --schema=gestao`
(ou `supabase db dump`) contra o projeto Supabase ao vivo e confira os tipos
de coluna reais — os nomes aqui vieram do código JS, não de um DDL autoritativo.

## Convenção de nomes nesta reescrita

Tabelas e colunas novas usam nomes descritivos em português
(`usuarios.nivel_acesso`) em vez dos códigos crípticos do legado
(`c02usuario.n02nivel_acesso`). Isso é intencional — é uma reescrita, não
uma cópia 1:1 — mas significa que qualquer script de migração de dados
precisa mapear coluna a coluna usando esta tabela como referência.

## Modeladas na Fase 1 (`gestao_py/models/`)

| Tabela nova | Tabela legada | Arquivo |
|---|---|---|
| `usuarios` | `c02usuario` | `models/usuario.py` |
| `usuario_sessoes` | `c91usuario_sessoes` | `models/usuario.py` |
| `audit_log` | `c92audit_log` | `models/usuario.py` |
| `segurados` | `segurado` | `models/segurado.py` |
| `segurado_documentos` | `segurado_docs` | `models/segurado.py` |
| `seguros` | `seguro` | `models/seguro.py` |
| `seguro_documentos` | `seguro_docs` | `models/seguro.py` |
| `condutores` | `c51condutores` | `models/seguro.py` |
| `parcelas` | `c38parcela` | `models/seguro.py` |
| `sequencias_seguro` | *(não existia — novo)* | `models/seguro.py` |
| `seguradoras` | `seguradora` | `models/seguradora.py` |
| `empresas` | `c01empresa` | `models/lookups.py` |
| `estados_civis` | `c83estadocivil` | `models/lookups.py` |
| `formas_pagamento` | `c84formapagamento` | `models/lookups.py` |
| `ramos` | `c89ramo` | `models/lookups.py` |
| `status_seguro` | `c80status` | `models/lookups.py` |
| `tipos_documento` | `c86documento` | `models/lookups.py` |

## Não modeladas ainda (referência para as fases 2+ do ROADMAP.md)

### Assinatura eletrônica (Fase 3)
`c40assinatura_documento` (titulo, status, cabecalho_posicao, arquivo_signatario_url,
cancelamento_motivo), `c41assinatura_signatario` (nome, cpf_cnpj, papel,
status, ordem, codigo_segurado, codigo_corretor), `c42assinatura` (imagem +
hash), `c43assinatura_auditoria` (tipo_evento, detalhe JSON, ocorrido_em,
usuario), `c44assinatura_campo` (posição do campo no PDF).

### Automações (Fase 2)
`c30automacao` (chave, ativo, horario, dias_antecedencia), `c31automacao_logs`,
`c39emails_enviados`.

### Trello/Kanban interno (Fase 4)
`c19trello_lembretes`, `c20trello` (colunas), `c21trello_anexos`,
`c22trello_cards` (coluna_id, posicao, observacao, cor, codigo_seguro),
`c23trello_comentarios`, `c25trello_notificacoes`, `c26comentarios`
(comentário genérico, também usado por `seguro`/`segurado` no legado —
candidato a virar uma tabela polimórfica única na reescrita).

### Financeiro (Fase 6 — `financeiro/`)
`c94contabanco`, `c95banco_importacao`, `c96banco_lancamento`, `c97categoria`,
`c98banco_regras`, `c11extrato`, `c12extrato_seguros`.

### Checkout público (Fase 6 — `checkout/`)
`c93checkout` (token, ativo, tentativas_falhas, status, contador_acessos,
ip_acesso, email_operacional). Lembrete importante do legado a preservar:
**dado de cartão nunca é persistido no banco**, só passa por e-mail.

### Cartão 24h (Fase 7)
`c13cartao24h` (lote, id_seguro, codigo_usr), `c15telefones_uteis`,
`c16logotipos`.

### Outras tabelas vistas no legado, ainda sem fase definida
`anexos`, `atendimento`, `atendimento_docs`, `c03usuario_empresa`,
`c06aliquota`, `c14oficina`, `c32comunicacaoemail`, `c33comunicacaoenvio`,
`c60ia_pergunta`, `c71seguradora_docs` (monitor de condições gerais),
`c82profissao`, `c85banco`, `c87ocorrencia`, `c90backup_log`, `cotacoes`,
`documentos`, `processos`, `sinistro_docs`, `sinistros`, `whatsapp_envios`,
`vw34cotacoes` (view), `vw_kpi_segurados_ult10anos` (view — SQL não está
disponível no repo, precisa ser extraída do Supabase ao vivo).
