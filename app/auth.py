from datetime import datetime, timedelta
from typing import Optional, List
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel


import os
from dotenv import load_dotenv

load_dotenv()

# Configurações
SECRET_KEY = os.environ.get('SECRET_KEY')
ALGORITHM = os.environ.get('ALGORITHM')
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7

# Configuração do contexto de criptografia para hash de senhas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Esquema OAuth2 com caminho do token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Banco de dados fictício de usuários

users_db = {
    "usuario": {
        "username": "usuario",
        "full_name": "Usuário",
        "email": "user@email.com",
        "hashed_password": pwd_context.hash("teste"),
        "disabled": False,
        "permissions": ["GET:/producao", "GET:/processamento"]  # Permissões do usuário
    },
    "admin": {
        "username": "admin",
        "full_name": "Admin Usuário",
        "email": "admin@usuario.com",
        "hashed_password": pwd_context.hash("admin"),
        "disabled": False,
        "permissions": [],
        "is_admin": True
    }
}


class TokenData(BaseModel):
    """Modelo para os dados do token"""
    username: Optional[str] = None


def verify_password(plain_password, hashed_password):
    """
    Verifica se a senha fornecida corresponde à senha hash armazenada.

    :param plain_password: Senha fornecida pelo usuário.
    :param hashed_password: Senha hash armazenada.
    :return: True se a senha corresponder, False caso contrário.
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """
    Gera um hash para a senha fornecida.

    :param password: Senha a ser hasheada.
    :return: Hash da senha.
    """
    return pwd_context.hash(password)


def get_user(db, username: str):
    """
    Obtém um usuário do banco de dados fictício.

    :param db: Banco de dados fictício.
    :param username: Nome de usuário.
    :return: Dicionário do usuário ou None se o usuário não for encontrado.
    """
    if username in db:
        user_dict = db[username]
        return user_dict

def authenticate_user(fake_db, username: str, password: str):
    """
    Autentica um usuário verificando suas credenciais.

    :param fake_db: Banco de dados fictício.
    :param username: Nome de usuário.
    :param password: Senha do usuário.
    :return: Dicionário do usuário autenticado ou False se a autenticação falhar.
    """
    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user["hashed_password"]):
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Cria um token JWT para o usuário.

    :param data: Dados a serem codificados no token.
    :param expires_delta: Tempo de expiração do token.
    :return: Token JWT codificado.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Obtém o usuário atual a partir do token JWT.

    :param token: Token JWT.
    :return: Dicionário do usuário atual.
    :raises HTTPException: Se o token for inválido ou o usuário não for encontrado.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não autorizado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

def check_permissions(user_permissions: List[str], method: str, path: str) -> bool:
    """
    Verifica se o usuário tem permissões para acessar o endpoint.

    :param user_permissions: Lista de permissões do usuário.
    :param method: Método HTTP da requisição.
    :param path: Caminho do endpoint.
    :return: True se o usuário tiver permissão, False caso contrário.
    """
    required_permission = f"{method}:{path}"
    return required_permission in user_permissions


async def get_current_active_user(current_user = Depends(get_current_user)):
    """
    Obtém o usuário ativo atual.

    :param current_user: Dicionário do usuário atual.
    :return: Dicionário do usuário ativo.
    :raises HTTPException: Se o usuário estiver desativado.
    """
    if current_user.get("disabled"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Usuário não encontrado")
    return current_user


def authorize_user(user, method, path):
    """
    Autoriza o usuário para acessar um endpoint específico.

    :param user: Dicionário do usuário.
    :param method: Método HTTP da requisição.
    :param path: Caminho do endpoint.
    :raises HTTPException: Se o usuário não tiver permissão para acessar o endpoint.
    """
    if user.get("is_admin"):
        return
    if not check_permissions(user["permissions"], method, path):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário sem permissão"
        )


def is_admin_user(user):
    """
    Verifica se o usuário é administrador.

    :param user: Dicionário do usuário.
    :return: True se o usuário for administrador, False caso contrário.
    """
    return user.get("is_admin", False)