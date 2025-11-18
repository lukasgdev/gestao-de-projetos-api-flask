# routes/tasks.py
from flask import Blueprint, request, jsonify
from services.csv_service import (
    get_next_task_id,
    find_task_by_id,
    find_tasks_by_project,
    save_task,
    update_task,
    delete_task
)

tasks_route = Blueprint("tasks", __name__)



# CREATE TASK

@tasks_route.route("/tasks", methods=["POST"])
def create_task():
    data = request.get_json()


    new_id = get_next_task_id()

    task = {
        "task_id": str(new_id),
        "title": data["title"],
        "description": data.get("description", ""),
        "status": data.get("status", "todo"),
        "project_id": str(data["project_id"])
    }

    save_task(task)
    return jsonify({"message": "Task criada com sucesso", "task": task}), 201



# LIST TASKS

@tasks_route.route("/tasks", methods=["GET"])
def list_tasks_especificas():
    project_id = request.args.get("project_id")

    if not project_id:
        return jsonify({"error": "Informe project_id: /tasks?project_id=x"}), 400

    tasks = find_tasks_by_project(project_id)
    return jsonify({"tasks": tasks}), 200



# UPDATE TASK

@tasks_route.route("/tasks/<int:task_id>", methods=["PUT", "PATCH"])
def update(task_id):
    data = request.get_json()

    if not data:
        return jsonify({"error": "Nenhum dado enviado"}), 400

    old_task = find_task_by_id(task_id)
    if not old_task:
        return jsonify({"error": "Task não encontrada"}), 404

    new_data = {
        "title": data.get("title", old_task["title"]),
        "description": data.get("description", old_task["description"]),
        "status": data.get("status", old_task["status"])
    }

    update_task(task_id, new_data)

    return jsonify({"message": "Task atualizada com sucesso"}), 200



# DELETE TASK

@tasks_route.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete(task_id):
    task = find_task_by_id(task_id)

    if not task:
        return jsonify({"error": "Task não encontrada"}), 404

    delete_task(task_id)

    return jsonify({"message": "Task deletada com sucesso"}), 200
