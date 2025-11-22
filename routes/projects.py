from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.csv_service import find_project_by_id, find_user_by_id, get_next_project_id, save_project, find_projects_by_user_id, find_project_by_id, update_project_data, delete_project_data, find_lists_by_project_id
from datetime import datetime

projects_route = Blueprint('projects', __name__)

@projects_route.route('/', methods=['POST'])
@jwt_required()
def create_project():
    """
    criacao de um projeto
    ---
    tags:
        - Projects
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        schema:
          type: object
          properties:
            project_title:
              type: string
            project_description:
              type: string
    responses:
      201:
        description: Projeto criado
      400:
        description: Dados inválidos
      404:
        description: Usuário não encontrado
    """
    
    current_user_id = get_jwt_identity()
    user = find_user_by_id(current_user_id)

    if not user:
        return jsonify(error="Usuário não encontrado"), 404
    
    data = request.json
    title = data.get("project_title")
    description = data.get("project_description", "")
    create = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if not title:
        return jsonify(error="Nome do projeto é obrigatório"), 400

    new_project_id = get_next_project_id()

    new_project = {
        "project_id": new_project_id,
        "user_id": current_user_id,
        "project_title": title,
        "project_description": description,
        "created_at": create,
    }

    save_project(new_project)

    return jsonify({
        "sucess":'Projeto criado com sucesso!',
        "data": new_project
    }), 201

@projects_route.route("/")
@jwt_required()
def get_my_projects():
    """
    Listar todos os meus projetos
    ---
    tags:
      - Projects
    security:
      - Bearer: []
    responses:
      200:
        description: Lista de projetos retornada
    """
    current_user_id = get_jwt_identity()
    user = find_user_by_id(current_user_id)
    my_projects = find_projects_by_user_id(current_user_id)

    # Verifica se o usuário existe
    if not user:
        return jsonify({"msg": "Nenhum usuario logado"}), 401   

    # Verifica se o usuário possui projetos
    if not my_projects:
        return jsonify(error="Você não possui projetos criados."), 200

    my_projects = find_projects_by_user_id(current_user_id)

    if not my_projects:
        return jsonify(msg="Nenhum projeto criado"), 200
    
    return jsonify(my_projects), 200

@projects_route.route("/<project_id>")
@jwt_required()
def get_specific_project(project_id):
    """
    Obter um projeto específico
    ---
    tags:
      - Projects
    security:
      - Bearer: []
    parameters:
      - in: path
        name: project_id
        required: true
        type: string
    responses:
      200:
        description: Projeto retornado
      404:
        description: Não encontrado ou sem permissão
    """
    current_user_id = get_jwt_identity()
    user = find_user_by_id(current_user_id)
    # Verifica se o usuário existe
    if not user:
        return jsonify(error="Usuário não encontrado"), 404   
    project = find_project_by_id(project_id)
    # Verifica se o projeto existe
    if not project:
        return jsonify(error="Projeto não encontrado"), 404
    
    # Verifica se o usuário é o dono do projeto
    if current_user_id != project['user_id']:
        return jsonify(error="Acesso negado"), 404
    
    project.pop('user_id')
    project['owner_user'] = user['name']

    return jsonify({
        "sucess": "Projetos Localizados",
        "data": project
        }), 200

@projects_route.route("/<project_id>", methods=["PUT"])
@jwt_required()
def updated_project(project_id):
    """
    Atualizar um projeto
    ---
    tags:
      - Projects
    security:
      - Bearer: []
    parameters:
      - in: path
        name: project_id
        required: true
        type: string
      - in: body
        name: body
        schema:
          type: object
          properties:
            project_title:
              type: string
            project_description:
              type: string
    responses:
      200:
        description: Projeto atualizado
      400:
        description: Título obrigatório
      403:
        description: Sem permissão
      404:
        description: Projeto não encontrado
    """
    current_user_id = get_jwt_identity()
    user = find_user_by_id(current_user_id)
    if not user:
        return jsonify(error="Usuário não encontrado"), 404
    
    # Verifica se o projeto existe
    project = find_project_by_id(project_id)
    if not project:
        return jsonify(error="Projeto não encontrado"), 404
    
    # Verifica se o nome do projeto foi fornecido
    data = request.json
    old_title = project.get("project_title")
    new_title = data.get("project_title") or old_title
    new_description = project.get("project_description","")

    # Verifica se o usuário é o dono do projeto
    owner_user_id = project.get("user_id")
    if owner_user_id != current_user_id:
        return jsonify(error="Você não tem permissão para editar este projeto"), 403
    
    new_data_to_update = {
        "project_title": new_title,
        "project_description": data.get("project_description",new_description),
    }

    update_project_data(project_id, new_data_to_update)

    return jsonify({
      "success": "Projeto atualizado com sucesso!",
      "data": new_data_to_update  
    }), 200

@projects_route.route("/<project_id>", methods=["DELETE"])
@jwt_required()
def delete_project(project_id):
    """
    Deletar um projeto
    ---
    tags:
      - Projects
    security:
      - Bearer: []
    parameters:
      - in: path
        name: project_id
        required: true
        type: string
    responses:
      200:
        description: Projeto deletado
      403:
        description: Sem permissão
      404:
        description: Projeto não encontrado
    """

    current_user_id = get_jwt_identity()

    user = find_user_by_id(current_user_id)

    if not user:
        return jsonify(error=f"Usuário não encontrado"), 404

    project = find_project_by_id(project_id)

    if not project:
        return jsonify(error=f"Projeto não encontrado"), 404
    
    owner_user_id = project.get("user_id")
    if owner_user_id != current_user_id:
        return jsonify(error=f"Você não tem permissão para deletar este projeto"), 403

    delete_project_data(project_id)

    response = {
        "project_id": project_id,
        "project_title": project.get("project_title"),
        "lists": find_lists_by_project_id(project_id),
        "lists_name": [lista.get("list_name") for lista in find_lists_by_project_id(project_id)],
        "lists_count": len(find_lists_by_project_id(project_id))
    }

    return jsonify({
        "success":"Projeto deletado com sucesso!",
        "data":response
    }), 200


