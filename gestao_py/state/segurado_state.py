"""Estado do módulo Segurados — CRUD completo.

Porta `carregarSegurados`/`salvarSegurado`/`verificarCpfCnpjDuplicado`/
`toggleAtivoSegurado` de js/gestao-segurado.js. A checagem de CPF/CNPJ
duplicado, que no legado era só uma consulta client-side antes de salvar
(alguém podia salvar em paralelo e furar a checagem), aqui vira uma
constraint `unique` no banco (ver models/segurado.py) — a validação no
handler só existe para dar uma mensagem de erro amigável antes de bater
na constraint.
"""
from __future__ import annotations

import datetime as dt
from typing import Optional

import reflex as rx
from sqlmodel import select

from gestao_py.auth.state import AuthState
from gestao_py.models.segurado import Segurado
from gestao_py.services.audit import log_action
from gestao_py.services.cep_cnpj import buscar_cnpj, buscar_endereco_por_cep


class SeguradoState(AuthState):
    itens: list[dict] = []
    busca: str = ""
    carregando: bool = False
    mensagem_erro: str = ""
    mensagem_sucesso: str = ""

    modal_aberto: bool = False
    editando_id: Optional[int] = None
    form_valores: dict[str, str] = {}

    def on_load(self):
        yield from self.exigir_login()
        if self.usuario_id is not None:
            self.carregar()

    def carregar(self):
        self.carregando = True
        with rx.session() as session:
            query = select(Segurado).where(Segurado.ativo == True)  # noqa: E712
            if self.busca.strip():
                termo = f"%{self.busca.strip()}%"
                query = query.where(
                    (Segurado.nome.ilike(termo)) | (Segurado.cpf_cnpj.ilike(termo))
                )
            resultados = session.exec(query.order_by(Segurado.nome)).all()
            self.itens = [
                {
                    "id": s.id,
                    "nome": s.nome,
                    "cpf_cnpj": s.cpf_cnpj,
                    "tipo_pessoa": s.tipo_pessoa,
                    "telefone": s.telefone or "",
                    "email": s.email or "",
                    "cidade": s.cidade or "",
                    "uf": s.uf or "",
                    "cidade_uf": f"{s.cidade or ''}/{s.uf or ''}" if (s.cidade or s.uf) else "—",
                }
                for s in resultados
            ]
        self.carregando = False

    def set_busca(self, valor: str):
        self.busca = valor
        self.carregar()

    def abrir_novo(self):
        self.editando_id = None
        self.form_valores = {}
        self.mensagem_erro = ""
        self.modal_aberto = True

    def abrir_edicao(self, item_id: int):
        with rx.session() as session:
            s = session.get(Segurado, item_id)
            if s is None:
                return
            self.editando_id = s.id
            self.form_valores = {
                "tipo_pessoa": s.tipo_pessoa,
                "nome": s.nome,
                "cpf_cnpj": s.cpf_cnpj,
                "telefone": s.telefone or "",
                "email": s.email or "",
                "cep": s.cep or "",
                "logradouro": s.logradouro or "",
                "numero": s.numero or "",
                "complemento": s.complemento or "",
                "bairro": s.bairro or "",
                "cidade": s.cidade or "",
                "uf": s.uf or "",
                "observacao": s.observacao or "",
            }
        self.mensagem_erro = ""
        self.modal_aberto = True

    def fechar_modal(self):
        self.modal_aberto = False

    def definir_modal_aberto(self, aberto: bool):
        self.modal_aberto = aberto

    async def buscar_cep(self, cep: str):
        endereco = await buscar_endereco_por_cep(cep)
        if endereco is None:
            return
        self.form_valores = {
            **self.form_valores,
            "cep": endereco.get("cep", self.form_valores.get("cep", "")),
            "logradouro": endereco.get("logradouro", ""),
            "bairro": endereco.get("bairro", ""),
            "cidade": endereco.get("cidade", ""),
            "uf": endereco.get("uf", ""),
        }

    async def buscar_cnpj_action(self, cnpj: str):
        dados = await buscar_cnpj(cnpj)
        if dados is None:
            return
        self.form_valores = {
            **self.form_valores,
            "nome": dados.get("razao_social", self.form_valores.get("nome", "")),
            "logradouro": dados.get("logradouro", ""),
            "numero": dados.get("numero", ""),
            "bairro": dados.get("bairro", ""),
            "cidade": dados.get("cidade", ""),
            "uf": dados.get("uf", ""),
            "cep": dados.get("cep", ""),
        }

    def salvar(self, form_data: dict):
        self.mensagem_erro = ""
        nome = (form_data.get("nome") or "").strip()
        cpf_cnpj = "".join(c for c in (form_data.get("cpf_cnpj") or "") if c.isdigit())

        if not nome or not cpf_cnpj:
            self.mensagem_erro = "Nome e CPF/CNPJ são obrigatórios."
            return
        if len(cpf_cnpj) not in (11, 14):
            self.mensagem_erro = "CPF deve ter 11 dígitos ou CNPJ 14 dígitos."
            return

        with rx.session() as session:
            duplicado = session.exec(
                select(Segurado).where(
                    Segurado.cpf_cnpj == cpf_cnpj, Segurado.id != self.editando_id
                )
            ).first()
            if duplicado is not None:
                self.mensagem_erro = f"Já existe um segurado com este CPF/CNPJ: {duplicado.nome}."
                return

            dados = {
                "tipo_pessoa": "PJ" if len(cpf_cnpj) == 14 else "PF",
                "nome": nome,
                "cpf_cnpj": cpf_cnpj,
                "telefone": (form_data.get("telefone") or "").strip() or None,
                "email": (form_data.get("email") or "").strip() or None,
                "cep": (form_data.get("cep") or "").strip() or None,
                "logradouro": (form_data.get("logradouro") or "").strip() or None,
                "numero": (form_data.get("numero") or "").strip() or None,
                "complemento": (form_data.get("complemento") or "").strip() or None,
                "bairro": (form_data.get("bairro") or "").strip() or None,
                "cidade": (form_data.get("cidade") or "").strip() or None,
                "uf": (form_data.get("uf") or "").strip().upper() or None,
                "observacao": (form_data.get("observacao") or "").strip() or None,
            }

            if self.editando_id is not None:
                s = session.get(Segurado, self.editando_id)
                antes = {"nome": s.nome, "cpf_cnpj": s.cpf_cnpj}
                for campo, valor in dados.items():
                    setattr(s, campo, valor)
                s.atualizado_em = dt.datetime.utcnow()
                session.add(s)
                session.flush()
                log_action(
                    session,
                    usuario_id=self.usuario_id,
                    acao="update",
                    entidade="segurado",
                    registro_id=s.id,
                    antes=antes,
                    depois=dados,
                )
            else:
                s = Segurado(**dados)
                session.add(s)
                session.flush()
                log_action(
                    session,
                    usuario_id=self.usuario_id,
                    acao="create",
                    entidade="segurado",
                    registro_id=s.id,
                    depois=dados,
                )

            session.commit()

        self.modal_aberto = False
        self.mensagem_sucesso = "Segurado salvo com sucesso."
        self.carregar()

    def desativar(self, item_id: int):
        with rx.session() as session:
            s = session.get(Segurado, item_id)
            if s is None:
                return
            s.ativo = False
            session.add(s)
            log_action(
                session,
                usuario_id=self.usuario_id,
                acao="update",
                entidade="segurado",
                registro_id=s.id,
                antes={"ativo": True},
                depois={"ativo": False},
            )
            session.commit()
        self.carregar()
