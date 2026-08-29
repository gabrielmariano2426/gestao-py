"""Página Seguros (apólices) — lista, busca e formulário de criação/edição."""
from __future__ import annotations

import reflex as rx

from gestao_py.components.layout import app_shell
from gestao_py.state.seguro_state import SeguroState


def _campo_texto(label: str, name: str, **kwargs) -> rx.Component:
    return rx.vstack(
        rx.text(label, size="1", color="gray"),
        rx.input(
            name=name,
            default_value=SeguroState.form_valores.get(name, ""),
            **kwargs,
        ),
        spacing="1",
        width="100%",
    )


def _campo_select(label: str, name: str, opcoes: rx.Var) -> rx.Component:
    return rx.vstack(
        rx.text(label, size="1", color="gray"),
        rx.select.root(
            rx.select.trigger(placeholder="Selecione..."),
            rx.select.content(
                rx.foreach(
                    opcoes,
                    lambda op: rx.select.item(op["label"], value=op["id"]),
                )
            ),
            name=name,
            default_value=SeguroState.form_valores.get(name, ""),
        ),
        spacing="1",
        width="100%",
    )


def _dialog_form() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(
                rx.cond(SeguroState.editando_id, "Editar apólice", "Nova apólice")
            ),
            rx.cond(
                SeguroState.financeiro_travado_atual,
                rx.callout(
                    "Apólice com financeiro travado — edição de campos financeiros exige nível 5+.",
                    color_scheme="amber",
                    size="1",
                ),
            ),
            rx.form(
                rx.vstack(
                    rx.cond(
                        SeguroState.mensagem_erro != "",
                        rx.callout(SeguroState.mensagem_erro, color_scheme="red", size="1"),
                    ),
                    rx.hstack(
                        _campo_select("Segurado", "segurado_id", SeguroState.opcoes_segurados),
                        _campo_select("Seguradora", "seguradora_id", SeguroState.opcoes_seguradoras),
                        width="100%",
                        spacing="3",
                    ),
                    rx.hstack(
                        _campo_select("Ramo", "ramo_id", SeguroState.opcoes_ramos),
                        _campo_select("Forma de pagamento", "forma_pagamento_id", SeguroState.opcoes_formas_pagamento),
                        _campo_select("Status", "status_id", SeguroState.opcoes_status),
                        width="100%",
                        spacing="3",
                    ),
                    rx.hstack(
                        _campo_texto("Tipo de operação", "tipo_operacao", placeholder="NOVO / RENOVAÇÃO / ENDOSSO"),
                        _campo_texto("Nº proposta", "numero_proposta"),
                        _campo_texto("Nº apólice (seguradora)", "numero_apolice"),
                        width="100%",
                        spacing="3",
                    ),
                    rx.hstack(
                        _campo_texto("Prêmio líquido", "premio_liquido"),
                        _campo_texto("Prêmio total", "premio_total"),
                        _campo_texto("IOF", "iof"),
                        width="100%",
                        spacing="3",
                    ),
                    rx.hstack(
                        _campo_texto("Qtd. parcelas", "qtd_parcelas"),
                        _campo_texto("Valor parcela", "valor_parcela"),
                        width="100%",
                        spacing="3",
                    ),
                    rx.hstack(
                        _campo_texto("Vigência início", "vigencia_inicio", type="date"),
                        _campo_texto("Vigência fim", "vigencia_fim", type="date"),
                        width="100%",
                        spacing="3",
                    ),
                    rx.hstack(
                        rx.dialog.close(rx.button("Cancelar", variant="soft", type="button")),
                        rx.button("Salvar", type="submit"),
                        spacing="3",
                        justify="end",
                        width="100%",
                    ),
                    spacing="3",
                    width="100%",
                ),
                on_submit=SeguroState.salvar,
                reset_on_submit=False,
            ),
            max_width="720px",
        ),
        open=SeguroState.modal_aberto,
        on_open_change=SeguroState.definir_modal_aberto,
    )


def _tabela() -> rx.Component:
    return rx.table.root(
        rx.table.header(
            rx.table.row(
                rx.table.column_header_cell("Número"),
                rx.table.column_header_cell("Segurado"),
                rx.table.column_header_cell("Seguradora"),
                rx.table.column_header_cell("Operação"),
                rx.table.column_header_cell("Prêmio total"),
                rx.table.column_header_cell("Vigência fim"),
                rx.table.column_header_cell(""),
            )
        ),
        rx.table.body(
            rx.foreach(
                SeguroState.itens,
                lambda item: rx.table.row(
                    rx.table.cell(item["numero"]),
                    rx.table.cell(item["segurado"]),
                    rx.table.cell(item["seguradora"]),
                    rx.table.cell(item["tipo_operacao"]),
                    rx.table.cell(item["premio_total"]),
                    rx.table.cell(item["vigencia_fim"]),
                    rx.table.cell(
                        rx.hstack(
                            rx.button(
                                "Editar",
                                size="1",
                                variant="soft",
                                on_click=SeguroState.abrir_edicao(item["id"]),
                            ),
                            rx.button(
                                "Desativar",
                                size="1",
                                variant="soft",
                                color_scheme="red",
                                on_click=SeguroState.desativar(item["id"]),
                            ),
                            spacing="2",
                        )
                    ),
                ),
            )
        ),
        width="100%",
    )


def seguros_page() -> rx.Component:
    return app_shell(
        rx.vstack(
            rx.hstack(
                rx.heading("Seguros", size="6"),
                rx.spacer(),
                rx.input(
                    placeholder="Buscar por número...",
                    value=SeguroState.busca,
                    on_change=SeguroState.set_busca,
                    width="320px",
                ),
                rx.button("Nova apólice", on_click=SeguroState.abrir_novo),
                width="100%",
                align="center",
            ),
            _tabela(),
            _dialog_form(),
            spacing="4",
            width="100%",
        )
    )
