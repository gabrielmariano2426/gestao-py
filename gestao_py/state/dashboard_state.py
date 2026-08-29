"""Estado do Dashboard — KPIs e filas "hoje" (renovação/parcela).

Porta `carregarDashboard`/`carregarRenovacoesParcelasHoje` de
gestao-dashboard.js, reaproveitando services/dashboard_dates.py para o
range de dias ciente do fim de semana.
"""
from __future__ import annotations

import reflex as rx
from sqlmodel import func, select

from gestao_py.auth.state import AuthState
from gestao_py.models.segurado import Segurado
from gestao_py.models.seguro import Parcela, Seguro
from gestao_py.services.dashboard_dates import calcular_range_dias_hoje


class DashboardState(AuthState):
    total_segurados: int = 0
    total_seguros_ativos: int = 0
    renovacoes_30_dias: int = 0

    fila_label: str = "Hoje"
    fila_renovacoes: list[dict] = []
    fila_parcelas: list[dict] = []

    def on_load(self):
        yield from self.exigir_login()
        if self.usuario_id is not None:
            self.carregar()

    def carregar(self):
        with rx.session() as session:
            self.total_segurados = session.exec(
                select(func.count()).select_from(Segurado).where(Segurado.ativo == True)  # noqa: E712
            ).one()
            self.total_seguros_ativos = session.exec(
                select(func.count()).select_from(Seguro).where(Seguro.ativo == True)  # noqa: E712
            ).one()

            hoje = calcular_range_dias_hoje()
            self.fila_label = hoje.label

            segurado_por_id = {s.id: s.nome for s in session.exec(select(Segurado)).all()}

            renovacoes = session.exec(
                select(Seguro).where(
                    Seguro.ativo == True,  # noqa: E712
                    Seguro.vigencia_fim.in_(hoje.datas),
                )
            ).all()
            self.fila_renovacoes = [
                {
                    "id": s.id,
                    "numero": s.numero,
                    "segurado": segurado_por_id.get(s.segurado_id, "—"),
                    "vigencia_fim": s.vigencia_fim.isoformat() if s.vigencia_fim else "—",
                }
                for s in renovacoes
            ]
            self.renovacoes_30_dias = len(renovacoes)

            parcelas = session.exec(
                select(Parcela).where(
                    Parcela.paga == False,  # noqa: E712
                    Parcela.data_vencimento.in_(hoje.datas),
                )
            ).all()
            seguro_por_id = {s.id: s for s in session.exec(select(Seguro)).all()}
            self.fila_parcelas = [
                {
                    "id": p.id,
                    "numero_seguro": seguro_por_id[p.seguro_id].numero if p.seguro_id in seguro_por_id else "—",
                    "numero_parcela": p.numero_parcela,
                    "valor": f"{p.valor:,.2f}",
                    "data_vencimento": p.data_vencimento.isoformat(),
                }
                for p in parcelas
            ]
