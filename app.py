import os
from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from datetime import timedelta
from flasgger import Swagger
from dotenv import load_dotenv

# Importando rotas
from routes.users import user_route
from routes.projects import projects_route
from routes.lists import list_route
from routes.tasks import tasks_route
from routes.comments import comments_route

app = Flask(__name__)
jwt = JWTManager(app)

# Carregando variáveis de ambiente do arquivo .env
load_dotenv()

app.json.sort_keys = False
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=1)

# Rota raiz para verificar se a API está funcionando
@app.route("/")
def api_status():
    """
    Rota raiz para verificar se a API está funcionando.
    ---
    tags:
        - Root
    operationId: "api_status"
    responses:
        200:
            description: API funcionando corretamente
    """
    
    return jsonify({"message": "Api funcionando."})

# Registrando blueprints
app.register_blueprint(user_route)
app.register_blueprint(projects_route, url_prefix='/user/projects')
app.register_blueprint(list_route, url_prefix='/user/projects/<project_id>/lists')
app.register_blueprint(tasks_route, url_prefix='/user/projects/<project_id>/lists/<list_id>/tasks')
app.register_blueprint(comments_route, url_prefix='/user/projects/<project_id>/lists/<list_id>/tasks/<task_id>/comments')

# Tratamento de token expirado
@jwt.expired_token_loader
def my_expired_token_callback(jwt_header, jwt_payload):
    return jsonify({"error": "Sua sessão expirou. Por favor, faça login novamente."}), 401

# Tratamento de token inválido
@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({"error": "Sessão inválida. Por favor, faça login para continuar."}), 422

# Tratamento de token ausente
@jwt.unauthorized_loader
def my_missing_token_callback(error):
    return jsonify({"error": "Nenhum token encontrado. Por favor, faça login para continuar."}), 401

# Configuração do Swagger
swagger_template = {
    "info": {
        "title": "API de Gestão de Projetos",
        "version": "1.0",
        "description": "API para gerenciar projetos, estilo trello",
    },
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "Cole o ACCESS TOKEN aqui. Ex: Bearer {token}"
        },
    },
    
}

# Inicializa o Swagger
swagger = Swagger(app, template=swagger_template)

# Executa a aplicação
if __name__ == '__main__':
    debug = os.getenv("FLASK_DEBUG", "False") == "True"
    app.run(debug=True)