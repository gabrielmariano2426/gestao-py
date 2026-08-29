"""Popula o banco com dados mínimos para desenvolvimento/demonstração.

Uso:
    python -m gestao_py.scripts.seed

Cria as tabelas (via `SQLModel.metadata.create_all()` — atalho de
desenvolvimento; em produção use `reflex db init/makemigrations/migrate`,
que gera migrações Alembic versionadas sobre o mesmo metadata), um usuário
admin e alguns registros de exemplo.
"""
from __future__ import annotations

import datetime as dt

import reflex as rx
from reflex.model import get_engine
from sqlmodel import SQLModel, select

from gestao_py.auth.security import hash_senha
from gestao_py.models.lookups import Empresa, EstadoCivil, FormaPagamento, Ramo, StatusSeguro, TipoDocumento
from gestao_py.models.segurado import Segurado
from gestao_py.models.seguradora import Seguradora
from gestao_py.models.seguro import Seguro
from gestao_py.models.usuario import Usuario

ADMIN_CODIGO = "admin"
ADMIN_SENHA = "trocar123"  # apenas para dev local — troque no primeiro login real


def _get_or_create(session, model, nome: str, **extra):
    obj = session.exec(select(model).where(model.nome == nome)).first()
    if obj is None:
        obj = model(nome=nome, **extra)
        session.add(obj)
        session.flush()
    return obj


def seed() -> None:
    SQLModel.metadata.create_all(get_engine())

    with rx.session() as session:
        if session.exec(select(Usuario).where(Usuario.codigo_usr == ADMIN_CODIGO)).first() is None:
            session.add(
                Usuario(
                    codigo_usr=ADMIN_CODIGO,
                    nome="Administrador",
                    apelido="Admin",
                    senha_hash=hash_senha(ADMIN_SENHA),
                    nivel_acesso=6,
                )
            )

        _get_or_create(session, Empresa, "Master Parceria")
        for nome in ("Solteiro(a)", "Casado(a)", "Divorciado(a)", "Viúvo(a)"):
            _get_or_create(session, EstadoCivil, nome)
        for nome in ("Boleto", "Cartão de Crédito", "Débito em Conta", "PIX"):
            _get_or_create(session, FormaPagamento, nome)
        for nome in ("Auto", "Residencial", "Vida", "Empresarial", "Outros"):
            _get_or_create(session, Ramo, nome)
        for nome in ("Em Cotação", "Emitido", "Vigente", "Cancelado", "Não Renovado"):
            _get_or_create(session, StatusSeguro, nome)
        for nome in ("CNH", "RG", "Comprovante de Residência", "Apólice", "Proposta"):
            _get_or_create(session, TipoDocumento, nome)

        seguradora = _get_or_create(session, Seguradora, "Porto Seguro")
        _get_or_create(session, Seguradora, "Azul Seguros")
        _get_or_create(session, Seguradora, "HDI Seguros")

        session.commit()

        segurado = session.exec(select(Segurado).where(Segurado.cpf_cnpj == "12345678900")).first()
        if segurado is None:
            segurado = Segurado(
                tipo_pessoa="PF",
                nome="Maria Exemplo da Silva",
                cpf_cnpj="12345678900",
                telefone="(85) 99999-0000",
                email="maria.exemplo@example.com",
                cidade="Fortaleza",
                uf="CE",
            )
            session.add(segurado)
            session.flush()

        ramo_auto = session.exec(select(Ramo).where(Ramo.nome == "Auto")).first()
        status_vigente = session.exec(select(StatusSeguro).where(StatusSeguro.nome == "Vigente")).first()

        ja_tem_seguro = session.exec(select(Seguro).where(Seguro.segurado_id == segurado.id)).first()
        if ja_tem_seguro is None:
            from gestao_py.services.numbering import proximo_numero_seguro

            numero = proximo_numero_seguro(session)
            session.add(
                Seguro(
                    numero=numero,
                    segurado_id=segurado.id,
                    seguradora_id=seguradora.id,
                    ramo_id=ramo_auto.id if ramo_auto else None,
                    status_id=status_vigente.id if status_vigente else None,
                    tipo_operacao="NOVO",
                    premio_liquido=1200.00,
                    premio_total=1450.00,
                    iof=45.00,
                    qtd_parcelas=10,
                    valor_parcela=145.00,
                    vigencia_inicio=dt.date.today(),
                    vigencia_fim=dt.date.today() + dt.timedelta(days=365),
                )
            )

        session.commit()

    print(f"Seed concluído. Login de teste: usuário='{ADMIN_CODIGO}' senha='{ADMIN_SENHA}'.")


if __name__ == "__main__":
    seed()
