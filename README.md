# API de Gerenciamento de Projetos

API RESTful desenvolvida em Python com Flask para gerenciamento de projetos, listas e tarefas (estilo Kanban/Trello). O sistema utiliza persistência de dados em arquivos CSV e autenticação segura via JWT.

---

## 👥 Equipe

* [Lukas Gomes](https://github.com/lukasgdev)
* [Allysson Matheus](https://github.com/AllyssonFerreira12)
* [Vitor Henrique](https://github.com/vitorhxnrique)

---

## 🚀 Funcionalidades

- **Autenticação e Segurança:**
  - Cadastro e Login de usuários com criptografia.
  - Proteção de rotas via **JWT (JSON Web Tokens)**.
  - Verificação de propriedade (usuários só acessam seus próprios projetos).

- **Gestão Hierárquica (CRUD Completo):**
  - **Projetos:** Criação, listagem e edição. Deletar um projeto remove suas listas automaticamente.
  - **Listas:** Colunas dentro do projeto (ex: "A Fazer", "Concluído").
  - **Tarefas:** Cards vinculados às listas.
  - **Comentários:** Interações dentro das tarefas.

- **Dados e Documentação:**
  - **Persistência em Arquivo:** Banco de dados leve usando arquivos `.csv`, sem necessidade de instalar SGBDs.
  - **Swagger UI:** Documentação interativa gerada automaticamente.

---

## 🛠️ Tecnologias Utilizadas

- **Linguagem:** [Python 3](https://www.python.org/)
- **Framework:** [Flask](https://flask.palletsprojects.com/)
- **Autenticação:** [Flask-JWT-Extended](https://flask-jwt-extended.readthedocs.io/)
- **Documentação:** [Flasgger](https://github.com/flasgger/flasgger) (OpenAPI)
- **Utilitários:** `python-dotenv` (Variáveis de ambiente)

---

## 🚀 Como Rodar o Projeto Localmente

Siga estes passos para configurar e executar a aplicação em seu ambiente local.

### Pré-requisitos

* Python 3.8 ou superior
* `pip` (gerenciador de pacotes do Python)
* Postman ou VS Code (com a extensão do Postman) para testar os endpoints.

### 1. Clone o Repositório

```bash
git clone https://github.com/lukasgdev/gestao-de-projetos-api-flask.git
cd gestao-de-projetos-api-flask
```

### 2. Crie e Ative um Ambiente Virtual

É uma boa prática isolar as dependências do projeto.

**No Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**No macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instale as Dependências

O arquivo `requirements.txt` contém todas as bibliotecas necessárias.

```bash
pip install -r requirements.txt
```

### 4. Configuração de Ambiente (.env)

Crie um arquivo chamado `.env` na raiz do projeto e adicione as seguintes configurações:

```bash
FLASK_APP=app.py
FLASK_DEBUG=True
JWT_SECRET_KEY=chave_de_acesso
```

### 5. Execute a Aplicação

Basta executar o arquivo `app.py`.

```bash
python app.py
```

O servidor estará rodando no modo de debug em `http://127.0.0.1:5000`.

### 6. Documentação Interativa (Swagger)

Para testar as rotas visualmente e ver os exemplos de JSON, acesse:

`http://127.0.0.1:5000/apidocs`