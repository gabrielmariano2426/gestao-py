"""Consultas públicas de CEP e CNPJ (ViaCEP / BrasilAPI).

Substitui as chamadas equivalentes feitas direto do browser em
gestao-segurado.js (`segBuscarCep`, `consultarReceitaCpfCnpj`). Movidas para
o backend porque são chamadas de rede — não porque exigissem uma chave
secreta (essas duas APIs são públicas e gratuitas).

A consulta de CPF via "Hub" proprietário citada no legado (`_consultarCpfViaHub`,
que embrulha `apicpf.com`) não foi portada nesta fase por depender de uma
chave/URL do provedor que não está disponível aqui — ver ROADMAP.md.
"""
from __future__ import annotations

from typing import Optional, TypedDict

import httpx


class EnderecoCep(TypedDict, total=False):
    cep: str
    logradouro: str
    bairro: str
    cidade: str
    uf: str


class DadosCnpj(TypedDict, total=False):
    razao_social: str
    logradouro: str
    numero: str
    bairro: str
    cidade: str
    uf: str
    cep: str


async def buscar_endereco_por_cep(cep: str) -> Optional[EnderecoCep]:
    cep_limpo = "".join(c for c in cep if c.isdigit())
    if len(cep_limpo) != 8:
        return None
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(f"https://viacep.com.br/ws/{cep_limpo}/json/")
    if resp.status_code != 200:
        return None
    data = resp.json()
    if data.get("erro"):
        return None
    return {
        "cep": cep_limpo,
        "logradouro": data.get("logradouro", ""),
        "bairro": data.get("bairro", ""),
        "cidade": data.get("localidade", ""),
        "uf": data.get("uf", ""),
    }


async def buscar_cnpj(cnpj: str) -> Optional[DadosCnpj]:
    cnpj_limpo = "".join(c for c in cnpj if c.isdigit())
    if len(cnpj_limpo) != 14:
        return None
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(f"https://brasilapi.com.br/api/cnpj/v1/{cnpj_limpo}")
    if resp.status_code != 200:
        return None
    data = resp.json()
    return {
        "razao_social": data.get("razao_social", ""),
        "logradouro": data.get("logradouro", ""),
        "numero": data.get("numero", ""),
        "bairro": data.get("bairro", ""),
        "cidade": data.get("municipio", ""),
        "uf": data.get("uf", ""),
        "cep": data.get("cep", ""),
    }
