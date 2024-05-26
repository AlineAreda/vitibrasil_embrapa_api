from datetime import datetime, timedelta
from typing import Optional, List
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel


# Configurações
SECRET_KEY = "teste_chave"  
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Configuração do contexto de criptografia para hash de senhas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Esquema OAuth2 com caminho do token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Banco de dados fictício de usuários
fake_users_db = {
    "exemplo_usuario": {
        "username": "exemplo_usuario",
        "full_name": "Exemplo Usuário",
        "email": "exemplo@usuario.com",
        "hashed_password": pwd_context.hash("senha"),
        "disabled": False,
        "permissions": ["GET:/producao-data", "GET:/processamento-data"]  # Permissões do usuário
    },
    "outro_usuario": {
        "username": "outro_usuario",
        "full_name": "Outro Usuário",
        "email": "outro@usuario.com",
        "hashed_password": pwd_context.hash("outra_senha"),
        "disabled": False,
        "permissions": ["GET:/importacao-data", "GET:/exportacao-data"]  # Permissões do usuário
    },
    "admin": {
        "username": "admin",
        "full_name": "Admin Usuário",
        "email": "admin@usuario.com",
        "hashed_password": pwd_context.hash("admin"),
        "disabled": False,
        "permissions": [],
        "is_admin": True  # Indica que este usuário é um administrador
    }
}

# Modelos
class TokenData(BaseModel):
    username: Optional[str] = None

# Utilitários para manipulação de senhas
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

# Utilitários para manipulação de usuários
def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return user_dict

def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user["hashed_password"]):
        return False
    return user

# Função para criar um token de acesso
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Dependência para obter o usuário atual
async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
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
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

def check_permissions(user_permissions: List[str], method: str, path: str) -> bool:
    required_permission = f"{method}:{path}"
    return required_permission in user_permissions

# Dependência para obter o usuário ativo atual
async def get_current_active_user(current_user = Depends(get_current_user)):
    if current_user.get("disabled"):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

# Função para autorizar o usuário
def authorize_user(user, method, path):
    if user.get("is_admin"):
        return  # Se o usuário for administrador, conceda acesso total
    if not check_permissions(user["permissions"], method, path):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this resource"
        )

# Função para verificar se o usuário é administrador
def is_admin_user(user):
    return user.get("is_admin", False)