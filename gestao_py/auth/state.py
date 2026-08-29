"""Estado de autenticação — sessão real de servidor, não `localStorage`.

O browser guarda apenas um token opaco (cookie `session_token`); todo dado
de identidade/permissão (`nivel_acesso` incluso) é relido de `usuario_sessoes`
+ `usuarios` a cada checagem de página, nunca confiado a partir do cliente.
Isso fecha a brecha do legado onde `nivel_acesso` vinha só do objeto salvo
em `localStorage.usuarioAtual`, editável via DevTools.
"""
from __future__ import annotations

import datetime as dt
import secrets
from typing import Optional

import reflex as rx
from sqlmodel import select

from gestao_py.auth.security import verificar_senha
from gestao_py.models.usuario import Usuario, UsuarioSessao
from gestao_py.services.audit import log_action


class AuthState(rx.State):
    session_token: str = rx.Cookie("", name="session_token", same_site="lax")

    usuario_id: Optional[int] = None
    codigo_usr: str = ""
    nome: str = ""
    nivel_acesso: int = 0
    erro_login: str = ""

    @rx.var
    def esta_autenticado(self) -> bool:
        return self.usuario_id is not None

    def checar_sessao(self):
        """Método interno (não é event handler de UI): só atualiza o
        estado local, nunca dispara redirect sozinho. Quem decide se deve
        redirecionar é `exigir_login`, que é o que as páginas chamam.
        """
        if self.usuario_id is not None:
            return
        if not self.session_token:
            self._forcar_logout_local()
            return

        with rx.session() as session:
            sessao = session.exec(
                select(UsuarioSessao).where(
                    UsuarioSessao.token == self.session_token,
                    UsuarioSessao.logout_em == None,  # noqa: E711
                )
            ).first()
            if sessao is None:
                self._forcar_logout_local()
                return

            usuario = session.get(Usuario, sessao.usuario_id)
            if usuario is None or not usuario.ativo:
                self._forcar_logout_local()
                return

            self.usuario_id = usuario.id
            self.codigo_usr = usuario.codigo_usr
            self.nome = usuario.nome
            self.nivel_acesso = usuario.nivel_acesso

    def fazer_login(self, form_data: dict):
        codigo = (form_data.get("codigo_usr") or "").strip()
        senha = form_data.get("senha") or ""
        self.erro_login = ""

        if not codigo or not senha:
            self.erro_login = "Informe usuário e senha."
            return

        with rx.session() as session:
            usuario = session.exec(
                select(Usuario).where(Usuario.codigo_usr == codigo)
            ).first()

            # Mensagem genérica de propósito: não revelar se o usuário existe.
            if usuario is None or not usuario.ativo or not verificar_senha(senha, usuario.senha_hash):
                self.erro_login = "Usuário ou senha inválidos."
                return

            token = secrets.token_urlsafe(32)
            session.add(UsuarioSessao(usuario_id=usuario.id, token=token))
            log_action(
                session,
                usuario_id=usuario.id,
                acao="login",
                entidade="usuario",
                registro_id=usuario.id,
            )
            session.commit()

            self.session_token = token
            self.usuario_id = usuario.id
            self.codigo_usr = usuario.codigo_usr
            self.nome = usuario.nome
            self.nivel_acesso = usuario.nivel_acesso

        return rx.redirect("/")

    def fazer_logout(self):
        with rx.session() as session:
            sessao = session.exec(
                select(UsuarioSessao).where(UsuarioSessao.token == self.session_token)
            ).first()
            if sessao is not None:
                sessao.logout_em = dt.datetime.utcnow()
                session.add(sessao)
                session.commit()

        self._forcar_logout_local()
        return rx.redirect("/login")

    def _forcar_logout_local(self):
        self.session_token = ""
        self.usuario_id = None
        self.codigo_usr = ""
        self.nome = ""
        self.nivel_acesso = 0

    def exigir_login(self):
        """on_load helper para páginas protegidas.

        É um gerador (usa `yield`) de propósito: outros event handlers
        (ex.: `SeguradoState.on_load`) encadeiam com `yield from
        self.exigir_login()` para propagar o redirect corretamente — chamar
        `self.exigir_login()` sem `yield from`/`return` descartaria o
        evento de redirect silenciosamente.
        """
        self.checar_sessao()
        if self.usuario_id is None:
            yield rx.redirect("/login")
