"""Cobre calcular_range_dias_hoje contra os 7 dias da semana, comparando
com o comportamento exato do legado `_calcularRangeDiasHoje`
(gestao-dashboard.js linhas 19-59) — ver services/dashboard_dates.py.
"""
import datetime as dt

from gestao_py.services.dashboard_dates import calcular_range_dias_hoje

# Uma semana de referência fixa: 2026-08-24 (segunda) a 2026-08-30 (domingo).
SEGUNDA = dt.date(2026, 8, 24)
TERCA = dt.date(2026, 8, 25)
QUARTA = dt.date(2026, 8, 26)
QUINTA = dt.date(2026, 8, 27)
SEXTA = dt.date(2026, 8, 28)
SABADO = dt.date(2026, 8, 29)
DOMINGO = dt.date(2026, 8, 30)
PROXIMA_SEGUNDA = dt.date(2026, 8, 31)

# Fim de semana ANTERIOR à SEGUNDA acima (usado só no teste de segunda-feira,
# que "recupera" o fim de semana que já passou — não o próximo).
SEXTA_ANTERIOR = dt.date(2026, 8, 21)
SABADO_ANTERIOR = dt.date(2026, 8, 22)
DOMINGO_ANTERIOR = dt.date(2026, 8, 23)


def test_terca_a_quinta_mostra_so_hoje():
    for dia in (TERCA, QUARTA, QUINTA):
        resultado = calcular_range_dias_hoje(dia)
        assert resultado.datas == [dia]
        assert resultado.label == "Hoje"


def test_segunda_recupera_fim_de_semana():
    resultado = calcular_range_dias_hoje(SEGUNDA)
    assert resultado.datas == [SEXTA_ANTERIOR, SABADO_ANTERIOR, DOMINGO_ANTERIOR, SEGUNDA]
    assert resultado.label == "Hoje e Fim de Semana"


def test_sexta_antecipa_fim_de_semana():
    resultado = calcular_range_dias_hoje(SEXTA)
    assert resultado.datas == [SEXTA, SABADO, DOMINGO]


def test_sabado_mostra_sexta_a_domingo():
    resultado = calcular_range_dias_hoje(SABADO)
    assert resultado.datas == [SEXTA, SABADO, DOMINGO]


def test_domingo_mostra_sexta_a_segunda():
    resultado = calcular_range_dias_hoje(DOMINGO)
    assert resultado.datas == [SEXTA, SABADO, DOMINGO, PROXIMA_SEGUNDA]
