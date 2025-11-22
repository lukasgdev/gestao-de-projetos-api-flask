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
            completed:
              type: boolean
    responses:
      201:
        description: Task criada com sucesso
      400:
        description: Erro nos dados enviados
      404:
        description: Projeto ou lista não encontrada
    """
    current_user_id = get_jwt_identity()
    data = request.get_json()

    if not data:
        return jsonify({"msg": "Nenhum dado enviado"}), 400

    #verifica se o projeto existe
    project = find_project_by_id(project_id)
    if not project:
        return jsonify({"msg": "Projeto não encontrado"}), 404

    #permissao de user
    if str(project["user_id"]) != str(current_user_id):
        return jsonify({"msg": "Você não tem permissão para criar tasks neste projeto"}), 403

    #verifica se a lista existe e pertence ao projeto
    lista = find_list_by_id(list_id)
    if not lista or str(lista["project_id"]) != str(project_id):
        return jsonify({"msg": "Lista não encontrada no projeto"}), 404

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
    return jsonify({"msg": "Task criada com sucesso!", "task": new_task}), 201



@tasks_route.get("/")
@jwt_required()
def list_tasks(project_id, list_id):
    """
    Listar todas as tasks de uma lista
    ---
    tags:
      - Tasks
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
        description: Lista de tasks retornada
      403:
        description: Sem permissão
      404:
        description: Lista não encontrada
    """
    current_user_id = get_jwt_identity()

    #verifica projeto
    project = find_project_by_id(project_id)
    if not project or str(project["user_id"]) != str(current_user_id):
        return jsonify({"error": "Projeto não encontrado ou não permitido"}), 403

    #verifica lista
    lista = find_list_by_id(list_id)
    if not lista or str(lista["project_id"]) != str(project_id):
        return jsonify({"error": "Lista não encontrada"}), 404

    tasks = find_tasks_by_list_id(list_id)

    return jsonify({"tasks": tasks}), 200


@tasks_route.put("/<task_id>")
@jwt_required()
def update_task(project_id, list_id, task_id):
    """
    Atualizar uma task
    ---
    tags:
      - Tasks
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
      400:
        description: Dados inválidos
      404:
        description: Task não encontrada
    """

    current_user_id = get_jwt_identity()
    data = request.get_json()

    task = find_task_by_id(task_id)
    if not task:
        return jsonify({"msg": "Task não encontrada"}), 404

    #testa pra ver se a task pertence a lista e ao projeto
    if str(task["list_id"]) != str(list_id):
        return jsonify({"msg": "Task não pertence à lista informada"}), 400

    lista = find_list_by_id(list_id)
    if not lista or str(lista["project_id"]) != str(project_id):
        return jsonify({"msg": "Lista inválida"}), 400

    project = find_project_by_id(project_id)
    if not project or str(project["user_id"]) != str(current_user_id):
        return jsonify({"msg": "Sem permissão"}), 403

    new_data = {
        "title": data.get("title", task["title"]),
        "description": data.get("description", task["description"]),
        "completed": data.get("completed", task["completed"]),
    }

    update_task_data(task_id, new_data)
    return jsonify({"msg": "Task atualizada com sucesso!"}), 200


@tasks_route.delete("/<task_id>")
@jwt_required()
def delete_task(project_id, list_id, task_id):
    """
    Deletar uma task
    ---
    tags:
      - Tasks
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
      404:
        description: Task não encontrada
    """
    current_user_id = get_jwt_identity()

    task = find_task_by_id(task_id)
    if not task:
        return jsonify({"msg": "Task não encontrada"}), 404

    if str(task["list_id"]) != str(list_id):
        return jsonify({"msg": "Task não pertence à lista informada"}), 400

    lista = find_list_by_id(list_id)
    if not lista or str(lista["project_id"]) != str(project_id):
        return jsonify({"msg": "Lista inválida"}), 400

    project = find_project_by_id(project_id)
    if not project or str(project["user_id"]) != str(current_user_id):
        return jsonify({"msg": "Sem permissão"}), 403

    delete_task_data(task_id)
    return jsonify({"msg": "Task deletada com sucesso!"}), 200
