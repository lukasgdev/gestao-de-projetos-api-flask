from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.csv_service import find_project_by_id, find_user_by_id, get_next_project_id, save_project, find_projects_by_user_id, find_project_by_id, update_project_data, delete_project_data
from datetime import datetime

projects_route = Blueprint('projects', __name__)

@projects_route.route('/projects', methods=['POST'])
@jwt_required()
def create_project():
    current_user_id = get_jwt_identity()

    user = find_user_by_id(current_user_id)

    if not user:
        return jsonify({"msg": "Usuário não encontrado"}), 404
    
    data = request.json
    title = data.get("project_title")
    description = data.get("project_description", "")
    create = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if not title:
        return jsonify(msg="Nome do projeto é obrigatório"), 400

    new_project_id = get_next_project_id()

    new_project = {
        "project_id": new_project_id,
        "user_id": current_user_id,
        "project_title": title,
        "project_description": description,
        "created_on": create,
    }

    save_project(new_project)

    return jsonify(msg='Projeto criado com sucesso!'), 201

@projects_route.route("/projects")
@jwt_required()
def get_my_projects():
    current_user_id = get_jwt_identity()

    user = find_user_by_id(current_user_id)

    if not user:
        return jsonify({"msg": "Usuário não encontrado"}), 404    

    my_projects = find_projects_by_user_id(current_user_id)
    return jsonify(my_projects), 200

@projects_route.route("/projects/<project_id>")
@jwt_required()
def get_specific_project(project_id):
    current_user_id = get_jwt_identity()

    user = find_user_by_id(current_user_id)

    if not user:
        return jsonify({"msg": "Usuário não encontrado"}), 404   

    project = find_project_by_id(project_id)

    if not project:
        return jsonify(msg="Projeto não encontrado"), 404
    
    if current_user_id != project['user_id']:
        return jsonify(msg="Acesso negado"), 404
    
    project.pop('user_id')
    project['owner_user'] = user['name']

    return jsonify(project)

@projects_route.route("/projects/<project_id>", methods=["PUT"])
@jwt_required()
def updated_project(project_id):

    current_user_id = get_jwt_identity()

    user = find_user_by_id(current_user_id)

    if not user:
        return jsonify({"msg": "Usuário não encontrado"}), 404

    data = request.json
    new_title = data.get("project_title")

    if not new_title:
        return jsonify(msg="Nome do projeto é obrigatório"), 400

    project = find_project_by_id(project_id)

    if not project:
        return jsonify(msg="Projeto não encontrado"), 404

    owner_user_id = project.get("user_id")
    if owner_user_id != current_user_id:
        return jsonify(msg="Você não tem permissão para editar este projeto"), 403

    new_data_to_update = {
        "project_title": new_title,
        "project_description": data.get("project_description", ""),
    }

    update_project_data(project_id, new_data_to_update)

    return jsonify(msg="Projeto atualizado com sucesso!"), 200

@projects_route.route("/projects/<project_id>", methods=["DELETE"])
@jwt_required()
def delete_project(project_id):

    current_user_id = get_jwt_identity()

    user = find_user_by_id(current_user_id)

    if not user:
        return jsonify({"msg": "Usuário não encontrado"}), 404

    project = find_project_by_id(project_id)

    if not project:
        return jsonify(msg="Projeto não encontrado"), 404
    
    owner_user_id = project.get("user_id")
    if owner_user_id != current_user_id:
        return jsonify(msg="Você não tem permissão para deletar este projeto"), 403

    delete_project_data(project_id)

    return jsonify(msg="Projeto deletado com sucesso!"), 200

