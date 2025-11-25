from flask import Blueprint, request, jsonify
from datetime import datetime
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.csv_service import (
    save_list, get_next_list_id, find_project_by_id, 
    find_lists_by_project_id, find_list_by_id, delete_list_data, update_list_data, find_user_by_id
)

list_route = Blueprint('lists', __name__)

# CRIAR UMA NOVA LISTA (COLUNA) PARA UM PROJETO

# Ex: Criar a coluna "Aguardando Aprovação" no Projeto 1

@list_route.route('/', methods=['POST'])
@jwt_required()
def create_list(project_id):
    """
    Criar uma nova lista em um projeto
    ---
    tags:
      - Lists
    operationId: "create_list"
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
            list_name:
              type: string
    responses:
      201:
        description: Lista criada
        examples:
          application/json:
            message: "Lista criada com sucesso!"
            data:
              list_id: "<id>"
              project_id: "<project_id>"
              list_name: "<nome>"
              created_at: "2025-11-23 12:00:00"
        401:
          description: Usuário não encontrado (token inválido/usuário removido)
          examples:
            application/json:
              error: "Usuário não encontrado. Por favor, efetuar o login novamente"
      400:
        description: Nome obrigatório
        examples:
          application/json:
            error: "O nome da lista é obrigatório"
      403:
        description: Sem permissão
        examples:
          application/json:
            error: "Você não tem permissão para ver as listas deste projeto"
      404:
        description: Projeto não encontrado
        examples:
          application/json:
            error: "Projeto não encontrado"
    """
    data = request.json
    list_name = data.get('list_name')
    current_user_id = get_jwt_identity()
    user = find_user_by_id(current_user_id)

    # Verifica se o usuário existe
    if not user:
      return jsonify({"error": "Usuário não encontrado. Por favor, efetuar o login novamente"}), 401
    
    #Verifica se o projeto existe
    project = find_project_by_id(project_id)
    if not project:
      return jsonify({"error": "Projeto não encontrado"}), 404
    
    # Verifica se o usuário é o dono do projeto
    if current_user_id  != project.get('user_id'):
      return jsonify({"error": "Você não tem permissão para ver as listas deste projeto"}), 403
      
    # Verifica se o nome da lista foi fornecido
    if not list_name:
      return jsonify({"error": "O nome da lista é obrigatório"}), 400
    
    #Cria a lista
    new_list = {
        "list_id": get_next_list_id(),
        "project_id": project_id,
        "list_name": list_name,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    save_list(new_list)

    return jsonify({
      "message":"Lista criada com sucesso!",
      "data":new_list
    }), 201


# VER TODAS AS LISTAS DE UM PROJETO

@list_route.route('/', methods=['GET'])
@jwt_required()
def get_project_lists(project_id):
    """
    Listar todas as listas de um projeto
    ---
    tags:
      - Lists
    operationId: "get_project_lists"
    security:
      - Bearer: []
    parameters:
      - in: path
        name: project_id
        required: true
        type: string
    responses:
      200:
        description: Listas retornadas
        401:
          description: Usuário não encontrado (token inválido/usuário removido)
          examples:
            application/json:
              error: "Usuário não encontrado. Por favor, efetuar o login novamente"
      404:
        description: Projeto não encontrado
        examples:
          application/json:
            error: "Projeto não encontrado"
    """

    project = find_project_by_id(project_id)
    my_lists = find_lists_by_project_id(project_id)
    current_user_id = get_jwt_identity()
    user = find_user_by_id(current_user_id)

    # Verifica se o usuário existe
    if not user:
      return jsonify({"error": "Usuário não encontrado. Por favor, efetuar o login novamente"}), 401

    # Verifica se o projeto existe
    if not project:
      return jsonify({"error": "Projeto não encontrado"}), 404
    
    # Verifica se o usuário é o dono do projeto
    if current_user_id  != project.get('user_id'):
      return jsonify({"error": "Você não tem permissão para ver as listas deste projeto"}), 403

    # Verifica se o projeto possui listas
    if not my_lists:
      return jsonify({"message": "Nenhuma lista encontrada para este projeto."}), 200
    
    response = {
        "project_info": {
            "project_id": project_id,
            "project_title": project.get('project_title'),
            "project_description": project.get('project_description'),
          },
        "lists": my_lists,
    }
    
    return jsonify({
      "message":"Listas recuperadas com sucesso",
      "data": response
    }), 200

@list_route.route('/<list_id>')
@jwt_required()
def get_specific_list(project_id, list_id):
    """
    Obter uma lista específica de um projeto
    ---
    tags:
      - Lists
    operationId: "get_specific_list"
    security:
      - Bearer: []
    parameters:
      - in: path
        name: project_id
        required: true
        type: string
      - in: path
        name: list_id
        required: true
        type: string
    responses:
      200:
        description: Lista retornada
        examples:
          application/json:
            message: "Lista recuperada com sucesso"
            data:
              project_info:
                project_id: "<project_id>"
                project_title: "<titulo>"
                project_description: "<descricao>"
              list:
                list_id: "<list_id>"
                project_id: "<project_id>"
                list_name: "<nome>"
        401:
          description: Usuário não encontrado (token inválido/usuário removido)
          examples:
            application/json:
              error: "Usuário não encontrado. Por favor, efetuar o login novamente"
      400:
        description: Lista não pertence ao projeto
        examples:
          application/json:
            error: "Esta lista não pertence ao projeto informado"
      403:
        description: Sem permissão
        examples:
          application/json:
            error: "Você não tem permissão para visualizar esta lista"
      404:
        description: Lista ou projeto não encontrado
        examples:
          application/json:
            error: "Lista não encontrada"
    """

    specific_list = find_list_by_id(list_id)
    project = find_project_by_id(project_id)
    current_user_id = get_jwt_identity()
    user = find_user_by_id(current_user_id)
    
    # Verifica se o usuário existe
    if not user:
      return jsonify({"error": "Usuário não encontrado. Por favor, efetuar o login novamente"}), 401
    
    #Verifica se o projeto existe
    if not project:
      return jsonify({"error": "Projeto não encontrado"}), 404
    
    #Verifica se a lista existe
    if not specific_list:
      return jsonify({"error": "Lista não encontrada"}), 404

    # Verifica se essa lista pertence mesmo ao projeto informado na URL
    if specific_list.get('project_id') != str(project_id):
      return jsonify({"error": "Esta lista não pertence ao projeto informado"}), 400
    
    # Verifica se o usuário é o dono do projeto
    if project.get('user_id') != current_user_id:
      return jsonify({"error": "Você não tem permissão para visualizar esta lista"}), 403

    response = {
      "project_info": {
          "project_id": project_id,
          "project_title": project.get('project_title'),
          "project_description": project.get('project_description'),
      },
      "list": specific_list,
    }

    return jsonify({
      "message":"Lista recuperada com sucesso",
      "data": response
    }), 200


# DELETAR UMA LISTA DE UM PROJETO
@list_route.route('/<list_id>', methods=['DELETE'])
@jwt_required()
def delete_project_list(project_id, list_id):
    """
    Deletar uma lista de um projeto
    ---
    tags:
      - Lists
    operationId: "delete_project_list"
    security:
      - Bearer: []
    parameters:
      - in: path
        name: project_id
        required: true
        type: string
      - in: path
        name: list_id
        required: true
        type: string
    responses:
      200:
        description: Lista deletada
        examples:
          application/json:
            message: "Lista deletada com sucesso"
            data:
              list_id: "<list_id>"
              project_id: "<project_id>"
              list_name: "<nome>"
        401:
          description: Usuário não encontrado (token inválido/usuário removido)
          examples:
            application/json:
              error: "Usuário não encontrado. Por favor, efetuar o login novamente"
      400:
        description: Lista não pertence ao projeto
        examples:
          application/json:
            error: "Esta lista não pertence ao projeto informado"
      403:
        description: Sem permissão
        examples:
          application/json:
            error: "Você não tem permissão para deletar listas deste projeto"
      404:
        description: Lista ou projeto não encontrado
        examples:
          application/json:
            error: "Lista não encontrada"
    """
    current_user_id = get_jwt_identity()
    user = find_user_by_id(current_user_id)
    
    # Verifica se o usuário existe
    if not user:
      return jsonify({"error": "Usuário não encontrado. Por favor, efetuar o login novamente"}), 401

    # Verifica se a lista existe
    lista = find_list_by_id(list_id)
    if not lista:
      return jsonify({"error": "Lista não encontrada"}), 404

    # Verifica se essa lista pertence mesmo ao projeto informado na URL
    if lista.get('project_id') != str(project_id):
      return jsonify({"error": "Esta lista não pertence ao projeto informado"}), 400

    # verifica se o Projeto existe
    project = find_project_by_id(project_id)
    if not project:
      return jsonify({"error": "Projeto não encontrado"}), 404
    
    # verifica a Permissão do Dono
    owner_user_id = project.get('user_id')
    if owner_user_id != current_user_id:
      return jsonify({"error": "Você não tem permissão para deletar listas deste projeto"}), 403

    # Deleta a lista
    delete_list_data(list_id)

    response ={
        "list_id": list_id,
        "project_id": project_id,
        "list_name": lista.get('list_name')
    }

    return jsonify({
      "message":"Lista deletada com sucesso",
      "data":response
    }), 200

@list_route.route('/<list_id>', methods=['PATCH'])
@jwt_required()
def update_list(project_id, list_id):
    """
    Atualizar o nome de uma lista
    ---
    tags:
      - Lists
    operationId: "update_list"
    security:
      - Bearer: []
    parameters:
      - in: path
        name: project_id
        required: true
        type: string
      - in: path
        name: list_id
        required: true
        type: string
      - in: body
        name: body
        schema:
          type: object
          properties:
            list_name:
              type: string
    responses:
      200:
        description: Lista atualizada
        examples:
          application/json:
            message: "Lista renomeada para '<novo_nome>' com sucesso!"
        401:
          description: Usuário não encontrado (token inválido/usuário removido)
          examples:
            application/json:
              error: "Usuário não encontrado. Por favor, efetuar o login novamente"
      400:
        description: Nome obrigatório ou lista inválida
        examples:
          application/json:
            error: "O novo nome da lista é obrigatório"
      403:
        description: Sem permissão
        examples:
          application/json:
            error: "Você não tem permissão para editar listas deste projeto"
      404:
        description: Lista ou projeto não encontrado
        examples:
          application/json:
            error: "Lista não encontrada"
    """
    # Pega o novo nome
    data = request.json
    new_name = data.get('list_name')
    current_user_id = get_jwt_identity()
    user = find_user_by_id(current_user_id)
    lista = find_list_by_id(list_id)

    # Verifica se o usuário existe
    if not user:
      return jsonify({"error": "Usuário não encontrado. Por favor, efetuar o login novamente"}), 401

    # verifica o Projeto 
    project = find_project_by_id(project_id)
    if not project:
      return jsonify({"error": "Projeto não encontrado"}), 404

    # Verifica se a lista existe
    if not lista:
      return jsonify({"error": "Lista não encontrada"}), 404
    
    # Verifica se essa lista pertence mesmo ao projeto informado na URL
    if lista.get('project_id') != str(project_id):
      return jsonify({"error": "Esta lista não pertence ao projeto informado"}), 400
    
     # Verifica se o novo nome foi fornecido
    if not new_name:
      return jsonify({"error": "O novo nome da lista é obrigatório"}), 400
    
    # verifica a Permissão do Dono
    owner_user_id = project.get('user_id')
    if owner_user_id != current_user_id:
      return jsonify({"error": "Você não tem permissão para editar listas deste projeto"}), 403

    # Atualiza
    update_list_data(list_id, {'list_name': new_name})
    return jsonify({"message": f"Lista renomeada para '{new_name}' com sucesso!"}), 200
