from gestao_py.auth.security import hash_senha, verificar_senha
from gestao_py.services.authz import (
    AutorizacaoNegada,
    exigir_nivel,
    pode_editar_financeiro_travado,
    pode_ver_auditoria_completa,
)


def test_hash_nunca_igual_a_senha_plana():
    senha_hash = hash_senha("minhaSenha123")
    assert senha_hash != "minhaSenha123"


def test_verificar_senha_correta():
    senha_hash = hash_senha("minhaSenha123")
    assert verificar_senha("minhaSenha123", senha_hash) is True


def test_verificar_senha_incorreta():
    senha_hash = hash_senha("minhaSenha123")
    assert verificar_senha("senhaErrada", senha_hash) is False


def test_verificar_senha_hash_malformado_nao_autentica():
    assert verificar_senha("qualquer", "isso-nao-e-um-hash-bcrypt") is False


def test_pode_editar_financeiro_travado():
    assert pode_editar_financeiro_travado(5) is True
    assert pode_editar_financeiro_travado(4) is False


def test_pode_ver_auditoria_completa():
    assert pode_ver_auditoria_completa(5) is True
    assert pode_ver_auditoria_completa(4) is False


def test_exigir_nivel_levanta_quando_insuficiente():
    try:
        exigir_nivel(2, 5, acao="editar campo financeiro")
        assert False, "deveria ter levantado AutorizacaoNegada"
    except AutorizacaoNegada:
        pass


def test_exigir_nivel_nao_levanta_quando_suficiente():
    exigir_nivel(5, 5, acao="editar campo financeiro")
