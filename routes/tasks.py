from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

from services.csv_service import (
    save_task,
    get_next_task_id,
    find_task_by_id,
    update_task_data,
    delete_task_data,
    find_tasks_by_list_id,
    find_project_by_id,
    find_list_by_id,
    find_user_by_id
)


tasks_route = Blueprint("tasks", __name__)


@tasks_route.route("/", methods=["POST"])
@jwt_required()
def create_task(project_id, list_id):
    """
    Criar uma nova task
    ---
    tags:
      - Tasks
    operationId: "create_task"
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
            title:
              type: string
            description:
              type: string
    responses:
      201:
        description: Task criada com sucesso
        examples:
          application/json:
            message: "Task criada com sucesso!"
            task:
              task_id: "<id>"
              title: "<titulo>"
              description: "<descricao>"
              completed: false
              created_at: "2025-11-23 12:00:00"
      400:
        description: Erro nos dados enviados
        examples:
          application/json:
            error: "Nenhum dado enviado"
      404:
        description: Projeto ou lista não encontrada
        examples:
          application/json:
            error: "Projeto não encontrado"
    """
    current_user_id = get_jwt_identity()
    data = request.get_json()
    title = data.get('title')

    if not data:
      return jsonify({"error": "Nenhum dado enviado"}), 400

    #verifica se o projeto existe
    project = find_project_by_id(project_id)
    if not project:
      return jsonify({"error": "Projeto não encontrado"}), 404

    #permissao de user
    if str(project["user_id"]) != str(current_user_id):
        return jsonify({"error": "Você não tem permissão para criar tasks neste projeto"}), 403

    #verifica se a lista existe e pertence ao projeto
    lista = find_list_by_id(list_id)
    if not lista or str(lista["project_id"]) != str(project_id):
      return jsonify({"error": "Lista não encontrada no projeto"}), 404

    if not title:
      return jsonify({"error": "O nome da task é obrigatório"}), 400

    new_task_id = get_next_task_id()

    new_task = {
        "task_id": str(new_task_id),
        "title": data.get("title", ""),
        "description": data.get("description", ""),
        "completed": False,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
        "list_id": str(list_id),
    }

    save_task(new_task)
    return jsonify({"message": "Task criada com sucesso!", "data": new_task}), 201



@tasks_route.route("/", methods=["GET"])
@jwt_required()
def list_tasks(project_id, list_id):
    """
    Listar todas as tasks de uma lista
    ---
    tags:
      - Tasks
    operationId: "list_tasks"
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
      - in: query
        name: completed
        required: false
        type: string
        enum: ["true", "false"]
        description: Filtrar tasks por status. Use "true" para concluídas e "false" para não concluídas.

    responses:
      200:
        description: Lista de tasks retornada
        examples:
          application/json:
            message: "Tasks recuperadas com sucesso"
            data:
              list_info:
                list_id: "<list_id>"
                list_name: "<nome>"
              tasks:
                - task_id: "1"
                  title: "Task A"
                  description: ""
                  completed: false
                - task_id: "2"
                  title: "Task B"
                  description: "Descrição"
                  completed: true
      403:
        description: Sem permissão
        examples:
          application/json:
            error: "Você não tem permissão para ver as tasks deste projeto"
      404:
        description: Lista não encontrada
        examples:
          application/json:
            error: "Lista não encontrada"
    """
    current_user_id = get_jwt_identity()

    #verifica projeto
    project = find_project_by_id(project_id)
    if not project:
      return jsonify({"error": "Projeto não encontrado"}), 404
    if str(project["user_id"]) != str(current_user_id):
      return jsonify({"error": "Você não tem permissão para ver as tasks deste projeto"}), 403

    #verifica lista
    lista = find_list_by_id(list_id)
    if not lista or str(lista["project_id"]) != str(project_id):
        return jsonify({"error": "Lista não encontrada"}), 404

    tasks = find_tasks_by_list_id(list_id)

    completed_param = request.args.get("completed")

    if completed_param is not None:
        completed_param = completed_param.lower()

        if completed_param not in ["true", "false"]:
            return jsonify({"error": "Valor inválido para completed. Use true ou false."}), 400

        completed_bool = (completed_param == "true")

        def normalize(value):
            if isinstance(value, bool):
                return value
            if isinstance(value, str):
                return value.lower() == "true"
            return False

        tasks = [t for t in tasks if normalize(t.get("completed")) == completed_bool]
    
    #print(tasks)

    if not tasks:
      return jsonify({"message": "Nenhuma task encontrada para esta lista."}), 200

    response = {
      "list_info": {
        "list_id": list_id,
        "list_name": lista.get('list_name'),
      },
      "tasks": tasks,
    }

    return jsonify({
      "message": "Tasks recuperadas com sucesso",
      "data": response
    }), 200

