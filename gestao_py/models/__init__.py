"""Modelos SQLModel/Reflex do sistema de gestão.

Convenção de nomes: esta reescrita usa nomes de tabela/coluna descritivos
(`usuarios`, `segurados`, `nivel_acesso`) em vez dos códigos crípticos do
legado (`c02usuario`, `c02cod_usr`). O mapeamento de cada tabela nova para a
tabela legada correspondente está documentado em SCHEMA_NOTES.md, na raiz do
projeto — consulte-o antes de escrever qualquer script de migração de dados
reais do Supabase.
"""
from .lookups import Empresa, EstadoCivil, FormaPagamento, Ramo, StatusSeguro, TipoDocumento
from .seguradora import Seguradora
from .segurado import Segurado, SeguradoDocumento
from .seguro import Condutor, Parcela, Seguro, SeguroDocumento, SequenciaSeguro
from .usuario import AuditLog, Usuario, UsuarioSessao

__all__ = [
    "Empresa",
    "EstadoCivil",
    "FormaPagamento",
    "Ramo",
    "StatusSeguro",
    "TipoDocumento",
    "Seguradora",
    "Segurado",
    "SeguradoDocumento",
    "Condutor",
    "Parcela",
    "Seguro",
    "SeguroDocumento",
    "SequenciaSeguro",
    "AuditLog",
    "Usuario",
    "UsuarioSessao",
]
