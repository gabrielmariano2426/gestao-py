"""Geração atômica do número de apólice, no formato legado `YYNNNNN`.

O legado (`proximoNumeroSeguro()` em gestao-seguro.js) calculava isso como
"maior número existente com esse prefixo de ano, mais 1" — direto no
browser, sem lock nenhum. Sob duas criações simultâneas, ambas podem ler o
mesmo "maior número" e gerar o mesmo próximo número. Aqui, um contador
dedicado por ano (`SequenciaSeguro`) é lido com `SELECT...FOR UPDATE` e
incrementado dentro da mesma transação da criação da apólice, o que
serializa concorrência no nível do banco.

O formato de saída (2 dígitos de ano + 5 dígitos de sequência) é preservado
de propósito: links de documento já emitidos pelo sistema legado (que
embutem esse número num hash de sufixo, ver ROADMAP.md) continuam válidos.
"""
from __future__ import annotations

import datetime as dt

from sqlmodel import Session, select

from gestao_py.models.seguro import SequenciaSeguro


def proximo_numero_seguro(session: Session, ano: int | None = None) -> str:
    ano_base = ano if ano is not None else dt.date.today().year
    ano2 = ano_base % 100

    query = select(SequenciaSeguro).where(SequenciaSeguro.ano == ano2)
    if session.bind is not None and session.bind.dialect.name != "sqlite":
        query = query.with_for_update()

    seq = session.exec(query).first()
    if seq is None:
        seq = SequenciaSeguro(ano=ano2, ultimo_numero=0)
        session.add(seq)
        session.flush()

    seq.ultimo_numero += 1
    session.add(seq)
    session.flush()

    return f"{ano2:02d}{seq.ultimo_numero:05d}"
