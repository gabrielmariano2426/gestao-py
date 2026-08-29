"""Cobre proximo_numero_seguro: formato YYNNNNN e ausência de colisão em
criações sequenciais (a race condition sob concorrência real só é evitada
pelo SELECT...FOR UPDATE do Postgres, que o SQLite de teste não exercita —
ver o comentário em services/numbering.py sobre o dialect check)."""
import datetime as dt

from sqlmodel import Session, SQLModel, create_engine

from gestao_py.models.seguro import SequenciaSeguro
from gestao_py.services.numbering import proximo_numero_seguro


def _memory_session() -> Session:
    engine = create_engine("sqlite://")
    SQLModel.metadata.create_all(engine, tables=[SequenciaSeguro.__table__])
    return Session(engine)


def test_formato_yynnnnn():
    with _memory_session() as session:
        numero = proximo_numero_seguro(session, ano=2026)
        assert numero == "2600001"
        assert len(numero) == 7


def test_incrementa_sequencialmente_sem_colisao():
    with _memory_session() as session:
        numeros = {proximo_numero_seguro(session, ano=2026) for _ in range(20)}
        assert len(numeros) == 20  # nenhuma colisão
        assert numeros == {f"26{i:05d}" for i in range(1, 21)}


def test_anos_diferentes_tem_sequencias_independentes():
    with _memory_session() as session:
        n1 = proximo_numero_seguro(session, ano=2025)
        n2 = proximo_numero_seguro(session, ano=2026)
        assert n1 == "2500001"
        assert n2 == "2600001"


def test_usa_ano_atual_por_padrao():
    with _memory_session() as session:
        numero = proximo_numero_seguro(session)
        ano2_esperado = dt.date.today().year % 100
        assert numero.startswith(f"{ano2_esperado:02d}")
