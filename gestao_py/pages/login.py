"""Tela de login — substitui `realizarLogin()` do index.html legado.

Diferença essencial: a senha digitada nunca é comparada em texto plano em
lugar nenhum (nem client, nem log) — só o backend recebe o form e chama
`verificar_senha()` contra o hash bcrypt armazenado.
"""
from __future__ import annotations

import reflex as rx

from gestao_py.auth.state import AuthState
from gestao_py.config import APP_NAME


def login_page() -> rx.Component:
    return rx.center(
        rx.card(
            rx.vstack(
                rx.heading(APP_NAME, size="5"),
                rx.text("Entre com seu usuário e senha.", color="gray", size="2"),
                rx.form(
                    rx.vstack(
                        rx.input(
                            name="codigo_usr",
                            placeholder="Usuário",
                            size="3",
                            auto_focus=True,
                        ),
                        rx.input(
                            name="senha",
                            placeholder="Senha",
                            type="password",
                            size="3",
                        ),
                        rx.cond(
                            AuthState.erro_login != "",
                            rx.callout(AuthState.erro_login, color_scheme="red", size="1"),
                        ),
                        rx.button("Entrar", type="submit", size="3", width="100%"),
                        spacing="3",
                        width="100%",
                    ),
                    on_submit=AuthState.fazer_login,
                    reset_on_submit=False,
                    width="100%",
                ),
                spacing="4",
                width="100%",
            ),
            width="360px",
        ),
        height="100vh",
    )
