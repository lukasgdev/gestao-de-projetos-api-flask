from flask import Blueprint, request, jsonify
from datetime import datetime
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.csv_service import (
    save_list, get_next_list_id, find_project_by_id, 
    find_lists_by_project_id, find_list_by_id, delete_list_data, update_list_data
)

list_route = Blueprint('/lists', __name__)

# CRIAR UMA NOVA LISTA (COLUNA) PARA UM PROJETO

# Ex: Criar a coluna "Aguardando Aprovação" no Projeto 1

@list_route.route('/<project_id>/lists', methods=['POST'])
@jwt_required()
def create_list_for_project(project_id):
    data = request.json
    list_name = data.get('list_name')
    
    if not list_name:
        return jsonify(msg="O nome da lista é obrigatório"), 400

    #Verifica se o projeto existe
    project = find_project_by_id(project_id)
    
    if not project:
        return jsonify(msg="Projeto não encontrado"), 404

    # Verifica se o usuário é o dono do projeto
    current_user_id = get_jwt_identity()
    if project.get('user_id') != current_user_id:
        return jsonify(msg="Você não tem permissão para adicionar listas a este projeto"), 403

    #Cria a lista
    new_list = {
        "list_id": get_next_list_id(),
        "project_id": project_id,
        "list_name": list_name,
        "created_on": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    save_list(new_list)

    return jsonify(msg=f"Lista '{list_name}' criada com sucesso!"), 201


# VER TODAS AS LISTAS DE UM PROJETO

@list_route.route('/<project_id>/lists')
@jwt_required()
def get_project_lists(project_id):

    project = find_project_by_id(project_id)

    if not project:
        return jsonify(msg="Projeto não encontrado"), 404
    
    #Verifica se o projeto existe
    my_lists = find_lists_by_project_id(project_id)

    if not my_lists:
        return jsonify(msg="Nenhuma lista encontrada para este projeto."), 200

    response = {
        "project_id": project_id,
        "project_title": project.get("project_title"),
        "lists": my_lists,
    }
    
    return jsonify(response), 200

# DELETAR UMA LISTA DE UM PROJETO
@list_route.route('/<project_id>/lists/<list_id>', methods=['DELETE'])
@jwt_required()

def delete_project_list(project_id, list_id):
    current_user_id = get_jwt_identity()

    # Verifica se a lista existe
    lista = find_list_by_id(list_id)
    if not lista:
        return jsonify(msg="Lista não encontrada"), 404

    # Verifica se essa lista pertence mesmo ao projeto informado na URL

    if lista.get('project_id') != str(project_id):
        return jsonify(msg="Esta lista não pertence ao projeto informado"), 400

    # Verifica o Projeto e a Permissão do Dono
    project = find_project_by_id(project_id)
    if not project:
        return jsonify(msg="Projeto não encontrado"), 404

    owner_user_id = project.get('user_id')
    if owner_user_id != current_user_id:
        return jsonify(msg="Você não tem permissão para deletar listas deste projeto"), 403

    # Deleta a lista
    delete_list_data(list_id)

    return jsonify(msg="Lista deletada com sucesso!"), 200

@list_route.route('/<project_id>/lists/<list_id>', methods=['PATCH'])
@jwt_required()
def update_list(project_id, list_id):
    current_user_id = get_jwt_identity()
    
    # Pega o novo nome
    data = request.json
    new_name = data.get('list_name')

    if not new_name:
        return jsonify(msg="O novo nome da lista é obrigatório"), 400

    # Verifica se a lista existe
    lista = find_list_by_id(list_id)
    if not lista:
        return jsonify(msg="Lista não encontrada"), 404

    # Verifica se essa lista pertence mesmo ao projeto informado na URL
    if lista.get('project_id') != str(project_id):
        return jsonify(msg="Esta lista não pertence ao projeto informado"), 400

    # verifica o Projeto 
    project = find_project_by_id(project_id)
    if not project:
        return jsonify(msg="Projeto não encontrado"), 404
    
    # verifica a Permissão do Dono
    owner_user_id = project.get('user_id')
    if owner_user_id != current_user_id:
        return jsonify(msg="Você não tem permissão para editar listas deste projeto"), 403

    # Atualiza
    update_list_data(list_id, {'list_name': new_name})
    return jsonify(msg=f"Lista renomeada para '{new_name}' com sucesso!"), 200