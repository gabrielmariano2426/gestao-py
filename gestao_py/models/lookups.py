"""Tabelas de referência (listas fixas usadas em formulários e filtros).

Cada classe substitui uma tabela legada do schema Supabase `gestao`:
Empresa->c01empresa, EstadoCivil->c83estadocivil, FormaPagamento->c84formapagamento,
Ramo->c89ramo, StatusSeguro->c80status, TipoDocumento->c86documento.
Colunas foram inferidas do código JS legado (não existe DDL no repo original)
— confira SCHEMA_NOTES.md antes de migrar dados reais.
"""
from __future__ import annotations

from typing import Optional

from sqlmodel import Field

from gestao_py.models.base import TabelaBase


class Empresa(TabelaBase, table=True):
    __tablename__ = "empresas"

    nome: str
    logo_url: Optional[str] = None
    cor_cartao24: Optional[str] = None
    ativo: bool = True


class EstadoCivil(TabelaBase, table=True):
    __tablename__ = "estados_civis"

    nome: str = Field(unique=True)
    ativo: bool = True


class FormaPagamento(TabelaBase, table=True):
    __tablename__ = "formas_pagamento"

    nome: str = Field(unique=True)
    ativo: bool = True


class Ramo(TabelaBase, table=True):
    __tablename__ = "ramos"

    nome: str = Field(unique=True)
    ativo: bool = True


class StatusSeguro(TabelaBase, table=True):
    __tablename__ = "status_seguro"

    nome: str = Field(unique=True)
    cor: Optional[str] = None
    ativo: bool = True


class TipoDocumento(TabelaBase, table=True):
    __tablename__ = "tipos_documento"

    nome: str = Field(unique=True)
    ativo: bool = True
