"""Estado do módulo Seguros (apólices) — CRUD completo.

Porta o núcleo de gestao-seguro.js: `carregarSeguros`/`_salvarSeguroInterno`/
`proximoNumeroSeguro`/`_aplicarTravaFinanceiraSeguro`. A geração de número e
a trava financeira, que no legado rodavam no browser (race condition numa,
burlável via DevTools na outra), aqui vivem no backend — ver
services/numbering.py e services/authz.py.
"""
from __future__ import annotations

import datetime as dt
from typing import Optional

import reflex as rx
from sqlmodel import select

from gestao_py.auth.state import AuthState
from gestao_py.models.lookups import FormaPagamento, Ramo, StatusSeguro
from gestao_py.models.segurado import Segurado
from gestao_py.models.seguradora import Seguradora
from gestao_py.models.seguro import Seguro
from gestao_py.services.audit import log_action
from gestao_py.services.authz import pode_editar_financeiro_travado
from gestao_py.services.numbering import proximo_numero_seguro


class SeguroState(AuthState):
    itens: list[dict] = []
    busca: str = ""
    carregando: bool = False
    mensagem_erro: str = ""
    mensagem_sucesso: str = ""

    modal_aberto: bool = False
    editando_id: Optional[int] = None
    form_valores: dict[str, str] = {}
    financeiro_travado_atual: bool = False

    opcoes_segurados: list[dict] = []
    opcoes_seguradoras: list[dict] = []
    opcoes_ramos: list[dict] = []
    opcoes_formas_pagamento: list[dict] = []
    opcoes_status: list[dict] = []

    def on_load(self):
        yield from self.exigir_login()
        if self.usuario_id is not None:
            self.carregar_opcoes()
            self.carregar()

    def carregar_opcoes(self):
        with rx.session() as session:
            self.opcoes_segurados = [
                {"id": str(s.id), "label": f"{s.nome} — {s.cpf_cnpj}"}
                for s in session.exec(
                    select(Segurado).where(Segurado.ativo == True).order_by(Segurado.nome)  # noqa: E712
                ).all()
            ]
            self.opcoes_seguradoras = [
                {"id": str(s.id), "label": s.nome}
                for s in session.exec(select(Seguradora).where(Seguradora.ativo == True)).all()  # noqa: E712
            ]
            self.opcoes_ramos = [
                {"id": str(r.id), "label": r.nome}
                for r in session.exec(select(Ramo).where(Ramo.ativo == True)).all()  # noqa: E712
            ]
            self.opcoes_formas_pagamento = [
                {"id": str(f.id), "label": f.nome}
                for f in session.exec(select(FormaPagamento).where(FormaPagamento.ativo == True)).all()  # noqa: E712
            ]
            self.opcoes_status = [
                {"id": str(s.id), "label": s.nome}
                for s in session.exec(select(StatusSeguro).where(StatusSeguro.ativo == True)).all()  # noqa: E712
            ]

    def carregar(self):
        self.carregando = True
        with rx.session() as session:
            query = select(Seguro).where(Seguro.ativo == True)  # noqa: E712
            if self.busca.strip():
                termo = f"%{self.busca.strip()}%"
                query = query.where(
                    (Seguro.numero.ilike(termo)) | (Seguro.numero_apolice.ilike(termo))
                )
            resultados = session.exec(query.order_by(Seguro.criado_em.desc())).all()

            segurado_por_id = {s.id: s.nome for s in session.exec(select(Segurado)).all()}
            seguradora_por_id = {s.id: s.nome for s in session.exec(select(Seguradora)).all()}

            self.itens = [
                {
                    "id": s.id,
                    "numero": s.numero,
                    "segurado": segurado_por_id.get(s.segurado_id, "—"),
                    "seguradora": seguradora_por_id.get(s.seguradora_id, "—") if s.seguradora_id else "—",
                    "tipo_operacao": s.tipo_operacao or "—",
                    "premio_total": f"{s.premio_total:,.2f}" if s.premio_total else "—",
                    "vigencia_fim": s.vigencia_fim.isoformat() if s.vigencia_fim else "—",
                    "financeiro_travado": s.financeiro_travado,
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
        self.financeiro_travado_atual = False
        self.mensagem_erro = ""
        self.modal_aberto = True

    def abrir_edicao(self, item_id: int):
        with rx.session() as session:
            s = session.get(Seguro, item_id)
            if s is None:
                return
            self.editando_id = s.id
            self.financeiro_travado_atual = s.financeiro_travado
            self.form_valores = {
                "segurado_id": str(s.segurado_id) if s.segurado_id else "",
                "seguradora_id": str(s.seguradora_id) if s.seguradora_id else "",
                "ramo_id": str(s.ramo_id) if s.ramo_id else "",
                "forma_pagamento_id": str(s.forma_pagamento_id) if s.forma_pagamento_id else "",
                "status_id": str(s.status_id) if s.status_id else "",
                "tipo_operacao": s.tipo_operacao or "",
                "numero_proposta": s.numero_proposta or "",
                "numero_apolice": s.numero_apolice or "",
                "premio_liquido": str(s.premio_liquido) if s.premio_liquido else "",
                "premio_total": str(s.premio_total) if s.premio_total else "",
                "iof": str(s.iof) if s.iof else "",
                "qtd_parcelas": str(s.qtd_parcelas) if s.qtd_parcelas else "",
                "valor_parcela": str(s.valor_parcela) if s.valor_parcela else "",
                "vigencia_inicio": s.vigencia_inicio.isoformat() if s.vigencia_inicio else "",
                "vigencia_fim": s.vigencia_fim.isoformat() if s.vigencia_fim else "",
            }
        self.mensagem_erro = ""
        self.modal_aberto = True

    def fechar_modal(self):
        self.modal_aberto = False

    def definir_modal_aberto(self, aberto: bool):
        self.modal_aberto = aberto

    @staticmethod
    def _float_ou_none(valor: str) -> Optional[float]:
        valor = (valor or "").strip().replace(".", "").replace(",", ".")
        return float(valor) if valor else None

    @staticmethod
    def _int_ou_none(valor: str) -> Optional[int]:
        valor = (valor or "").strip()
        return int(valor) if valor else None

    @staticmethod
    def _data_ou_none(valor: str) -> Optional[dt.date]:
        valor = (valor or "").strip()
        return dt.date.fromisoformat(valor) if valor else None

    def salvar(self, form_data: dict):
        self.mensagem_erro = ""

        segurado_id = self._int_ou_none(form_data.get("segurado_id"))
        if segurado_id is None:
            self.mensagem_erro = "Selecione o segurado."
            return

        # Trava financeira: só nível >= 5 pode alterar campos financeiros
        # de uma apólice já travada. Verificado aqui, no servidor — o
        # legado só desabilitava o campo na UI (_aplicarTravaFinanceiraSeguro),
        # o que não impede uma chamada direta à API.
        if self.editando_id is not None and self.financeiro_travado_atual:
            if not pode_editar_financeiro_travado(self.nivel_acesso):
                self.mensagem_erro = (
                    "Esta apólice está com o financeiro travado (já conciliado). "
                    "Apenas usuários de nível 5+ podem editar esses campos."
                )
                return

        dados = {
            "segurado_id": segurado_id,
            "seguradora_id": self._int_ou_none(form_data.get("seguradora_id")),
            "ramo_id": self._int_ou_none(form_data.get("ramo_id")),
            "forma_pagamento_id": self._int_ou_none(form_data.get("forma_pagamento_id")),
            "status_id": self._int_ou_none(form_data.get("status_id")),
            "tipo_operacao": (form_data.get("tipo_operacao") or "").strip() or None,
            "numero_proposta": (form_data.get("numero_proposta") or "").strip() or None,
            "numero_apolice": (form_data.get("numero_apolice") or "").strip() or None,
            "premio_liquido": self._float_ou_none(form_data.get("premio_liquido")),
            "premio_total": self._float_ou_none(form_data.get("premio_total")),
            "iof": self._float_ou_none(form_data.get("iof")),
            "qtd_parcelas": self._int_ou_none(form_data.get("qtd_parcelas")),
            "valor_parcela": self._float_ou_none(form_data.get("valor_parcela")),
            "vigencia_inicio": self._data_ou_none(form_data.get("vigencia_inicio")),
            "vigencia_fim": self._data_ou_none(form_data.get("vigencia_fim")),
        }

        with rx.session() as session:
            if self.editando_id is not None:
                s = session.get(Seguro, self.editando_id)
                antes = {"numero": s.numero, "premio_total": s.premio_total}
                for campo, valor in dados.items():
                    setattr(s, campo, valor)
                s.atualizado_em = dt.datetime.utcnow()
                session.add(s)
                session.flush()
                log_action(
                    session,
                    usuario_id=self.usuario_id,
                    acao="update",
                    entidade="seguro",
                    registro_id=s.id,
                    antes=antes,
                    depois=dados,
                )
            else:
                numero = proximo_numero_seguro(session)
                s = Seguro(numero=numero, **dados)
                session.add(s)
                session.flush()
                log_action(
                    session,
                    usuario_id=self.usuario_id,
                    acao="create",
                    entidade="seguro",
                    registro_id=s.id,
                    depois={**dados, "numero": numero},
                )

            session.commit()

        self.modal_aberto = False
        self.mensagem_sucesso = "Apólice salva com sucesso."
        self.carregar()

    def desativar(self, item_id: int):
        with rx.session() as session:
            s = session.get(Seguro, item_id)
            if s is None:
                return
            s.ativo = False
            session.add(s)
            log_action(
                session,
                usuario_id=self.usuario_id,
                acao="update",
                entidade="seguro",
                registro_id=s.id,
                antes={"ativo": True},
                depois={"ativo": False},
            )
            session.commit()
        self.carregar()
