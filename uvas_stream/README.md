# Uva Viva

Uva Viva é um catálogo web para explorar variedades de uvas e organizar informações sobre seus produtores e colheitas. O painel apresenta uma introdução à viticultura e indicadores de volume e valor dos lotes cadastrados.

## Funcionalidades

- Cadastro, consulta, edição e exclusão de variedades, com cor, origem, perfil de sabor e descrição.
- Cadastro, consulta, edição e exclusão de produtores e propriedades.
- Cadastro, consulta, edição e exclusão de lotes, vinculando cada colheita a uma variedade e a um produtor.
- Cálculo do valor estimado dos lotes com base na quantidade e no preço por quilo.

## Requisitos

- Python 3.10 ou superior.
- [uv](https://docs.astral.sh/uv/).

## Executar localmente

Por padrão, o sistema usa SQLite e cria o banco em `data/uvas.db`.

```bash
uv sync
uv run streamlit run src/app.py
```

O Streamlit exibirá o endereço local no terminal, normalmente `http://localhost:8501`. O arquivo SQLite é criado automaticamente na primeira execução.

## Configurar MySQL

Em produção, defina `APP_ENV=production` e `DATABASE_URL` com a URL de conexão. O driver PyMySQL já está incluído nas dependências.

Exemplo em Bash:

```bash
export APP_ENV=production
export DATABASE_URL='mysql+pymysql://usuario:senha@host:3306/uvas?charset=utf8mb4'
uv run streamlit run src/app.py
```

Exemplo em PowerShell:

```powershell
$env:APP_ENV = "production"
$env:DATABASE_URL = "mysql+pymysql://usuario:senha@host:3306/uvas?charset=utf8mb4"
uv run streamlit run src/app.py
```

Crie o banco `uvas` previamente no servidor MySQL. Use credenciais próprias para a aplicação, restrinja os privilégios desse usuário e não versione URLs ou senhas. O sistema cria as tabelas na primeira inicialização; alterações futuras de esquema devem ser tratadas com migrações.

## Deploy no Streamlit Community Cloud

1. Publique este repositório em um provedor Git acessível pelo Streamlit Community Cloud.
2. Crie uma aplicação apontando para `uvas_stream/src/app.py`. O `requirements.txt`
   da raiz do repositório encaminha a instalação para `uvas_stream/requirements.txt`.
3. Configure os segredos da aplicação na área **Settings > Secrets**:

```toml
APP_ENV = "production"
DATABASE_URL = "mysql+pymysql://usuario:senha@host:3306/uvas?charset=utf8mb4"
```

O código aceita `DATABASE_URL` e `APP_ENV` tanto como variáveis de ambiente quanto como segredos do Streamlit. O servidor MySQL precisa aceitar conexões do ambiente de deploy.

## Estrutura

```text
src/
  app.py        # interface Streamlit e páginas CRUD
  database.py   # engine, sessões e configuração de banco
  models.py     # modelos persistentes SQLAlchemy
```

O modo padrão é local/SQLite. Ao definir `APP_ENV=production`, a aplicação exige uma URL `mysql+...` e falha de forma explícita se a configuração estiver ausente ou apontar para outro banco.