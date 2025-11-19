from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.csv_service import (
    read_csv,
    save_task,
    get_next_task_id,
    find_task_by_id,
    update_task_data,
    delete_task_data,
    find_tasks_by_project,
    find_project_by_id,
)
from services.csv_service import TASKS
from services.csv_service import find_user_by_id

tasks_route = Blueprint('tasks', __name__)


# -----------------------------
# CREATE TASK
# -----------------------------
@tasks_route.route("/tasks", methods=["POST"])
@jwt_required()
def create_task():
    current_user_id = get_jwt_identity()

    data = request.get_json()
    if not data:
        return jsonify({"msg": "Nenhum dado enviado"}), 400

    project_id = data.get("project_id")
    if not project_id:
        return jsonify({"msg": "project_id é obrigatório"}), 400

    # Verifica se o projeto existe
    project = find_project_by_id(project_id)
    if not project:
        return jsonify({"msg": "Projeto não encontrado"}), 404

    # Verifica se o projeto pertence ao usuário logado
    if str(project["user_id"]) != str(current_user_id):
        return jsonify({"msg": "Você não tem permissão para criar tasks nesse projeto"}), 403

    new_task_id = get_next_task_id()

    new_task = {
        "task_id": str(new_task_id),
        "title": data.get("title", ""),
        "description": data.get("description", ""),
        "status": data.get("status", "todo"),
        "project_id": str(project_id),
        "user_id": str(current_user_id)
    }

    save_task(new_task)

    return jsonify({"msg": "Task criada com sucesso!", "task": new_task}), 201



# -----------------------------
# LIST ALL TASKS OF THE USER
# -----------------------------
@tasks_route.route("/tasks", methods=["GET"])
@jwt_required()
def list_all_tasks():
    current_user_id = get_jwt_identity()

    tasks = read_csv(TASKS)

    user_tasks = [t for t in tasks if str(t.get("user_id")) == str(current_user_id)]

    if not user_tasks:
        return jsonify({"msg": "Nenhuma task encontrada"}), 404

    return jsonify({"tasks": user_tasks}), 200



# -----------------------------
# LIST TASKS OF A SPECIFIC PROJECT
# -----------------------------
@tasks_route.route("/tasks/by_project/<project_id>", methods=["GET"])
@jwt_required()
def list_tasks_by_project(project_id):
    current_user_id = get_jwt_identity()

    project = find_project_by_id(project_id)
    if not project:
        return jsonify({"msg": "Projeto não encontrado"}), 404

    if str(project["user_id"]) != str(current_user_id):
        return jsonify({"msg": "Acesso negado"}), 403

    tasks = find_tasks_by_project(project_id)

    # Filtrar tasks do usuário
    tasks = [t for t in tasks if str(t["user_id"]) == str(current_user_id)]

    return jsonify({"tasks": tasks}), 200



# -----------------------------
# UPDATE TASK
# -----------------------------
@tasks_route.route("/tasks/<task_id>", methods=["PUT"])
@jwt_required()
def update_task(task_id):
    current_user_id = get_jwt_identity()
    data = request.json

    task = find_task_by_id(task_id)
    if not task:
        return jsonify({"msg": "Task não encontrada"}), 404

    if str(task["user_id"]) != str(current_user_id):
        return jsonify({"msg": "Você não tem permissão para editar esta task"}), 403

    new_data = {
        "title": data.get("title", task["title"]),
        "description": data.get("description", task["description"]),
        "status": data.get("status", task["status"]),
    }

    update_task_data(task_id, new_data)

    return jsonify({"msg": "Task atualizada com sucesso!"}), 200



# -----------------------------
# DELETE TASK
# -----------------------------
@tasks_route.route("/tasks/<task_id>", methods=["DELETE"])
@jwt_required()
def delete_task(task_id):
    current_user_id = get_jwt_identity()

    task = find_task_by_id(task_id)
    if not task:
        return jsonify({"msg": "Task não encontrada"}), 404

    if str(task["user_id"]) != str(current_user_id):
        return jsonify({"msg": "Você não tem permissão para deletar esta task"}), 403

    delete_task_data(task_id)

    return jsonify({"msg": "Task deletada com sucesso!"}), 200
