from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from datetime import timedelta
from routes.users import user_route
from routes.projects import projects_route
from routes.lists import list_route
from routes.tasks import tasks_route
from routes.comments import comments_route
from flasgger import Swagger

app = Flask(__name__)
app.json.sort_keys = False
app.config["JWT_SECRET_KEY"] = "8d5111adeddaafe18a2118d05d12281ffd05af27248cabccbde3dec49d9e987f"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=1)
jwt = JWTManager(app)

swagger_template = {
    "info": {
        "title": "API de Gestão de Projetos",
        "version": "1.0",
        "description": "API para gerenciar projetos, estilo trello",
        "contact": {
            "name": "Vitor Henrique | Lukas Gomes | Allysson Ferreira",
        }
    },
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "Cole o ACCESS TOKEN aqui"
        },
        "RefreshToken": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "Cole o REFRESH TOKEN aqui"
        }
    },
    
}

swagger = Swagger(app, template=swagger_template)


app.register_blueprint(user_route)
app.register_blueprint(projects_route, url_prefix='/user/projects')
app.register_blueprint(list_route, url_prefix='/user/projects/<project_id>/lists')
app.register_blueprint(tasks_route, url_prefix='/user/projects/<project_id>/lists/<list_id>/tasks')
app.register_blueprint(comments_route, url_prefix='/user/projects/<project_id>/lists/<list_id>/tasks/<task_id>/comments')

@app.route("/")
def api():
    """
    API ESTA FUNCIONANDO
    ---
    responses:
        200:
            description: API funcionando corretamente
    """
    
    return jsonify(msg="Api funcionando.")

@jwt.expired_token_loader
def my_expired_token_callback(jwt_header, jwt_payload):
    return jsonify({
        "msg": "Sua sessão expirou. Por favor, faça login novamente.",
    }), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({
        "msg": "Sessão inválida. Por favor, faça login para continuar.",
    }), 422

@jwt.unauthorized_loader
def my_missing_token_callback(error):
    return jsonify({
        "msg": "Nenhum token encontrado. Por favor, faça login para continuar.",
    }), 401

if __name__ == '__main__':
    app.run(debug=True)