"""Hash e verificação de senha.

Corrige o achado mais grave da revisão do sistema legado: `realizarLogin()`
comparava `String(data.senha||'').trim() !== senha` — a senha do usuário
trafegava e era comparada em **texto plano**, direto no navegador, contra a
coluna `c02usuario.senha` lida com a chave anônima do Supabase. Aqui a senha
nunca é armazenada nem comparada em texto plano: só o hash bcrypt trafega
entre o formulário e o banco.
"""
from __future__ import annotations

from passlib.context import CryptContext

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_senha(senha_plana: str) -> str:
    return _pwd_context.hash(senha_plana)


def verificar_senha(senha_plana: str, senha_hash: str) -> bool:
    try:
        return _pwd_context.verify(senha_plana, senha_hash)
    except ValueError:
        # hash malformado/legado — nunca autentica silenciosamente
        return False
