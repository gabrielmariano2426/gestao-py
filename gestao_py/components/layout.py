"""Layout comum (barra lateral + topo) para páginas autenticadas.

Substitui o shell fixo que vivia dentro do próprio index.html de 27 mil
linhas do legado — aqui é um componente Python reutilizável, sem duplicar
marcação por página.
"""
from __future__ import annotations

import reflex as rx

from gestao_py.auth.state import AuthState
from gestao_py.config import APP_NAME

_LINKS = [
    ("Dashboard", "/"),
    ("Segurados", "/segurados"),
    ("Seguros", "/seguros"),
]


def _nav_link(texto: str, href: str) -> rx.Component:
    return rx.link(
        texto,
        href=href,
        padding="0.5rem 1rem",
        border_radius="0.375rem",
        color="var(--gray-12)",
        _hover={"background": "var(--gray-4)"},
        weight="medium",
    )


def _sidebar() -> rx.Component:
    return rx.vstack(
        rx.heading(APP_NAME, size="4", padding="1rem"),
        rx.vstack(
            *[_nav_link(texto, href) for texto, href in _LINKS],
            align="stretch",
            width="100%",
            padding_x="0.5rem",
        ),
        rx.spacer(),
        rx.vstack(
            rx.text(AuthState.nome, weight="bold", size="2"),
            rx.text(f"Nível {AuthState.nivel_acesso}", size="1", color="gray"),
            rx.button("Sair", on_click=AuthState.fazer_logout, size="2", variant="soft", width="100%"),
            padding="1rem",
            align="stretch",
            width="100%",
        ),
        height="100vh",
        width="240px",
        border_right="1px solid var(--gray-5)",
        position="sticky",
        top="0",
        align="stretch",
    )


def app_shell(*children: rx.Component) -> rx.Component:
    return rx.hstack(
        _sidebar(),
        rx.box(*children, padding="2rem", width="100%", overflow_y="auto"),
        align="start",
        spacing="0",
        width="100%",
    )
