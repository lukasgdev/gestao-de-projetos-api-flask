from flask import Blueprint, jsonify,request
from services.csv_service import save_user, find_user_by_email, get_next_user_id, find_user_by_id, update_user_data, delete_user_data
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from datetime import datetime

user_route = Blueprint('users', __name__)

@user_route.route('/register', methods=['POST'])
def create_user():
    """
    Registra um novo usuário.
    ---
    tags:
      - Users
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            email:
              type: string
              example: usuario@email.com
            senha:
              type: string
              example: "123456"
            nome:
              type: string
              example: João Silva
    responses:
      201:
        description: Usuário cadastrado com sucesso
      400:
        description: Dados inválidos ou email já cadastrado
    """
    data = request.json
    email = data.get('email', '')
    password = data.get('senha', '')
    name = data.get('nome', '')

    if not email or not name or not password:
        return jsonify({"msg": 'Email, senha e nome são obrigatorios'}), 400
    
    if find_user_by_email(email):
        return jsonify({"msg": 'Email ja cadastrado'}), 400
    
    password_hash = generate_password_hash(password)
    new_id = get_next_user_id()

    new_user = {
        "user_id": new_id,
        "name": name,
        "password_hash": password_hash,
        "email": email,
        "created_on": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    save_user(new_user)

    return jsonify(msg="Usuário cadastrado com sucesso!"), 201


@user_route.route('/login', methods=['POST'])
def login():
    """
    Realiza login e retorna tokens JWT.
    ---
    tags:
      - Users
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            email:
              type: string
            senha:
              type: string
          example:
            email: usuario@email.com
            senha: "123456"
    responses:
      200:
        description: Login bem-sucedido, tokens retornados
      400:
        description: Dados incompletos
      401:
        description: Credenciais inválidas
    """
    data = request.json
    email = data.get('email', '')
    password = data.get('senha', '')

    if not email or not password:
        return jsonify({"msg": 'Email e senha são obrigatorios'}), 400
    
    user = find_user_by_email(email)

    if not user:
        return jsonify({"msg": 'Email ou senha inválidos'}), 401
    
    password_hash = user.get('password_hash')
    if check_password_hash(password_hash, password):
        user_id = user.get('user_id')

        access_token = create_access_token(identity=user_id)
        refresh_token = create_refresh_token(identity=user_id)

        return jsonify(access_token=access_token, refresh_token=refresh_token), 200
    
    else:
        return jsonify({"msg": "Email ou senha inválidos"}), 401
    

@user_route.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh_token():
    """
    Gera um novo access token utilizando o refresh token.
    ---
    tags:
      - Users
    security:
      - Bearer: []
    responses:
      200:
        description: Novo access token gerado
      404:
        description: Usuário não encontrado
    """
    current_user_id = get_jwt_identity()
    
    user = find_user_by_id(current_user_id)

    if not user:
        return jsonify({"msg": "Usuário não encontrado"}), 404
    
    new_acess_token= create_access_token(identity=current_user_id)

    return jsonify(access_token=new_acess_token), 200


@user_route.route('/user')
@jwt_required()
def user_info():
    """
    Retorna as informações do usuário autenticado.
    ---
    tags:
      - Users
    security:
      - Bearer: []
    responses:
      200:
        description: Informações do usuário
      404:
        description: Usuário não encontrado
    """
    current_user_id = get_jwt_identity()

    user = find_user_by_id(current_user_id)

    if not user:
        return jsonify({"msg": "Usuário não encontrado"}), 404
    
    return jsonify({
        "id": user.get("user_id"),
        "nome": user.get("name"),
        "email": user.get("email"),
        "criado_em": user.get('created_on')
    }), 200


@user_route.route('/user', methods=['PUT'])
@jwt_required()
def update_user():
    """
    Atualiza os dados do usuário autenticado.
    ---
    tags:
      - Users
    security:
      - Bearer: []
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        schema:
          type: object
          properties:
            nome:
              type: string
            email:
              type: string
            senha:
              type: string
    responses:
      200:
        description: Dados atualizados com sucesso
      400:
        description: Nenhum dado enviado
    """
    current_user_id = get_jwt_identity()
    data = request.json

    new_name = data.get('nome', '')
    new_email = data.get('email', '')
    new_password = data.get('senha', '')

    if new_name or new_email or new_password:
        if new_password:
            new_password_hash = generate_password_hash(new_password)
            data.pop('senha')
            data['password_hash'] = new_password_hash
        
        if new_name:
            data.pop('nome')
            data['name'] = new_name

        update_user_data(current_user_id, data)

        return jsonify(msg='Cadastro atualizado com sucesso'), 200


    return jsonify(msg='Informe o que deseja atualizar corretamente'), 400


@user_route.route('/user', methods=['DELETE'])
@jwt_required()
def delete_user():
    """
    Deleta o usuário autenticado.
    ---
    tags:
      - Users
    security:
      - Bearer: []
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        schema:
          type: object
          properties:
            senha:
              type: string
              example: "123456"
          required:
            - senha
    responses:
      200:
        description: Usuário deletado
      400:
        description: Senha não informada
      401:
        description: Senha inválida
      404:
        description: Usuário não encontrado
    """
    current_user_id = get_jwt_identity()

    password = request.json.get('senha', '')

    if not password:
        return jsonify(msg='informe a senha de usuario'), 400
    
    user = find_user_by_id(current_user_id)

    if not user:
        return jsonify(msg='usuário não encontrado'), 404
    
    password_hash = user.get('password_hash')
    if check_password_hash(password_hash, password):
        delete_user_data(current_user_id)
        return jsonify(msg='Usuario deletado'), 200

    return jsonify(msg='Senha inválida'), 401
