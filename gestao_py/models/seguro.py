"""Seguro (apólice) — substitui `seguro`, `c51condutores`, `c38parcela`, `seguro_docs`.

`numero` preserva o formato legado `YYNNNNN` (ano de 2 dígitos + sequência de
5 dígitos) para não quebrar links de documento já emitidos (ver api/doc.js
no sistema legado, que embute esse número no hash de sufixo). A geração
atômica desse número vive em services/numbering.py — não em código de UI —
porque o legado usa "maior número + 1", que tem race condition sob criação
concorrente.
"""
from __future__ import annotations

import datetime as dt
from typing import Optional

from sqlmodel import Field

from gestao_py.models.base import TabelaBase


class Seguro(TabelaBase, table=True):
    __tablename__ = "seguros"

    numero: str = Field(unique=True, index=True)  # formato YYNNNNN

    segurado_id: int = Field(foreign_key="segurados.id", index=True)
    seguradora_id: Optional[int] = Field(default=None, foreign_key="seguradoras.id")
    ramo_id: Optional[int] = Field(default=None, foreign_key="ramos.id")
    forma_pagamento_id: Optional[int] = Field(default=None, foreign_key="formas_pagamento.id")
    status_id: Optional[int] = Field(default=None, foreign_key="status_seguro.id")
    corretor_id: Optional[int] = Field(default=None, foreign_key="usuarios.id")

    tipo_operacao: Optional[str] = None  # NOVO | RENOVAÇÃO | ENDOSSO
    numero_proposta: Optional[str] = None
    numero_apolice: Optional[str] = None

    premio_liquido: Optional[float] = None
    premio_total: Optional[float] = None
    iof: Optional[float] = None
    qtd_parcelas: Optional[int] = None
    valor_parcela: Optional[float] = None

    vigencia_inicio: Optional[dt.date] = None
    vigencia_fim: Optional[dt.date] = None

    cartao_emitido: bool = False

    # Trava financeira: quando True, edição de campos financeiros exige
    # nivel_acesso >= 5 (ver services/authz.py) — replica
    # `_aplicarTravaFinanceiraSeguro` do legado, mas checado no servidor,
    # não só escondido na UI.
    financeiro_travado: bool = False

    ativo: bool = True
    criado_em: dt.datetime = Field(default_factory=dt.datetime.utcnow)
    atualizado_em: dt.datetime = Field(default_factory=dt.datetime.utcnow)


class Condutor(TabelaBase, table=True):
    __tablename__ = "condutores"

    seguro_id: int = Field(foreign_key="seguros.id", index=True)
    nome: str
    cpf: Optional[str] = None
    data_nascimento: Optional[dt.date] = None


class Parcela(TabelaBase, table=True):
    __tablename__ = "parcelas"

    seguro_id: int = Field(foreign_key="seguros.id", index=True)
    numero_parcela: int
    data_vencimento: dt.date = Field(index=True)
    valor: float
    paga: bool = False
    pago_em: Optional[dt.datetime] = None


class SeguroDocumento(TabelaBase, table=True):
    __tablename__ = "seguro_documentos"

    seguro_id: int = Field(foreign_key="seguros.id", index=True)
    tipo_documento_id: Optional[int] = Field(default=None, foreign_key="tipos_documento.id")
    nome_arquivo: str
    url_arquivo: str
    criado_em: dt.datetime = Field(default_factory=dt.datetime.utcnow)


class SequenciaSeguro(TabelaBase, table=True):
    """Contador atômico por ano-base, usado por services/numbering.py.

    Substitui o esquema legado `proximoNumeroSeguro()` (maior número
    existente + 1, calculado no browser), que tem race condition sob
    criação concorrente de apólices. Uma linha por ano, travada com
    SELECT...FOR UPDATE antes do incremento.
    """

    __tablename__ = "sequencias_seguro"

    ano: int = Field(unique=True, index=True)  # ano de 2 dígitos, ex. 26
    ultimo_numero: int = 0