@tasks_route.route('/<task_id>', methods=["GET"])
@jwt_required()
def get_specific_task(project_id, list_id, task_id):
    """
    Obter uma task específica de uma lista
    ---
    tags:
      - Tasks
    operationId: "get_specific_task"
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
      - in: path
        name: task_id
        required: true
        type: string
    responses:
      200:
        description: Task retornada
        examples:
          application/json:
            message: "Task recuperada com sucesso"
            data:
              project_info:
                project_id: "<project_id>"
                project_title: "<titulo>"
              list_info:
                list_id: "<list_id>"
                list_name: "<nome>"
              task:
                task_id: "<task_id>"
                title: "<titulo>"
                description: "<descricao>"
                completed: false
      401:
        description: Usuário não encontrado (token inválido/usuário removido)
        examples:
          application/json:
            error: "Usuário não encontrado. Por favor, efetuar o login novamente"
      400:
        description: Task não pertence à lista
        examples:
          application/json:
            error: "Esta task não pertence à lista informada"
      403:
        description: Sem permissão
        examples:
          application/json:
            error: "Você não tem permissão para visualizar esta task"
      404:
        description: Task, lista ou projeto não encontrado
        examples:
          application/json:
            error: "Task não encontrada"
    """

    current_user_id = get_jwt_identity()

    # Verifica usuário
    user = find_user_by_id(current_user_id)
    if not user:
        return jsonify({"error": "Usuário não encontrado. Por favor, efetue o login novamente"}), 401

    # Verifica projeto
    project = find_project_by_id(project_id)
    if not project:
        return jsonify({"error": "Projeto não encontrado"}), 404

    # Verifica lista
    lista = find_list_by_id(list_id)
    if not lista:
        return jsonify({"error": "Lista não encontrada"}), 404

    # Verifica task
    task = find_task_by_id(task_id)
    if not task:
        return jsonify({"error": "Task não encontrada"}), 404

    # Verifica se a lista pertence ao projeto
    if lista.get('project_id') != str(project_id):
        return jsonify({"error": "Esta lista não pertence ao projeto informado"}), 400

    # Verifica se a task pertence à lista
    if task.get('list_id') != str(list_id):
        return jsonify({"error": "Esta task não pertence à lista informada"}), 400

    # Verifica se o usuário é o dono do projeto
    if project.get('user_id') != current_user_id:
        return jsonify({"error": "Você não tem permissão para visualizar esta task"}), 403

    response = {
        #"project_info": {
        #    "project_id": project_id,
        #    "project_title": project.get('project_title'),
        #    "project_description": project.get('project_description'),
        #},
        "list_info": {
            "list_id": list_id,
            "list_name": lista.get('list_name'),
        },
        "task": task,
    }

    return jsonify({
        "message": "Task recuperada com sucesso",
        "data": response
    }), 200


@tasks_route.route("/<task_id>", methods=["PUT"])
@jwt_required()
def update_task(project_id, list_id, task_id):
    """
    Atualizar uma task
    ---
    tags:
      - Tasks
    operationId: "update_task"
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
      - in: path
        name: task_id
        required: true
        type: string
      - in: body
        name: body
        schema:
          type: object
          properties:
            title:
              type: string
            description:
              type: string
            completed:
              type: boolean
    responses:
      200:
        description: Task atualizada
        examples:
          application/json:
            message: "Task atualizada com sucesso!"
      400:
        description: Dados inválidos
        examples:
          application/json:
            error: "Dados inválidos"
      404:
        description: Task não encontrada
        examples:
          application/json:
            error: "Task não encontrada"
    """

    current_user_id = get_jwt_identity()
    data = request.get_json()
    title = data.get('title')

    task = find_task_by_id(task_id)
    if not task:
      return jsonify({"error": "Task não encontrada"}), 404

    #testa pra ver se a task pertence a lista e ao projeto
    if str(task["list_id"]) != str(list_id):
      return jsonify({"error": "Task não pertence à lista informada"}), 400

    lista = find_list_by_id(list_id)
    if not lista or str(lista["project_id"]) != str(project_id):
      return jsonify({"error": "Lista inválida"}), 400

    project = find_project_by_id(project_id)
    if not project:
      return jsonify({"error": "Projeto não encontrado"}), 404
    if str(project["user_id"]) != str(current_user_id):
      return jsonify({"error": "Você não tem permissão para acessar esta task"}), 403

    if not title:
      return jsonify({"error": "O novo nome da task é obrigatório"}), 400

    new_data = {
        "title": data.get("title", task["title"]),
        "description": data.get("description", task["description"]),
        "completed": data.get("completed", task["completed"]),
    }

    update_task_data(task_id, new_data)
    return jsonify({"message": "Task atualizada com sucesso!"}), 200


@tasks_route.route("/<task_id>", methods=["DELETE"])
@jwt_required()
def delete_task(project_id, list_id, task_id):
    """
    Deletar uma task
    ---
    tags:
      - Tasks
    operationId: "delete_task"
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
      - in: path
        name: task_id
        required: true
        type: string
    responses:
      200:
        description: Task deletada
        examples:
          application/json:
            message: "Task deletada com sucesso!"
      404:
        description: Task não encontrada
        examples:
          application/json:
            error: "Task não encontrada"
    """
    current_user_id = get_jwt_identity()

    task = find_task_by_id(task_id)
    if not task:
      return jsonify({"error": "Task não encontrada"}), 404

    if str(task["list_id"]) != str(list_id):
      return jsonify({"error": "Task não pertence à lista informada"}), 400

    lista = find_list_by_id(list_id)
    if not lista or str(lista["project_id"]) != str(project_id):
      return jsonify({"error": "Lista inválida"}), 400

    project = find_project_by_id(project_id)
    if not project:
      return jsonify({"error": "Projeto não encontrado"}), 404
    if str(project["user_id"]) != str(current_user_id):
      return jsonify({"error": "Você não tem permissão para acessar esta task"}), 403

    delete_task_data(task_id)
    return jsonify({"message": "Task deletada com sucesso!"}), 200
