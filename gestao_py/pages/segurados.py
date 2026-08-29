"""Página Segurados — lista, busca e formulário de criação/edição."""
from __future__ import annotations

import reflex as rx

from gestao_py.components.layout import app_shell
from gestao_py.state.segurado_state import SeguradoState


def _campo(label: str, name: str, **kwargs) -> rx.Component:
    return rx.vstack(
        rx.text(label, size="1", color="gray"),
        rx.input(
            name=name,
            default_value=SeguradoState.form_valores.get(name, ""),
            **kwargs,
        ),
        spacing="1",
        width="100%",
    )


def _dialog_form() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(
                rx.cond(SeguradoState.editando_id, "Editar segurado", "Novo segurado")
            ),
            rx.form(
                rx.vstack(
                    rx.cond(
                        SeguradoState.mensagem_erro != "",
                        rx.callout(SeguradoState.mensagem_erro, color_scheme="red", size="1"),
                    ),
                    rx.hstack(
                        _campo("Nome / Razão social", "nome"),
                        _campo("CPF / CNPJ", "cpf_cnpj"),
                        width="100%",
                        spacing="3",
                    ),
                    rx.hstack(
                        _campo("Telefone", "telefone"),
                        _campo("E-mail", "email"),
                        width="100%",
                        spacing="3",
                    ),
                    rx.hstack(
                        _campo("CEP", "cep"),
                        _campo("Cidade", "cidade"),
                        _campo("UF", "uf"),
                        width="100%",
                        spacing="3",
                    ),
                    rx.hstack(
                        _campo("Logradouro", "logradouro"),
                        _campo("Número", "numero"),
                        _campo("Complemento", "complemento"),
                        _campo("Bairro", "bairro"),
                        width="100%",
                        spacing="3",
                    ),
                    _campo("Observação", "observacao"),
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
                on_submit=SeguradoState.salvar,
                reset_on_submit=False,
            ),
            max_width="640px",
        ),
        open=SeguradoState.modal_aberto,
        on_open_change=SeguradoState.definir_modal_aberto,
    )


def _tabela() -> rx.Component:
    return rx.table.root(
        rx.table.header(
            rx.table.row(
                rx.table.column_header_cell("Nome"),
                rx.table.column_header_cell("CPF/CNPJ"),
                rx.table.column_header_cell("Telefone"),
                rx.table.column_header_cell("Cidade/UF"),
                rx.table.column_header_cell(""),
            )
        ),
        rx.table.body(
            rx.foreach(
                SeguradoState.itens,
                lambda item: rx.table.row(
                    rx.table.cell(item["nome"]),
                    rx.table.cell(item["cpf_cnpj"]),
                    rx.table.cell(item["telefone"]),
                    rx.table.cell(item["cidade_uf"]),
                    rx.table.cell(
                        rx.hstack(
                            rx.button(
                                "Editar",
                                size="1",
                                variant="soft",
                                on_click=SeguradoState.abrir_edicao(item["id"]),
                            ),
                            rx.button(
                                "Desativar",
                                size="1",
                                variant="soft",
                                color_scheme="red",
                                on_click=SeguradoState.desativar(item["id"]),
                            ),
                            spacing="2",
                        )
                    ),
                ),
            )
        ),
        width="100%",
    )


def segurados_page() -> rx.Component:
    return app_shell(
        rx.vstack(
            rx.hstack(
                rx.heading("Segurados", size="6"),
                rx.spacer(),
                rx.input(
                    placeholder="Buscar por nome ou CPF/CNPJ...",
                    value=SeguradoState.busca,
                    on_change=SeguradoState.set_busca,
                    width="320px",
                ),
                rx.button("Novo segurado", on_click=SeguradoState.abrir_novo),
                width="100%",
                align="center",
            ),
            _tabela(),
            _dialog_form(),
            spacing="4",
            width="100%",
        )
    )
