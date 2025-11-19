from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

from services.csv_service import (
    read_csv,
    find_project_by_id,
    find_list_by_id,
    find_task_by_id,
    find_comments_by_task_id,
    get_next_comment_id,
    save_comment,
    update_comment_data,
    delete_comment_data
)

comments_route = Blueprint("comments", __name__)


# ============================================================
# CREATE COMMENT
# ============================================================
@comments_route.post("/projects/<project_id>/lists/<list_id>/tasks/<task_id>/comments")
@jwt_required()
def create_comment(project_id, list_id, task_id):

    current_user_id = get_jwt_identity()
    data = request.get_json()

    if not data or "content" not in data:
        return jsonify({"msg": "Nenhum conteúdo enviado"}), 400

    # verifica projeto
    project = find_project_by_id(project_id)
    if not project:
        return jsonify({"msg": "Projeto não encontrado"}), 404

    # verifica permissão
    if str(project["user_id"]) != str(current_user_id):
        return jsonify({"msg": "voce nao tem permissao para acessar esse projeto"}), 403

    # verifica lista
    lista = find_list_by_id(list_id)
    if not lista or str(lista["project_id"]) != str(project_id):
        return jsonify({"msg": "Lista não encontrada no projeto"}), 404

    # verifica task
    task = find_task_by_id(task_id)
    if not task or str(task["list_id"]) != str(list_id):
        return jsonify({"msg": "Task não encontrada na lista"}), 404

    new_comment_id = get_next_comment_id()

    new_comment = {
        "comment_id": str(new_comment_id),
        "task_id": str(task_id),
        "content": data["content"],
        "created_on": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    save_comment(new_comment)
    return jsonify({"msg": "Comentário criado com sucesso!", "comment": new_comment}), 201



# ============================================================
# LIST COMMENTS
# ============================================================
@comments_route.get("/projects/<project_id>/lists/<list_id>/tasks/<task_id>/comments")
@jwt_required()
def list_comments(project_id, list_id, task_id):

    current_user_id = get_jwt_identity()

    # verifica projeto
    project = find_project_by_id(project_id)
    if not project or str(project["user_id"]) != str(current_user_id):
        return jsonify({"error": "Projeto não encontrado ou não permitido"}), 403

    # verifica lista
    lista = find_list_by_id(list_id)
    if not lista or str(lista["project_id"]) != str(project_id):
        return jsonify({"error": "Lista não encontrada"}), 404

    # verifica task
    task = find_task_by_id(task_id)
    if not task or str(task["list_id"]) != str(list_id):
        return jsonify({"error": "Task não encontrada"}), 404

    comments = find_comments_by_task_id(task_id)

    return jsonify({"comments": comments}), 200



# ============================================================
# UPDATE COMMENT
# ============================================================
@comments_route.put("/projects/<project_id>/lists/<list_id>/tasks/<task_id>/comments/<comment_id>")
@jwt_required()
def update_comment(project_id, list_id, task_id, comment_id):

    current_user_id = get_jwt_identity()
    data = request.get_json()

    if not data or "content" not in data:
        return jsonify({"msg": "Nenhum conteúdo enviado"}), 400

    # verifica projeto
    project = find_project_by_id(project_id)
    if not project or str(project["user_id"]) != str(current_user_id):
        return jsonify({"msg": "Sem permissão"}), 403

    # verifica lista
    lista = find_list_by_id(list_id)
    if not lista or str(lista["project_id"]) != str(project_id):
        return jsonify({"msg": "Lista inválida"}), 400

    # verifica task
    task = find_task_by_id(task_id)
    if not task or str(task["list_id"]) != str(list_id):
        return jsonify({"msg": "Task inválida"}), 400

    updated = update_comment_data(comment_id, data["content"])
    if not updated:
        return jsonify({"msg": "Comentário não encontrado"}), 404

    return jsonify({"msg": "Comentário atualizado com sucesso!"}), 200



# ============================================================
# DELETE COMMENT
# ============================================================
@comments_route.delete("/projects/<project_id>/lists/<list_id>/tasks/<task_id>/comments/<comment_id>")
@jwt_required()
def delete_comment(project_id, list_id, task_id, comment_id):

    current_user_id = get_jwt_identity()

    # verifica projeto
    project = find_project_by_id(project_id)
    if not project or str(project["user_id"]) != str(current_user_id):
        return jsonify({"msg": "Sem permissão"}), 403

    # verifica lista
    lista = find_list_by_id(list_id)
    if not lista or str(lista["project_id"]) != str(project_id):
        return jsonify({"msg": "Lista inválida"}), 400

    # verifica task
    task = find_task_by_id(task_id)
    if not task or str(task["list_id"]) != str(list_id):
        return jsonify({"msg": "Task inválida"}), 400

    deleted = delete_comment_data(comment_id)
    if not deleted:
        return jsonify({"msg": "Comentário não encontrado"}), 404

    return jsonify({"msg": "Comentário deletado com sucesso!"}), 200
