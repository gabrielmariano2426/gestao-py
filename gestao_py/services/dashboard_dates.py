"""Cálculo do intervalo de dias "hoje" usado pelas filas de renovação e
parcela do dashboard.

Porte literal de `_calcularRangeDiasHoje()` em gestao-dashboard.js (linhas
19-59 do legado) — a regra existe porque o escritório fecha no fim de
semana: sexta já mostra o que vence sábado/domingo, e segunda "recupera" o
que venceu durante o fim de semana. É uma regra de negócio pequena mas fácil
de errar numa reescrita, por isso está isolada aqui com testes dedicados
(ver tests/test_dashboard_ranges.py) em vez de embutida na query do dashboard.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass


@dataclass(frozen=True)
class RangeDiasHoje:
    datas: list[dt.date]
    label: str


def calcular_range_dias_hoje(hoje: dt.date | None = None) -> RangeDiasHoje:
    hoje = hoje or dt.date.today()
    dow = (hoje.weekday() + 1) % 7  # Python: seg=0..dom=6  ->  JS: dom=0..sab=6

    def add_days(n: int) -> dt.date:
        return hoje + dt.timedelta(days=n)

    if 2 <= dow <= 4:  # terça a quinta: só hoje
        return RangeDiasHoje(datas=[hoje], label="Hoje")

    if dow == 1:  # segunda: sex+sáb+dom+seg
        return RangeDiasHoje(
            datas=[add_days(-3), add_days(-2), add_days(-1), hoje],
            label="Hoje e Fim de Semana",
        )

    if dow == 5:  # sexta: sex+sáb+dom
        return RangeDiasHoje(
            datas=[hoje, add_days(1), add_days(2)],
            label="Hoje e Fim de Semana",
        )

    if dow == 6:  # sábado: sex+sáb+dom
        return RangeDiasHoje(
            datas=[add_days(-1), hoje, add_days(1)],
            label="Hoje e Fim de Semana",
        )

    # domingo (dow == 0): sex+sáb+dom+seg
    return RangeDiasHoje(
        datas=[add_days(-2), add_days(-1), hoje, add_days(1)],
        label="Hoje e Fim de Semana",
    )
