"""Ponto de entrada do app Reflex — registra as páginas.

Substitui o index.html único do legado por rotas reais (`reflex` compila
cada `rx.app.page` numa rota de verdade, com URL própria e suporte a
recarregar a página sem perder a sessão — diferente da SPA legada, que
navegava trocando `display:none`/`display:block` sem nunca mudar a URL).
"""
from __future__ import annotations

import reflex as rx

from gestao_py.pages.dashboard import dashboard_page
from gestao_py.pages.login import login_page
from gestao_py.pages.segurados import segurados_page
from gestao_py.pages.seguros import seguros_page
from gestao_py.state.dashboard_state import DashboardState
from gestao_py.state.segurado_state import SeguradoState
from gestao_py.state.seguro_state import SeguroState

app = rx.App()

app.add_page(login_page, route="/login", title="Login")
app.add_page(dashboard_page, route="/", title="Dashboard", on_load=DashboardState.on_load)
app.add_page(segurados_page, route="/segurados", title="Segurados", on_load=SeguradoState.on_load)
app.add_page(seguros_page, route="/seguros", title="Seguros", on_load=SeguroState.on_load)
