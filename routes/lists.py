from flask import Blueprint, request, jsonify
from datetime import datetime
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.csv_service import (
    save_list, get_next_list_id, find_project_by_id, 
    find_lists_by_project_id
)

list_route = Blueprint('lists', __name__)


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

@list_route.route('/<project_id>/lists', methods=['GET'])
@jwt_required()
def get_project_lists(project_id):
    # (Opcional) Você pode adicionar verificação de dono aqui também se quiser privacidade total
    
    my_lists = find_lists_by_project_id(project_id)
    return jsonify(my_lists), 200