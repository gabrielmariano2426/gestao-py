"""Página Dashboard — KPIs e filas do dia."""
from __future__ import annotations

import reflex as rx

from gestao_py.components.layout import app_shell
from gestao_py.state.dashboard_state import DashboardState


def _kpi_card(titulo: str, valor: rx.Var) -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.text(titulo, size="2", color="gray"),
            rx.heading(valor, size="7"),
            spacing="1",
        ),
        width="100%",
    )


def _fila_renovacoes() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.heading(f"Renovações — {DashboardState.fila_label}", size="4"),
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.table.column_header_cell("Nº apólice"),
                        rx.table.column_header_cell("Segurado"),
                        rx.table.column_header_cell("Vigência fim"),
                    )
                ),
                rx.table.body(
                    rx.foreach(
                        DashboardState.fila_renovacoes,
                        lambda item: rx.table.row(
                            rx.table.cell(item["numero"]),
                            rx.table.cell(item["segurado"]),
                            rx.table.cell(item["vigencia_fim"]),
                        ),
                    )
                ),
                width="100%",
            ),
            align="stretch",
            width="100%",
        ),
        width="100%",
    )


def _fila_parcelas() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.heading(f"Parcelas — {DashboardState.fila_label}", size="4"),
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.table.column_header_cell("Nº apólice"),
                        rx.table.column_header_cell("Parcela"),
                        rx.table.column_header_cell("Valor"),
                        rx.table.column_header_cell("Vencimento"),
                    )
                ),
                rx.table.body(
                    rx.foreach(
                        DashboardState.fila_parcelas,
                        lambda item: rx.table.row(
                            rx.table.cell(item["numero_seguro"]),
                            rx.table.cell(item["numero_parcela"]),
                            rx.table.cell(item["valor"]),
                            rx.table.cell(item["data_vencimento"]),
                        ),
                    )
                ),
                width="100%",
            ),
            align="stretch",
            width="100%",
        ),
        width="100%",
    )


def dashboard_page() -> rx.Component:
    return app_shell(
        rx.vstack(
            rx.heading("Dashboard", size="6"),
            rx.grid(
                _kpi_card("Segurados ativos", DashboardState.total_segurados),
                _kpi_card("Apólices ativas", DashboardState.total_seguros_ativos),
                _kpi_card("Vencendo no range de hoje", DashboardState.renovacoes_30_dias),
                columns="3",
                spacing="4",
                width="100%",
            ),
            rx.grid(
                _fila_renovacoes(),
                _fila_parcelas(),
                columns="2",
                spacing="4",
                width="100%",
            ),
            spacing="4",
            width="100%",
        )
    )
