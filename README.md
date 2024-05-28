# API - Vitibrasil Embrapa 

Esse projeto foi desenvolvido para atender aos objetivos do Tech Challenge da Fase 1 da Pós Graduação em Machine Learning Engineering, turma 1MLET. 

### Objetivo

O trabalho envolve analisar os dados de vitivinicultura da Embrapa, os quais estão disponíveis na seguinte URL: [Vitibrasil Embrapa](http://vitibrasil.cnpuv.embrapa.br/index.php?opcao=opt_01).

A ideia do projeto é a criação de uma API pública de consulta nos dados do site nas respectivas abas:

-   /produção
-   /processamento
-   /comercialização
-   /importação
-   /exportação

A API vai servir para alimentar uma base de dados que futuramente será usada para um modelo de Machine Learning.


### Visão Geral do Projeto
![extração de dados](https://github.com/AlineAreda/vitibrasil_embrapa_api/assets/77371831/9dee90e7-ae6c-452f-b899-0e597f70c8b3)


##  Configuração e Execução

1.  Clone o repositório:
```bash
https://github.com/AlineAreda/vitibrasil_embrapa_api.git
```
2.  Crie e ative o ambiente virtual:
```bash
python3 -m venv venv
source venv/bin/activate

# se windons
python -m venv venv
.venv\Scripts\activate

```
3.  Instale as dependências:
```bash
pip install -r requirements.txt
```
Este aplicativo pode ser configurado com variáveis ​​de ambiente.

Você pode criar o arquivo `.env` no diretório raiz e colocar todos
variáveis ​​de ambiente aqui.

4.  Configure as variáveis de ambiente criando um arquivo `.env`:
```bash
SECRET_KEY=seu-secret-key
ALGORITHM=HS256
```
5.  Executando a Aplicação Localmente:
```bash
uvicorn app.main:app --reload
```
Acesse a documentação da API no navegador: http://localhost:8000/docs

### Pré-requisitos
-   Python 3.9 ou superior
-   Git
-   Ambiente virtual Python


## Dependências
- FastAPI
- Uvicorn
- python-jose
- bcrypt
- Pydantic
- Pandas
- Requests
- BeautifulSoup4
-  dotenv


## Estrutura atual do projeto

```bash
VITIBRASIL_EMBRAPA/
├── app/
│   ├── routes/
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── utils_data/
│   │   ├── csv/
│   │   │   ├── download_csv.py
│   │   │   └── transform_csv.py
│   │   ├── web_scraping/
│   │   │   ├── __init__.py
│   │   │   ├── scraping_base.py
│   │   │   ├── scraping_comercializacao.py
│   │   │   ├── scraping_exportacao.py
│   │   │   ├── scraping_importacao.py
│   │   │   ├── scraping_processamento.py
│   │   │   └── scraping_producao.py
│   ├── constants.py
│   ├── utils.py
│   ├── auth.py
│   ├── main.py
│   └── requirements.txt
├── .env
├── .gitignore
├── README.md
└── requirements.txt
```


## Endpoints

![endpoints](https://github.com/AlineAreda/vitibrasil_embrapa_api/assets/77371831/8a4c4f26-ad45-442a-9d58-68fd2e452b7b)

## Autenticação

A API utiliza tokens JWT (JSON Web Tokens) para gerenciar a autenticação. Quando um usuário faz login, ele recebe um token JWT que deve ser enviado nos cabeçalhos das requisições futuras para acessar endpoints protegidos.

Para autenticar um usuário e obter um token JWT, é necessário acessar o endpoint `/token`, fornecendo as credenciais de login (nome de usuário e senha) no corpo da requisição. Se as credenciais forem validadas com sucesso, o endpoint retornará um token JWT válido.

Na implementação atual, o arquivo `auth.py` contém um dicionário que simula um banco de dados de usuários, incluindo suas respectivas permissões, para fins de autenticação. ***Verifique***


#### Exemplo de Chamada API GET/producao
![exemplo de resposta](https://github.com/AlineAreda/vitibrasil_embrapa_api/assets/77371831/2a4c8c1b-5c9c-4048-9054-7db4351db5c3)



#### Modelo para sequências de fases com deploy na AWS
![entrega-da-primeira-fase-tech-chalenge-ML](https://github.com/AlineAreda/vitibrasil_embrapa_api/assets/77371831/cefcf939-f0b9-4620-85ce-a1403b6335dc)


## Contribuição

1.  Faça um fork do projeto.
2.  Crie uma branch para sua feature (`git checkout -b feature/SuaFeature`).
3.  Faça commit das suas alterações (`git commit -m 'Add Feature'`).
4.  Envie para a branch (`git push origin feature/SuaFeature`).
5.  Abra um Pull Request.


## Licença

Distribuído sob a licença MIT. Veja `LICENSE` para mais informações.
