"""Segurado (cliente) — substitui `segurado` e `segurado_docs`.

Campos derivados do que a IA de leitura de proposta (api/ler-proposta.js) e
o formulário de cadastro (js/gestao-segurado.js) manipulam no legado.
"""
from __future__ import annotations

import datetime as dt
from typing import Optional

from sqlmodel import Field

from gestao_py.models.base import TabelaBase


class Segurado(TabelaBase, table=True):
    __tablename__ = "segurados"

    tipo_pessoa: str = "PF"  # "PF" ou "PJ"
    nome: str = Field(index=True)
    cpf_cnpj: str = Field(unique=True, index=True)
    data_nascimento: Optional[dt.date] = None
    sexo: Optional[str] = None
    estado_civil_id: Optional[int] = Field(default=None, foreign_key="estados_civis.id")

    telefone: Optional[str] = None
    email: Optional[str] = None

    cep: Optional[str] = None
    logradouro: Optional[str] = None
    numero: Optional[str] = None
    complemento: Optional[str] = None
    bairro: Optional[str] = None
    cidade: Optional[str] = None
    uf: Optional[str] = None

    observacao: Optional[str] = None
    corretor_id: Optional[int] = Field(default=None, foreign_key="usuarios.id")

    ativo: bool = True
    criado_em: dt.datetime = Field(default_factory=dt.datetime.utcnow)
    atualizado_em: dt.datetime = Field(default_factory=dt.datetime.utcnow)


class SeguradoDocumento(TabelaBase, table=True):
    __tablename__ = "segurado_documentos"

    segurado_id: int = Field(foreign_key="segurados.id", index=True)
    tipo_documento_id: Optional[int] = Field(default=None, foreign_key="tipos_documento.id")
    nome_arquivo: str
    url_arquivo: str
    criado_em: dt.datetime = Field(default_factory=dt.datetime.utcnow)
