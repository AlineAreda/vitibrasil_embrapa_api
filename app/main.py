from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from app.auth import authenticate_user, create_access_token, get_current_active_user, fake_users_db, ACCESS_TOKEN_EXPIRE_MINUTES
from app.routes.routes import router

tags_metadata = [
    {
        "name": "Auth",
        "description": "Endpoints relacionados à autenticação",
    },
    {
        "name": "Produção",
        "description": "Endpoints relacionados à produção de vinhos, sucos e derivados.",
    },
    {
        "name": "Processamento",
        "description": "Endpoints relacionados à quantidade de uvas processadas.",
    },
    {
        "name": "Comercialização",
        "description": "Endpoints relacionados à comercialização de vinhos e derivados.",
    },
    {
        "name": "Importação",
        "description": "Endpoints relacionados à importação de derivados de uva",
    },
    {
        "name": "Exportação",
        "description": "Endpoints relacionados à exportação de derivados de uva",
    },
    {   
        "name": "Página Inicial",
        "description": "Banco de dados de uva, vinho e derivados",
    }
]

app = FastAPI(
    title="API  Vitivinicultura- Dados de uva, vinho e derivados.",
    description="API para obter dados de uva, vinho e derivados do site [Embrapa Uva e Vinho](http://vitibrasil.cnpuv.embrapa.br/index.php?opcao=opt_01).",
    version="0.0.1",
    openapi_tags=tags_metadata,
)

@app.get("/",
        response_model=dict, 
        tags=["Página Inicial"], 
        summary='Página Inicial', 
        description='Página Inicial')
def root():
    return {"message": "Banco de dados de uva, vinho e derivados"}

@app.post("/token", 
        response_model=dict, 
        tags=["Auth"], 
        summary='Autenticar usuário', 
        description='Gera um token JWT para autenticação'
        )
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=dict, 
        tags=["Auth"], 
        summary='Obter informações do usuário autenticado', 
        description='Retorna as informações do usuário baseado no token JWT')
async def read_users_me(current_user = Depends(get_current_active_user)):
    return current_user

app.include_router(router, prefix="/vitibrasil/api/v1" )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

