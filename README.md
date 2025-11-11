# API de Gerenciamento de Projetos

Esta é uma API REST desenvolvida em Flask para a disciplina de Linguagem de Programação. O projeto simula um sistema de gerenciamento de tarefas (similar ao Trello), com foco na autenticação de usuários e persistência de dados em arquivos CSV.

---

## 👥 Equipe

* [Lukas Gomes](https://github.com/lukasgdev)
* [Allysson Matheus](https://github.com/AllyssonFerreira12)
* [Vitor Henrique](https://github.com/vitorhxnrique)

---

## 🛠️ Tecnologias Utilizadas

* **Python 3**
* **Flask:** O micro-framework principal para a criação da API.
* **Flask-JWT-Extended:** Para gerenciamento da autenticação via JSON Web Tokens.
* **Werkzeug:** Para hashing e verificação de senhas de usuário.

---

## 🚀 Como Rodar o Projeto Localmente

Siga estes passos para configurar e executar a aplicação em seu ambiente local.

### Pré-requisitos

* Python 3.8 ou superior
* `pip` (gerenciador de pacotes do Python)
* Postman ou VS Code (com a extensão do Postman) para testar os endpoints.

### 1. Clone o Repositório

```bash
git clone [URL_DO_SEU_REPOSITORIO]
cd projeto_kanban_api
```

### 2. Crie e Ative um Ambiente Virtual

É uma boa prática isolar as dependências do projeto.

**No Windows:**
```bash
python -m venv .venv
.\.venv\Scripts\activate
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

### 5. Execute a Aplicação

Basta executar o arquivo `app.py`.

```bash
python app.py
```

O servidor estará rodando no modo de debug em `http://127.0.0.1:5000`.

---

## 🗺️ Endpoints Principais da API

A estrutura das rotas foi desenhada para ser segura, onde a maioria dos endpoints parte de `/user` para se referir ao usuário logado.

### Autenticação (Público)
* `POST /registrar`: Cria um novo usuário (nome, email, senha).
* `POST /login`: Autentica um usuário (email, senha) e retorna os tokens de acesso e atualização.

### Usuário (Protegido)
* `GET /user`: Retorna os dados do perfil do usuário logado.
* `PUT /user`: Atualiza os dados (nome, email) do usuário logado.

### Projetos (Protegido)
* `GET /user/projetos`: Lista todos os projetos que pertencem ao usuário logado.
* `POST /user/projetos`: Cria um novo projeto para o usuário.
* `GET /user/projetos/<id_projeto>`: Busca um projeto específico do usuário.
* `DELETE /user/projetos/<id_projeto>`: Deleta um projeto específico do usuário.

### Colunas (Protegido)
* `GET /user/projetos/<id_projeto>/colunas`: Lista as colunas de um projeto específico.
* `POST /user/projetos/<id_projeto>/colunas`: Cria uma nova coluna no projeto.
* `DELETE /user/projetos/<id_projeto>/colunas/<id_coluna>`: Deleta uma coluna específica.

### Tarefas (Protegido)
* `GET /user/projetos/<...>/colunas/<id_coluna>/tarefas`: Lista as tarefas de uma coluna.
* `POST /user/projetos/<...>/colunas/<id_coluna>/tarefas`: Cria uma nova tarefa na coluna.
* `PUT /user/projetos/<...>/tarefas/<id_tarefa>`: Atualiza uma tarefa (ex: move para outra coluna).
* `DELETE /user/projetos/<...>/tarefas/<id_tarefa>`: Deleta uma tarefa.

### Comentários (Protegido)
* `GET /user/projetos/<...>/tarefas/<id_tarefa>/comentarios`: Lista os comentários de uma tarefa.
* `POST /user/projetos/<...>/tarefas/<id_tarefa>/comentarios`: Cria um novo comentário na tarefa.

