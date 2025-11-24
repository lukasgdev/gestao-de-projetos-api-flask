from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from services.csv_service import (
    find_project_by_id,
    find_list_by_id,
    find_task_by_id,
    find_comments_by_task_id,
    get_next_comment_id,
    save_comment,
    update_comment_data,
    delete_comment_data,
    find_comment_by_id,
    find_user_by_id
)

comments_route = Blueprint("comments", __name__)


# ============================================================
# CREATE COMMENT
# ============================================================
@comments_route.route("/", methods=["POST"])
@jwt_required()
def create_comment(project_id, list_id, task_id):
    """
    Criar um novo comentario
    ---
    tags:
      - Comments
    operationId: "create_comment"
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
            content:
              type: string
    responses:
      201:
        description: comentario criado com sucesso
        examples:
          application/json:
            message: "Comentário criado com sucesso!"
            comment:
              comment_id: "<id>"
              task_id: "<task_id>"
              content: "<conteúdo>"
              created_at: "2025-11-23 12:00:00"
      400:
        description: sem conteudo
        examples:
          application/json:
            error: "Nenhum conteúdo enviado"
      404:
        description: projeto,lista ou task não encontrada
        examples:
          application/json:
            error: "Projeto não encontrado"
      403:
        description: sem permissão
        examples:
          application/json:
            error: "Você não tem permissão para acessar esse projeto"
    """
    current_user_id = get_jwt_identity()
    data = request.get_json()

    if not data or "content" not in data:
      return jsonify({"error": "Nenhum conteúdo enviado"}), 400

    # verifica projeto
    project = find_project_by_id(project_id)
    if not project:
      return jsonify({"error": "Projeto não encontrado"}), 404

    # verifica permissão
    if str(project["user_id"]) != str(current_user_id):
      return jsonify({"error": "voce nao tem permissao para acessar esse projeto"}), 403

    # verifica lista
    lista = find_list_by_id(list_id)
    if not lista or str(lista["project_id"]) != str(project_id):
      return jsonify({"error": "Lista não encontrada no projeto"}), 404

    # verifica task
    task = find_task_by_id(task_id)
    if not task or str(task["list_id"]) != str(list_id):
      return jsonify({"error": "Task não encontrada na lista"}), 404

    new_comment_id = get_next_comment_id()

    new_comment = {
        "comment_id": str(new_comment_id),
        "task_id": str(task_id),
        "content": data["content"],
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    save_comment(new_comment)
    return jsonify({"message": "Comentário criado com sucesso!", "data": new_comment}), 201



# ============================================================
# LIST COMMENTS
# ============================================================
@comments_route.route("/", methods=["GET"])
@jwt_required()
def list_comments(project_id, list_id, task_id):
    """
    Listar todas os comentarios de uma task
    ---
    tags:
      - Comments
    operationId: "list_comments"
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
        description: Lista de comentarios retornada
        examples:
          application/json:
            message: "Comentários recuperados com sucesso"
            data:
              task_info:
                task_id: "<task_id>"
                title: "<titulo>"
                description: "<descricao>"
              comments:
                - comment_id: "1"
                  content: "Comentário A"
                  created_at: "2025-11-23 11:00:00"
                - comment_id: "2"
                  content: "Comentário B"
                  created_at: "2025-11-23 11:05:00"
      403:
        description: Sem permissão
        examples:
          application/json:
            error: "Você não tem permissão para ver os comentários deste projeto"
      404:
        description: comentario não encontrado
        examples:
          application/json:
            error: "Task não encontrada"
    """
    current_user_id = get_jwt_identity()

    # verifica projeto
    project = find_project_by_id(project_id)
    if not project:
      return jsonify({"error": "Projeto não encontrado"}), 404
    
    if str(project["user_id"]) != str(current_user_id):
      return jsonify({"error": "Você não tem permissão para ver os comentários deste projeto"}), 403

    # verifica lista
    list = find_list_by_id(list_id)
    if not list or str(list["project_id"]) != str(project_id):
      return jsonify({"error": "Lista não encontrada"}), 404

    # verifica task
    task = find_task_by_id(task_id)
    if not task or str(task["list_id"]) != str(list_id):
      return jsonify({"error": "Task não encontrada"}), 404

    comments = find_comments_by_task_id(task_id)

    if not comments:
      return jsonify({
        "message": "Nenhum comentário encontrado para esta task.",
      }), 200

    response = {
        "task_info": {
            "task_id": task_id,
            "title": task.get('title'),
            "description": task.get('description'),
        },
        "comments": comments or [],
    }

    return jsonify({
      "message": "Comentários recuperados com sucesso",
      "data": response
    }), 200

@comments_route.route('/<comment_id>', methods=["GET"])
@jwt_required()
def get_specific_comment(project_id, list_id, task_id, comment_id):
    """
    Obter um comentário específico de uma task.
    ---
    tags:
      - Comments
    operationId: "get_specific_comment"
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
      - in: path
        name: comment_id
        required: true
        type: string
    responses:
      200:
        description: Comentário retornado
        examples:
          application/json:
            message: "Comentário recuperado com sucesso"
            data:
              project_info:
                project_id: "<project_id>"
              list_info:
                list_id: "<list_id>"
              task_info:
                task_id: "<task_id>"
              comment:
                comment_id: "<comment_id>"
                content: "<conteúdo>"
                created_at: "2025-11-23 12:00:00"
      401:
        description: Usuário não encontrado (token inválido/usuário removido)
        examples:
          application/json:
            error: "Usuário não encontrado. Por favor, faça login novamente."
      400:
        description: Alguma entidade não pertence ao nível correto
        examples:
          application/json:
            error: "Esta lista não pertence ao projeto informado"
      403:
        description: Sem permissão
        examples:
          application/json:
            error: "Você não tem permissão para visualizar este projeto"
      404:
        description: Projeto, lista, task ou comentário não encontrado
        examples:
          application/json:
            error: "Comentário não encontrado"
    """

    current_user_id = get_jwt_identity()
    user = find_user_by_id(current_user_id)

    # Verifica usuário
    if not user:
        return jsonify({"error": "Usuário não encontrado. Por favor, faça login novamente."}), 401

    # Verifica projeto
    project = find_project_by_id(project_id)
    if not project:
        return jsonify({"error": "Projeto não encontrado"}), 404

    # Verifica dono do projeto
    if str(project["user_id"]) != str(current_user_id):
        return jsonify({"error": "Você não tem permissão para visualizar este projeto"}), 403

    # Verifica lista
    lista = find_list_by_id(list_id)
    if not lista:
        return jsonify({"error": "Lista não encontrada"}), 404

    if lista.get("project_id") != str(project_id):
        return jsonify({"error": "Esta lista não pertence ao projeto informado"}), 400

    # Verifica task
    task = find_task_by_id(task_id)
    if not task:
        return jsonify({"error": "Task não encontrada"}), 404

    if task.get("list_id") != str(list_id):
        return jsonify({"error": "Esta task não pertence à lista informada"}), 400

    # Verifica comment
    comment = find_comment_by_id(comment_id)
    if not comment:
        return jsonify({"error": "Comentário não encontrado"}), 404

    if comment.get("task_id") != str(task_id):
        return jsonify({"error": "Este comentário não pertence à task informada"}), 400

    # Resposta final
    response = {
        "project_info": {
            "project_id": project_id,
            "project_title": project.get("project_title"),
            "project_description": project.get("project_description"),
        },
        "list_info": lista,
        "task_info": task,
        "comment": comment,
    }

    return jsonify({
        "message": "Comentário recuperado com sucesso",
        "data": response
    }), 200


# ============================================================
# UPDATE COMMENT
# ============================================================
@comments_route.route("/<comment_id>", methods=["PUT"])
@jwt_required()
def update_comment(project_id, list_id, task_id, comment_id):
    """
    Atualizar um comentario
    ---
    tags:
      - Comments
    operationId: "update_comment"
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
      - in: path
        name: comment_id
        required: true
        type: string
      - in: body
        name: body
        schema:
          type: object
          properties:
            content:
              type: string
    responses:
      200:
        description: comentario atualizado
        examples:
          application/json:
            message: "Comentário atualizado com sucesso!"
      400:
        description: Dados inválidos
        examples:
          application/json:
            error: "Nenhum conteúdo enviado"
      404:
        description: comentario não encontrado
        examples:
          application/json:
            error: "Comentário não encontrado"
    """
    current_user_id = get_jwt_identity()
    data = request.get_json()

    if not data or "content" not in data:
      return jsonify({"error": "Nenhum conteúdo enviado"}), 400

    # verifica projeto
    project = find_project_by_id(project_id)
    if not project:
      return jsonify({"error": "Projeto não encontrado"}), 404
    if str(project["user_id"]) != str(current_user_id):
      return jsonify({"error": "Sem permissão"}), 403

    # verifica lista
    lista = find_list_by_id(list_id)
    if not lista or str(lista["project_id"]) != str(project_id):
      return jsonify({"error": "Lista inválida"}), 400

    # verifica task
    task = find_task_by_id(task_id)
    if not task or str(task["list_id"]) != str(list_id):
      return jsonify({"error": "Task inválida"}), 400

    updated = update_comment_data(comment_id, data["content"])
    if not updated:
      return jsonify({"error": "Comentário não encontrado"}), 404

    return jsonify({"message": "Comentário atualizado com sucesso!"}), 200



# ============================================================
# DELETE COMMENT
# ============================================================
@comments_route.route("/<comment_id>", methods=["DELETE"])
@jwt_required()
def delete_comment(project_id, list_id, task_id, comment_id):
    """
    Deletar um comentario
    ---
    tags:
      - Comments
    operationId: "delete_comment"
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
      - in: path
        name: comment_id
        required: true
        type: string
    responses:
      200:
        description: comentario deletado
        examples:
          application/json:
            message: "Comentário deletado com sucesso!"
      404:
        description: comentario não encontrado
        examples:
          application/json:
            error: "Comentário não encontrado"
    """
    current_user_id = get_jwt_identity()

    # verifica projeto
    project = find_project_by_id(project_id)
    if not project:
      return jsonify({"error": "Projeto não encontrado"}), 404
    if str(project["user_id"]) != str(current_user_id):
      return jsonify({"error": "Sem permissão"}), 403

    # verifica lista
    lista = find_list_by_id(list_id)
    if not lista or str(lista["project_id"]) != str(project_id):
      return jsonify({"error": "Lista inválida"}), 400

    # verifica task
    task = find_task_by_id(task_id)
    if not task or str(task["list_id"]) != str(list_id):
      return jsonify({"error": "Task inválida"}), 400

    delete_comment_data(comment_id)

    return jsonify({"message": "Comentário deletado com sucesso!"}), 200
